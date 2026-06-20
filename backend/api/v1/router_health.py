"""
Health probe endpoints for AarogyaAgent v2.

Two probe types following the Kubernetes cloud-native standard:

  GET /api/v1/health/live
    Liveness probe — is the process alive?
    Fast, no external dependencies. Restart the pod if this fails.

  GET /api/v1/health/ready
    Readiness probe — can the service accept traffic?
    Checks database connectivity. Remove from load balancer if this fails.

Both probes return a 200 on success. The readiness probe returns 503
when the database is unreachable, signalling the orchestrator to stop
routing traffic to this instance.
"""
import logging

from fastapi import APIRouter, status

from api.dependencies import HealthServiceDep
from schemas.health import (
    HealthDBResponse,
    HealthLiveResponse,
    HealthReadyResponse,
    HealthResponse,
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/health", tags=["health"])


@router.get(
    "",
    response_model=HealthResponse,
    status_code=status.HTTP_200_OK,
    summary="Overall health check",
    description=(
        "Confirms the application process is running and checks overall dependencies."
    ),
    responses={
        status.HTTP_503_SERVICE_UNAVAILABLE: {
            "description": "Service unhealthy or degraded",
        }
    },
)
async def health_overall(service: HealthServiceDep) -> HealthResponse:
    """Return overall health status including database check."""
    logger.debug("GET /health")
    result = await service.get_overall_health()

    if result.status == "degraded":
        from fastapi.responses import JSONResponse
        return JSONResponse(  # type: ignore[return-value]
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            content=result.model_dump(mode="json", by_alias=True),
        )

    return result


@router.get(
    "/live",
    response_model=HealthLiveResponse,
    status_code=status.HTTP_200_OK,
    summary="Liveness probe",
    description=(
        "Confirms the application process is running. "
        "No external dependency checks. "
        "Kubernetes restarts the pod if this returns non-2xx."
    ),
)
async def health_live(service: HealthServiceDep) -> HealthLiveResponse:
    """Return liveness status without checking external dependencies."""
    logger.debug("GET /health/live")
    return await service.get_liveness()


@router.get(
    "/ready",
    response_model=HealthReadyResponse,
    status_code=status.HTTP_200_OK,
    summary="Readiness probe",
    description=(
        "Confirms the application can serve traffic by checking database connectivity. "
        "Kubernetes removes the pod from load balancer rotation if this returns non-2xx."
    ),
    responses={
        status.HTTP_503_SERVICE_UNAVAILABLE: {
            "description": "Service not ready — database unreachable",
        }
    },
)
async def health_ready(service: HealthServiceDep) -> HealthReadyResponse:
    """Return readiness status including database connectivity check."""
    logger.debug("GET /health/ready")
    result = await service.get_readiness()

    # HTTP 503 when degraded so load balancers stop routing traffic here
    if result.status == "degraded":
        from fastapi.responses import JSONResponse
        return JSONResponse(  # type: ignore[return-value]
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            content=result.model_dump(mode="json", by_alias=True),
        )

    return result


@router.get(
    "/db",
    response_model=HealthDBResponse,
    status_code=status.HTTP_200_OK,
    summary="Database health check",
    description=(
        "Confirms database connectivity and reports connection latency."
    ),
    responses={
        status.HTTP_503_SERVICE_UNAVAILABLE: {
            "description": "Database unreachable or degraded",
        }
    },
)
async def health_db(service: HealthServiceDep) -> HealthDBResponse:
    """Return database health status specifically."""
    logger.debug("GET /health/db")
    result = await service.get_db_health()

    if result.status == "degraded":
        from fastapi.responses import JSONResponse
        return JSONResponse(  # type: ignore[return-value]
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            content=result.model_dump(mode="json", by_alias=True),
        )

    return result
