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
import httpx
from datetime import datetime, timezone
import asyncio
from ai_engine.rag.vector_store import get_vector_store

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
        
        async def ping_vector_store():
            start = time.perf_counter()
            try:
                # Use loop.run_in_executor since store.retrieve is blocking
                loop = asyncio.get_running_loop()
                store = get_vector_store()
                if store._collection is not None:
                    await loop.run_in_executor(None, store.retrieve, "health check ping", 1)
                    elapsed = (time.perf_counter() - start) * 1000
                    return "healthy", round(elapsed, 2)
                return "unhealthy", 0.0
            except Exception:
                return "unhealthy", round((time.perf_counter() - start) * 1000, 2)
                
        async def ping_llm_provider():
            start = time.perf_counter()
            try:
                async with httpx.AsyncClient() as client:
                    headers = {"Authorization": f"Bearer {settings.ai.openai_api_key}"}
                    resp = await client.get("https://api.openai.com/v1/models", headers=headers, timeout=settings.ai.health_timeout_seconds)
                    elapsed = (time.perf_counter() - start) * 1000
                    return "healthy" if resp.status_code == 200 else "degraded", round(elapsed, 2)
            except Exception:
                return "unhealthy", round((time.perf_counter() - start) * 1000, 2)

        # Run DB checks sequentially to avoid SQLAlchemy concurrent session errors
        ping_result = await self._repository.ping_db()
        queue_result = await self._repository.check_review_queue()
        
        # Run external IO checks concurrently
        vs_future = ping_vector_store()
        llm_future = ping_llm_provider()
        
        (vs_status, vs_latency), (llm_status, llm_latency) = await asyncio.gather(
            vs_future, llm_future
        )
        
        db_status = str(ping_result.get("status", "unknown"))
        queue_status = str(queue_result.get("status", "unknown"))
        queue_latency = float(queue_result.get("latency_ms", 0.0))
        
        # Overall status is degraded if any component is unhealthy
        overall_status = "healthy"
        if "unhealthy" in [db_status, queue_status, vs_status, llm_status] or "disconnected" in [db_status]:
            overall_status = "degraded"
            
        return HealthResponse(
            status=overall_status,
            version=settings.APP_VERSION,
            timestamp=datetime.now(timezone.utc),
            uptime_seconds=time.monotonic() - _START_TIME,
            db_status=db_status,
            vector_store_status=vs_status,
            vector_store_latency_ms=vs_latency,
            ai_services_status=llm_status,
            ai_services_latency_ms=llm_latency,
            review_queue_status=queue_status,
            review_queue_latency_ms=queue_latency
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
