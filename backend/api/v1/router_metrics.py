from typing import Optional
from datetime import datetime
from fastapi import APIRouter, Depends, Query, HTTPException

from api.dependencies import MetricsServiceDep, require_role
from schemas.metrics import (
    OverviewMetricsResponse,
    ConfidenceMetricsResponse,
    ReviewMetricsResponse,
    ClinicalMetricsResponse,
    ActivityFeedResponse,
    SystemHealthResponse
)

router = APIRouter(
    prefix="/metrics",
    tags=["metrics"],
    dependencies=[Depends(require_role("physician"))]
)

def validate_dates(start_date: Optional[datetime], end_date: Optional[datetime]):
    if start_date and end_date and start_date > end_date:
        raise HTTPException(status_code=400, detail="start_date cannot be greater than end_date")

@router.get("/overview", response_model=OverviewMetricsResponse)
async def get_overview(
    metrics_service: MetricsServiceDep,
    start_date: Optional[datetime] = Query(None),
    end_date: Optional[datetime] = Query(None)
):
    validate_dates(start_date, end_date)
    return await metrics_service.get_overview(start_date, end_date)

@router.get("/confidence", response_model=ConfidenceMetricsResponse)
async def get_confidence(
    metrics_service: MetricsServiceDep,
    start_date: Optional[datetime] = Query(None),
    end_date: Optional[datetime] = Query(None)
):
    validate_dates(start_date, end_date)
    return await metrics_service.get_confidence(start_date, end_date)

@router.get("/reviews", response_model=ReviewMetricsResponse)
async def get_reviews(
    metrics_service: MetricsServiceDep,
    start_date: Optional[datetime] = Query(None),
    end_date: Optional[datetime] = Query(None)
):
    validate_dates(start_date, end_date)
    return await metrics_service.get_reviews(start_date, end_date)

@router.get("/clinical", response_model=ClinicalMetricsResponse)
async def get_clinical(
    metrics_service: MetricsServiceDep,
    start_date: Optional[datetime] = Query(None),
    end_date: Optional[datetime] = Query(None)
):
    validate_dates(start_date, end_date)
    return await metrics_service.get_clinical(start_date, end_date)

@router.get("/activity", response_model=ActivityFeedResponse)
async def get_activity(
    metrics_service: MetricsServiceDep,
    limit: int = Query(20, ge=1, le=100),
    cursor: Optional[str] = Query(None)
):
    return await metrics_service.get_activity(limit, cursor)

@router.get("/system", response_model=SystemHealthResponse)
async def get_system(
    metrics_service: MetricsServiceDep
):
    return await metrics_service.get_system_health()
