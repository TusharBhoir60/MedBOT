"""
Unit tests for Pydantic schemas — no database required.

Validates:
  - BaseSchema camelCase alias generation
  - HealthLiveResponse and HealthReadyResponse field constraints
  - ErrorResponse correlation_id field presence
  - CMARAgentOutput schema from ai_engine/models.py
"""
from datetime import datetime, timezone
import pytest

from schemas.base_schema import BaseSchema, to_camel_case
from schemas.health import (
    ErrorResponse,
    HealthDBResponse,
    HealthLiveResponse,
    HealthReadyResponse,
    HealthResponse,
)
from ai_engine.models import CMARAgentOutput


class TestCamelCaseConversion:
    def test_single_word_unchanged(self) -> None:
        assert to_camel_case("status") == "status"

    def test_two_word_field(self) -> None:
        assert to_camel_case("created_at") == "createdAt"

    def test_three_word_field(self) -> None:
        assert to_camel_case("db_latency_ms") == "dbLatencyMs"

    def test_already_camel_case(self) -> None:
        # Single word — no underscore — returns unchanged
        assert to_camel_case("version") == "version"


class TestHealthLiveResponse:
    def test_serializes_to_camel_case(self) -> None:
        response = HealthLiveResponse(
            status="healthy",
            version="0.1.0",
            timestamp=datetime.now(timezone.utc),
        )
        dumped = response.model_dump(mode="json", by_alias=True)
        assert "status" in dumped
        assert "version" in dumped
        assert "timestamp" in dumped
        # Should not contain snake_case keys when by_alias=True
        assert "created_at" not in dumped

    def test_valid_status_field(self) -> None:
        response = HealthLiveResponse(
            status="healthy",
            version="0.1.0",
            timestamp=datetime.now(timezone.utc),
        )
        assert response.status == "healthy"
        assert response.version == "0.1.0"


class TestHealthReadyResponse:
    def test_db_latency_ms_is_float(self) -> None:
        response = HealthReadyResponse(
            status="healthy",
            version="0.1.0",
            timestamp=datetime.now(timezone.utc),
            db_status="connected",
            db_latency_ms=4.23,
        )
        assert isinstance(response.db_latency_ms, float)
        assert response.db_latency_ms == 4.23

    def test_degraded_status_allowed(self) -> None:
        response = HealthReadyResponse(
            status="degraded",
            version="0.1.0",
            timestamp=datetime.now(timezone.utc),
            db_status="disconnected",
            db_latency_ms=0.0,
        )
        assert response.status == "degraded"
        assert response.db_status == "disconnected"

    def test_camel_case_alias_db_latency(self) -> None:
        response = HealthReadyResponse(
            status="healthy",
            version="0.1.0",
            timestamp=datetime.now(timezone.utc),
            db_status="connected",
            db_latency_ms=1.5,
        )
        dumped = response.model_dump(mode="json", by_alias=True)
        assert "dbLatencyMs" in dumped
        assert "dbStatus" in dumped


class TestErrorResponse:
    def test_error_response_has_correlation_id(self) -> None:
        response = ErrorResponse(
            error_code="DATABASE_ERROR",
            message="DB unreachable",
            correlation_id="test-corr-id-123",
            timestamp=datetime.now(timezone.utc),
        )
        assert response.correlation_id == "test-corr-id-123"
        assert response.error_code == "DATABASE_ERROR"


class TestCMARAgentOutput:
    def test_default_metadata_is_empty_dict(self) -> None:
        output = CMARAgentOutput(
            agent_id="symptom_agent_v1",
            confidence_score=0.87,
            triage_decision="URGENT",
            reasoning_trace=["High fever detected", "Duration > 72h"],
        )
        assert output.metadata == {}
        assert output.confidence_score == 0.87
        assert len(output.reasoning_trace) == 2

    def test_confidence_score_accepts_boundary_values(self) -> None:
        low = CMARAgentOutput(
            agent_id="a", confidence_score=0.0, triage_decision="LOW",
            reasoning_trace=[],
        )
        high = CMARAgentOutput(
            agent_id="a", confidence_score=1.0, triage_decision="HIGH",
            reasoning_trace=[],
        )
        assert low.confidence_score == 0.0
        assert high.confidence_score == 1.0


class TestHealthResponse:
    def test_overall_health_response(self) -> None:
        response = HealthResponse(
            status="healthy",
            version="0.1.0",
            timestamp=datetime.now(timezone.utc),
            uptime_seconds=123.45,
        )
        assert response.status == "healthy"
        assert response.version == "0.1.0"
        assert response.uptime_seconds == 123.45


class TestHealthDBResponse:
    def test_db_health_response(self) -> None:
        response = HealthDBResponse(
            status="healthy",
            version="0.1.0",
            timestamp=datetime.now(timezone.utc),
            db_status="connected",
            db_latency_ms=10.5,
        )
        assert response.status == "healthy"
        assert response.db_status == "connected"
        assert response.db_latency_ms == 10.5

        dumped = response.model_dump(mode="json", by_alias=True)
        assert "dbLatencyMs" in dumped
        assert "dbStatus" in dumped
