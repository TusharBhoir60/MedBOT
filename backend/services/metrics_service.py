import logging
from typing import Optional
from datetime import datetime

from core.config import settings
from repositories.metrics_repository import MetricsRepository
from services.health_service import HealthService
from schemas.metrics import (
    OverviewMetricsResponse,
    ConfidenceMetricsResponse,
    ReviewMetricsResponse,
    ClinicalMetricsResponse,
    ActivityFeedResponse,
    SystemHealthResponse,
    HealthComponent
)

logger = logging.getLogger(__name__)

class MetricsService:
    def __init__(self, metrics_repository: MetricsRepository, health_service: HealthService):
        self.metrics_repository = metrics_repository
        self.health_service = health_service

    async def get_overview(self, start_date: Optional[datetime] = None, end_date: Optional[datetime] = None) -> OverviewMetricsResponse:
        logger.debug("Fetching overview metrics")
        data = await self.metrics_repository.get_overview_metrics(start_date, end_date)
        return OverviewMetricsResponse(**data)

    async def get_confidence(self, start_date: Optional[datetime] = None, end_date: Optional[datetime] = None) -> ConfidenceMetricsResponse:
        logger.debug("Fetching confidence metrics")
        # Use settings.ai.confidence_low as the low confidence threshold
        low_threshold = float(getattr(settings.ai, 'confidence_low', 0.4))
        data = await self.metrics_repository.get_confidence_metrics(low_threshold, start_date, end_date)
        return ConfidenceMetricsResponse(**data)

    async def get_reviews(self, start_date: Optional[datetime] = None, end_date: Optional[datetime] = None) -> ReviewMetricsResponse:
        logger.debug("Fetching review metrics")
        data = await self.metrics_repository.get_review_metrics(start_date, end_date)
        return ReviewMetricsResponse(**data)

    async def get_clinical(self, start_date: Optional[datetime] = None, end_date: Optional[datetime] = None) -> ClinicalMetricsResponse:
        logger.debug("Fetching clinical metrics")
        data = await self.metrics_repository.get_clinical_metrics(start_date, end_date)
        return ClinicalMetricsResponse(**data)

    async def get_activity(self, limit: int = 20, cursor: Optional[str] = None) -> ActivityFeedResponse:
        logger.debug("Fetching activity feed", extra={"limit": limit, "cursor": cursor})
        data = await self.metrics_repository.get_activity_feed(limit, cursor)
        return ActivityFeedResponse(**data)

    async def get_system_health(self) -> SystemHealthResponse:
        logger.debug("Fetching system health metrics")
        health_resp = await self.health_service.get_overall_health()
        
        components = []
        if hasattr(health_resp, 'db_status'):
            components.append(HealthComponent(
                name="database",
                status=health_resp.db_status,
                latency_ms=getattr(health_resp, 'db_latency_ms', None),
                message=None
            ))
        if hasattr(health_resp, 'vector_store_status'):
            components.append(HealthComponent(
                name="vector_store",
                status=health_resp.vector_store_status,
                latency_ms=getattr(health_resp, 'vector_store_latency_ms', None),
                message=None
            ))
        if hasattr(health_resp, 'ai_services_status'):
            components.append(HealthComponent(
                name="ai_services",
                status=health_resp.ai_services_status,
                latency_ms=getattr(health_resp, 'ai_services_latency_ms', None),
                message=None
            ))
        if hasattr(health_resp, 'review_queue_status'):
            components.append(HealthComponent(
                name="review_queue",
                status=health_resp.review_queue_status,
                latency_ms=getattr(health_resp, 'review_queue_latency_ms', None),
                message=None
            ))
            
        return SystemHealthResponse(
            overall_status=health_resp.status,
            components=components
        )
