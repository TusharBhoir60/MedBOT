"""
Health check response schemas.

These schemas define the JSON contract for the /health/live
and /health/ready endpoints.
"""
from datetime import datetime

from schemas.base_schema import BaseSchema


class HealthLiveResponse(BaseSchema):
    """Response schema for GET /api/v1/health/live.

    A lightweight liveness probe — confirms the process is running.
    No external dependency checks.
    """

    status: str
    version: str
    timestamp: datetime


class HealthReadyResponse(BaseSchema):
    """Response schema for GET /api/v1/health/ready.

    A readiness probe — confirms the application can serve traffic
    by verifying database connectivity and reporting pool status.
    """

    status: str
    version: str
    timestamp: datetime
    db_status: str
    db_latency_ms: float


class HealthResponse(BaseSchema):
    """Response schema for GET /api/v1/health.

    A general overall health check — confirms the application process is running
    and details any checked dependencies.
    """

    status: str
    version: str
    timestamp: datetime


class HealthDBResponse(BaseSchema):
    """Response schema for GET /api/v1/health/db.

    Database-specific health check — confirms database connectivity and latency.
    """

    status: str
    version: str
    timestamp: datetime
    db_status: str
    db_latency_ms: float


class ErrorResponse(BaseSchema):
    """Standard error response schema returned by the global exception handler.

    Every error response includes a correlation_id so that the error
    can be traced through logs, agent traces, and DB queries.
    """

    error_code: str
    message: str
    correlation_id: str
    timestamp: datetime
