"""
Health service — business logic for liveness and readiness probes.

Standalone service class (no base class inheritance) per the architectural
decision that BaseService was YAGNI — fewer than 3 services shared common
behaviour, so a base class adds unnecessary abstraction overhead.

This service is responsible for:
  - Reporting application liveness (process running, version info)
  - Reporting database readiness (connectivity + latency)
"""
import logging
import time
from datetime import datetime, timezone

from core.config import settings
from core.exceptions import DatabaseException
from repositories.health_repository import HealthRepository
from schemas.health import (
    HealthDBResponse,
    HealthLiveResponse,
    HealthReadyResponse,
    HealthResponse,
)

logger = logging.getLogger(__name__)

# Captured at import time; used to calculate uptime_seconds
_START_TIME: float = time.monotonic()


class HealthService:
    """Handles health check business logic for liveness, readiness, and custom probes.

    Args:
        repository: The health repository used for DB connectivity checks.
    """

    def __init__(self, repository: HealthRepository) -> None:
        self._repository = repository

    async def get_liveness(self) -> HealthLiveResponse:
        """Return application liveness status.

        Does NOT check external dependencies. If this endpoint fails,
        the container should be restarted (Kubernetes liveness probe).
        """
        logger.debug("Liveness probe requested")
        return HealthLiveResponse(
            status="healthy",
            version=settings.APP_VERSION,
            timestamp=datetime.now(timezone.utc),
        )

    async def get_readiness(self) -> HealthReadyResponse:
        """Return application readiness status including database connectivity.

        Checks whether the service can serve traffic by verifying the
        database connection. If the DB is unreachable, the pod should
        be removed from load balancer rotation (Kubernetes readiness probe).

        Raises:
            DatabaseException: If the database connectivity check fails
                with an unexpected error (non-connectivity failure).
        """
        logger.debug("Readiness probe requested")
        ping_result = await self._repository.ping_db()

        db_status = str(ping_result.get("status", "unknown"))
        db_latency_ms = float(ping_result.get("latency_ms", 0.0))

        overall_status = "healthy" if db_status == "connected" else "degraded"

        if db_status != "connected":
            logger.warning(
                "Readiness probe: database not connected",
                extra={"db_status": db_status, "db_latency_ms": db_latency_ms},
            )

        return HealthReadyResponse(
            status=overall_status,
            version=settings.APP_VERSION,
            timestamp=datetime.now(timezone.utc),
            db_status=db_status,
            db_latency_ms=db_latency_ms,
        )

    async def get_overall_health(self) -> HealthResponse:
        """Return overall application health status.

        Checks the process and basic database connectivity.
        """
        logger.debug("Overall health check requested")
        ping_result = await self._repository.ping_db()
        db_status = str(ping_result.get("status", "unknown"))
        overall_status = "healthy" if db_status == "connected" else "degraded"
        return HealthResponse(
            status=overall_status,
            version=settings.APP_VERSION,
            timestamp=datetime.now(timezone.utc),
        )

    async def get_db_health(self) -> HealthDBResponse:
        """Return database health status specifically.

        Confirms database connectivity and reports connection status and latency.
        """
        logger.debug("DB health check requested")
        ping_result = await self._repository.ping_db()
        db_status = str(ping_result.get("status", "unknown"))
        db_latency_ms = float(ping_result.get("latency_ms", 0.0))
        overall_status = "healthy" if db_status == "connected" else "degraded"
        return HealthDBResponse(
            status=overall_status,
            version=settings.APP_VERSION,
            timestamp=datetime.now(timezone.utc),
            db_status=db_status,
            db_latency_ms=db_latency_ms,
        )
