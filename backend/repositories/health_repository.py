"""
Health repository for database connectivity verification.

This repository does NOT write any data. Health probes are read-only
diagnostic operations — writing health check results to the application
database was rejected during architectural review (YAGNI, creates
3000-9000 useless rows/day from Kubernetes probes).
"""
import logging
import time

from sqlalchemy import text, select, func
from sqlalchemy.ext.asyncio import AsyncSession
from models.review import ReviewTask, ReviewStatus

from core.constants import HEALTH_DB_PING_QUERY

logger = logging.getLogger(__name__)


class HealthRepository:
    """Read-only repository for database health verification.

    Executes a lightweight `SELECT 1` query to verify database
    connectivity and measure round-trip latency.
    """

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def ping_db(self) -> dict[str, float | str]:
        """Execute a lightweight query to verify DB connectivity.

        Returns:
            A dict containing:
                - status: 'connected' or 'disconnected'
                - latency_ms: round-trip time in milliseconds
        """
        start = time.perf_counter()
        try:
            result = await self._session.execute(text(HEALTH_DB_PING_QUERY))
            value = result.scalar_one()
            elapsed_ms = (time.perf_counter() - start) * 1000

            if value != 1:
                logger.warning("DB ping returned unexpected value: %s", value)
                return {"status": "unhealthy", "latency_ms": elapsed_ms}

            logger.debug("DB ping successful in %.2fms", elapsed_ms)
            return {"status": "connected", "latency_ms": round(elapsed_ms, 2)}

        except Exception as exc:
            elapsed_ms = (time.perf_counter() - start) * 1000
            logger.error("DB ping failed after %.2fms: %s", elapsed_ms, exc)
            return {"status": "disconnected", "latency_ms": round(elapsed_ms, 2)}

    async def check_review_queue(self) -> dict[str, float | str]:
        """Check review queue status and latency."""
        start = time.perf_counter()
        try:
            result = await self._session.execute(
                select(func.count()).select_from(ReviewTask).where(ReviewTask.status == ReviewStatus.NEW)
            )
            count = result.scalar()
            elapsed_ms = (time.perf_counter() - start) * 1000
            
            # If queue has too many tasks, could be degraded, but for now just healthy
            status = "healthy" if count is not None else "unhealthy"
            return {"status": status, "latency_ms": round(elapsed_ms, 2)}
        except Exception as exc:
            elapsed_ms = (time.perf_counter() - start) * 1000
            logger.error("Review queue check failed: %s", exc)
            return {"status": "unhealthy", "latency_ms": round(elapsed_ms, 2)}
