"""
AarogyaAgent v2 — FastAPI application factory.

Architecture decisions in this file:
  - Lifespan context manager handles startup/shutdown cleanly
  - Middleware is mounted in reverse order (last added = outermost)
  - TrustedHostMiddleware uses settings.security.allowed_hosts
  - CORSMiddleware uses settings.security.allowed_origins
  - All domain exceptions are mapped to structured JSON responses
  - Docs are disabled in production (APP_ENV == "production")
"""
import logging
from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware

from api.middleware import (
    CorrelationIdMiddleware,
    RequestSizeLimiterMiddleware,
    RequestTimingMiddleware,
    SecurityHeadersMiddleware,
    RateLimiterMiddleware,
    aarogya_exception_handler,
    unhandled_exception_handler,
)
from api.v1.router_health import router as health_router
from api.v1.router_chat import router as chat_router
from api.v1.router_review import router as review_router
from core.config import settings
from core.constants import API_V1_STR
from core.exceptions import AarogyaBaseException
from core.logging_config import setup_logging
from database.engine import close_db, init_db

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Manage application startup and shutdown lifecycle.

    Startup:
      1. Configure structured logging (must be first)
      2. Initialize the database engine connection pool
      3. Log startup banner

    Shutdown:
      1. Dispose the database engine, releasing all pool connections
      2. Log shutdown confirmation
    """
    # --- Startup ---
    setup_logging(
        log_level=settings.log.level,
        format_type=settings.log.format_type,
    )
    logger.info(
        "Starting AarogyaAgent v%s in %s mode",
        settings.APP_VERSION,
        settings.APP_ENV,
    )

    await init_db()
    logger.info("Application startup complete")

    yield

    # --- Shutdown ---
    logger.info("Application shutting down")
    await close_db()
    logger.info("Application shutdown complete")


def create_application() -> FastAPI:
    """Construct and configure the FastAPI application instance.

    Returns:
        A fully configured FastAPI application ready to serve requests.
    """
    # Disable interactive docs in production — they expose the API schema
    docs_url = None if settings.APP_ENV == "production" else "/docs"
    redoc_url = None if settings.APP_ENV == "production" else "/redoc"
    openapi_url = None if settings.APP_ENV == "production" else "/openapi.json"

    application = FastAPI(
        title=settings.APP_TITLE,
        version=settings.APP_VERSION,
        description=(
            "AarogyaAgent v2 — Research-grade AI Healthcare Triage Platform "
            "implementing Confidence-Weighted Multi-Agent Reasoning (CMAR)."
        ),
        docs_url=docs_url,
        redoc_url=redoc_url,
        openapi_url=openapi_url,
        lifespan=lifespan,
    )

    # ------------------------------------------------------------------ #
    # Security: Trusted Host validation
    # Rejects requests with a Host header not in the allowed list.
    # Must be outermost to block host-header injection before any processing.
    # ------------------------------------------------------------------ #
    application.add_middleware(
        TrustedHostMiddleware,
        allowed_hosts=settings.security.allowed_hosts,
    )

    # ------------------------------------------------------------------ #
    # Security: CORS
    # Restricts cross-origin requests to configured origins.
    # Critical for Sprint 1+ parallel frontend-backend development.
    # ------------------------------------------------------------------ #
    application.add_middleware(
        CORSMiddleware,
        allow_origins=settings.security.allowed_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # ------------------------------------------------------------------ #
    # Custom ASGI middleware stack
    # FastAPI adds middleware in LIFO order — last added = outermost.
    # Desired request traversal order:
    #   RequestSizeLimiter → CorrelationId → RequestTiming → SecurityHeaders
    # So we add them in reverse:
    # ------------------------------------------------------------------ #
    application.add_middleware(SecurityHeadersMiddleware)
    application.add_middleware(
        RateLimiterMiddleware,
        default_limit=settings.security.rate_limit_default,
    )
    application.add_middleware(RequestTimingMiddleware)
    application.add_middleware(CorrelationIdMiddleware)
    application.add_middleware(
        RequestSizeLimiterMiddleware,
        max_size=settings.security.max_request_size,
    )

    # ------------------------------------------------------------------ #
    # Exception handlers
    # ------------------------------------------------------------------ #
    application.add_exception_handler(
        AarogyaBaseException,
        aarogya_exception_handler,  # type: ignore[arg-type]
    )
    application.add_exception_handler(
        Exception,
        unhandled_exception_handler,
    )

    # ------------------------------------------------------------------ #
    # Routers
    # ------------------------------------------------------------------ #
    application.include_router(health_router, prefix=API_V1_STR)
    application.include_router(chat_router, prefix=API_V1_STR)
    application.include_router(review_router, prefix=API_V1_STR)

    return application


app: FastAPI = create_application()
