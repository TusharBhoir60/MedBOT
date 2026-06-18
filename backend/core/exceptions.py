"""
Domain exception hierarchy for AarogyaAgent v2.

All application-level exceptions inherit from AarogyaBaseException.
Each exception carries structured fields for consistent error reporting
across API responses, logs, and agent traces.
"""
from datetime import datetime, timezone
from typing import Any


class AarogyaBaseException(Exception):
    """Base exception for all AarogyaAgent domain errors."""

    def __init__(
        self,
        message: str,
        error_code: str = "AAROGYA_ERROR",
        details: dict[str, Any] | None = None,
    ) -> None:
        super().__init__(message)
        self.message = message
        self.error_code = error_code
        self.details = details or {}
        self.timestamp = datetime.now(timezone.utc).isoformat()


class DatabaseException(AarogyaBaseException):
    """Raised when a database operation fails (connection, query, transaction)."""

    def __init__(
        self,
        message: str = "A database error occurred",
        details: dict[str, Any] | None = None,
    ) -> None:
        super().__init__(
            message=message,
            error_code="DATABASE_ERROR",
            details=details,
        )


class ServiceException(AarogyaBaseException):
    """Raised when business logic validation or processing fails."""

    def __init__(
        self,
        message: str = "A service error occurred",
        details: dict[str, Any] | None = None,
    ) -> None:
        super().__init__(
            message=message,
            error_code="SERVICE_ERROR",
            details=details,
        )


class NotFoundException(AarogyaBaseException):
    """Raised when a requested entity does not exist."""

    def __init__(
        self,
        message: str = "Resource not found",
        details: dict[str, Any] | None = None,
    ) -> None:
        super().__init__(
            message=message,
            error_code="NOT_FOUND",
            details=details,
        )


class ValidationException(AarogyaBaseException):
    """Raised when input data fails domain validation rules."""

    def __init__(
        self,
        message: str = "Validation error",
        details: dict[str, Any] | None = None,
    ) -> None:
        super().__init__(
            message=message,
            error_code="VALIDATION_ERROR",
            details=details,
        )
