"""
ASGI middleware stack for AarogyaAgent v2.

Middleware is layered in the order requests traverse them (outermost first):

  1. RequestSizeLimiterMiddleware  — rejects oversized payloads before any processing
  2. CorrelationIdMiddleware       — injects X-Request-ID into context and response headers
  3. RequestTimingMiddleware       — measures and logs request latency
  4. SecurityHeadersMiddleware     — injects security headers on every response
  5. GlobalExceptionHandlerMiddleware — converts domain exceptions to structured JSON

The global exception handler is registered separately via FastAPI's
exception_handler mechanism (not as ASGI middleware) so it has access
to FastAPI's response helpers. See main.py for registration.
"""
import logging
import time
import uuid
from datetime import datetime, timezone

from typing import Any, Callable
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.requests import Request
from starlette.responses import JSONResponse, Response
from starlette.types import ASGIApp

from core.config import settings
from core.context import set_correlation_id, get_correlation_id
from core.exceptions import (
    AarogyaBaseException,
    DatabaseException,
    NotFoundException,
    ValidationException,
)

logger = logging.getLogger(__name__)


class RequestSizeLimiterMiddleware(BaseHTTPMiddleware):
    """Rejects requests whose Content-Length exceeds MAX_REQUEST_SIZE.

    This prevents memory exhaustion from large payloads (e.g. during
    bulk medical document uploads) before the request body is buffered.
    Returns 413 Payload Too Large without reading the body.
    """

    def __init__(self, app: ASGIApp, max_size: int) -> None:
        super().__init__(app)
        self._max_size = max_size

    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        content_length = request.headers.get("content-length")
        if content_length and int(content_length) > self._max_size:
            logger.warning(
                "Request rejected: payload too large",
                extra={
                    "content_length": content_length,
                    "max_size": self._max_size,
                    "path": request.url.path,
                },
            )
            return JSONResponse(
                status_code=413,
                content={
                    "error_code": "PAYLOAD_TOO_LARGE",
                    "message": f"Request body exceeds maximum allowed size of {self._max_size} bytes",
                    "correlation_id": get_correlation_id(),
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                },
            )
        return await call_next(request)


class CorrelationIdMiddleware(BaseHTTPMiddleware):
    """Injects a unique correlation ID into every request context.

    Reads from the incoming X-Request-ID header if present,
    otherwise generates a new UUID4. The ID is:
      - Stored in a ContextVar accessible throughout the entire request chain
      - Injected into every log record via CorrelationIdFilter
      - Echoed back in the X-Request-ID response header
    """

    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        correlation_id = request.headers.get("x-request-id") or str(uuid.uuid4())
        set_correlation_id(correlation_id)

        response = await call_next(request)
        response.headers["X-Request-ID"] = correlation_id
        return response


class RequestTimingMiddleware(BaseHTTPMiddleware):
    """Measures and logs the wall-clock duration of every request.

    Logs method, path, status code, and duration in milliseconds.
    This data feeds SLA monitoring and CMAR latency benchmarks.
    """

    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        start = time.perf_counter()
        response = await call_next(request)
        duration_ms = (time.perf_counter() - start) * 1000

        logger.info(
            "Request completed",
            extra={
                "method": request.method,
                "path": request.url.path,
                "status_code": response.status_code,
                "duration_ms": round(duration_ms, 2),
                "correlation_id": get_correlation_id(),
            },
        )
        response.headers["X-Response-Time-Ms"] = str(round(duration_ms, 2))
        return response


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """Injects security best-practice HTTP headers into every response.

    Headers applied:
      - X-Frame-Options: DENY                        (clickjacking protection)
      - X-Content-Type-Options: nosniff              (MIME sniffing protection)
      - X-XSS-Protection: 0                          (disable legacy XSS filter — modern browsers handle this)
      - Referrer-Policy: strict-origin-when-cross-origin
      - Strict-Transport-Security                    (HSTS, production only)

    HSTS is only applied when APP_ENV == "production" to avoid
    issues during local development with HTTP.
    """

    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        response = await call_next(request)

        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-XSS-Protection"] = "0"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"

        if settings.APP_ENV == "production":
            response.headers["Strict-Transport-Security"] = (
                "max-age=31536000; includeSubDomains; preload"
            )

        return response


def _make_error_response(
    status_code: int,
    error_code: str,
    message: str,
    details: dict[str, Any] | None = None,
) -> JSONResponse:
    """Build a structured JSON error response."""
    content: dict[str, Any] = {
        "error_code": error_code,
        "message": message,
        "correlation_id": get_correlation_id(),
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }
    if details:
        content["details"] = details
    return JSONResponse(status_code=status_code, content=content)


async def aarogya_exception_handler(
    request: Request, exc: AarogyaBaseException
) -> JSONResponse:
    """Map domain exceptions to structured HTTP error responses.

    Mapping:
      NotFoundException      → 404 Not Found
      ValidationException    → 422 Unprocessable Entity
      DatabaseException      → 503 Service Unavailable
      AarogyaBaseException   → 500 Internal Server Error (catch-all)

    Never leaks internal stack traces to the client.
    """
    if isinstance(exc, NotFoundException):
        status_code = 404
    elif isinstance(exc, ValidationException):
        status_code = 422
    elif isinstance(exc, DatabaseException):
        status_code = 503
    else:
        status_code = 500

    logger.error(
        "Domain exception: %s",
        exc.message,
        extra={
            "error_code": exc.error_code,
            "details": exc.details,
            "status_code": status_code,
        },
        exc_info=True,
    )

    return _make_error_response(
        status_code=status_code,
        error_code=exc.error_code,
        message=exc.message,
        details=exc.details or None,
    )


async def unhandled_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """Catch-all handler for unexpected exceptions.

    Ensures no raw stack trace is ever returned to the client.
    Logs at ERROR level with full traceback for operator investigation.
    """
    logger.critical(
        "Unhandled exception on %s %s",
        request.method,
        request.url.path,
        exc_info=True,
    )
    return _make_error_response(
        status_code=500,
        error_code="INTERNAL_SERVER_ERROR",
        message="An unexpected error occurred. Please try again later.",
    )

import asyncio
from collections import defaultdict

class RateLimiterMiddleware(BaseHTTPMiddleware):
    """
    Lightweight in-memory rate limiter based on sliding window.
    For production, this should be backed by Redis.
    Limits by IP address (request.client.host).
    """
    def __init__(self, app: ASGIApp, default_limit: int = 100) -> None:
        super().__init__(app)
        self.default_limit = default_limit
        self._requests: dict[str, list[float]] = defaultdict(list)
        self._lock = asyncio.Lock()

    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        client_ip = request.client.host if request.client else "unknown"
        now = time.time()
        
        async with self._lock:
            # Remove requests older than 60 seconds
            self._requests[client_ip] = [ts for ts in self._requests[client_ip] if now - ts < 60.0]
            
            if len(self._requests[client_ip]) >= self.default_limit:
                logger.warning(f"Rate limit exceeded for IP {client_ip}")
                return _make_error_response(
                    status_code=429,
                    error_code="TOO_MANY_REQUESTS",
                    message="Rate limit exceeded. Please try again later.",
                )
            self._requests[client_ip].append(now)
            
        return await call_next(request)
