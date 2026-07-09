import pytest
from datetime import datetime, timezone, timedelta
from unittest.mock import AsyncMock, MagicMock
from services.metrics_service import MetricsService
from schemas.metrics import OverviewMetricsResponse, ConfidenceMetricsResponse

@pytest.mark.asyncio
async def test_metrics_service_overview():
    mock_repo = AsyncMock()
    mock_repo.get_overview_metrics.return_value = {
        "total_conversations": 10,
        "total_review_tasks": 5,
        "pending_reviews": 1,
        "assigned_reviews": 1,
        "under_review": 1,
        "approved_reviews": 1,
        "rejected_reviews": 0,
        "overridden_reviews": 1,
        "closed_reviews": 0,
        "average_confidence": 0.85,
        "average_review_time_seconds": 120.0,
        "escalation_rate": 0.5,
        "average_messages_per_conversation": 4.5,
    }
    
    mock_health = AsyncMock()
    service = MetricsService(mock_repo, mock_health)
    
    result = await service.get_overview()
    
    assert isinstance(result, OverviewMetricsResponse)
    assert result.total_conversations == 10
    assert result.average_confidence == 0.85
    assert result.escalation_rate == 0.5

@pytest.mark.asyncio
async def test_metrics_service_confidence():
    mock_repo = AsyncMock()
    mock_repo.get_confidence_metrics.return_value = {
        "average_confidence": 0.75,
        "minimum_confidence": 0.1,
        "maximum_confidence": 0.9,
        "sample_size": 20,
        "distribution": [],
        "agent_averages": [],
        "condition_averages": [],
        "low_confidence_cases": 2,
        "low_confidence_threshold": 0.4
    }
    
    mock_health = AsyncMock()
    service = MetricsService(mock_repo, mock_health)
    
    result = await service.get_confidence()
    
    assert isinstance(result, ConfidenceMetricsResponse)
    assert result.average_confidence == 0.75
    assert result.low_confidence_cases == 2
