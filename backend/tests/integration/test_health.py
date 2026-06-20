"""
Integration tests for the Health endpoints.

Tests /health/live and /health/ready, verifying that the actual HTTP
responses match the Pydantic schemas and that DB connections work.
"""
import pytest
from httpx import AsyncClient
from datetime import datetime, timezone


@pytest.mark.asyncio
async def test_health_live_returns_200(client: AsyncClient) -> None:
    """The liveness probe should always return 200 OK without DB checks."""
    response = await client.get("/api/v1/health/live")

    assert response.status_code == 200
    data = response.json()

    assert data["status"] == "healthy"
    assert "version" in data
    assert "timestamp" in data

    # Timestamp must be parseable
    parsed = datetime.fromisoformat(data["timestamp"])
    assert parsed is not None


@pytest.mark.asyncio
async def test_health_ready_returns_200_when_db_connected(client: AsyncClient) -> None:
    """The readiness probe should return 200 OK when DB is reachable.
    
    This verifies that the test isolation SAVEPOINT pattern allows
    successful queries (SELECT 1).
    """
    response = await client.get("/api/v1/health/ready")

    assert response.status_code == 200
    data = response.json()

    assert data["status"] == "healthy"
    assert data["dbStatus"] == "connected"
    assert isinstance(data["dbLatencyMs"], float)
    assert data["dbLatencyMs"] >= 0.0

    # Ensure camelCase aliases were applied
    assert "db_latency_ms" not in data


@pytest.mark.asyncio
async def test_health_ready_returns_503_when_db_disconnected(client: AsyncClient, monkeypatch: pytest.MonkeyPatch) -> None:
    """The readiness probe should return 503 when the DB is unreachable."""
    from repositories.health_repository import HealthRepository

    # Mock the ping_db to return disconnected status
    async def mock_ping_db(*args, **kwargs) -> dict[str, float | str]:
        return {"status": "disconnected", "latency_ms": 150.5}

    monkeypatch.setattr(HealthRepository, "ping_db", mock_ping_db)

    response = await client.get("/api/v1/health/ready")

    assert response.status_code == 503
    data = response.json()

    assert data["status"] == "degraded"
    assert data["dbStatus"] == "disconnected"
    assert data["dbLatencyMs"] == 150.5


@pytest.mark.asyncio
async def test_health_overall_returns_200_when_db_connected(client: AsyncClient) -> None:
    """The overall health endpoint should return 200 OK when DB is reachable."""
    response = await client.get("/api/v1/health")

    assert response.status_code == 200
    data = response.json()

    assert data["status"] == "healthy"
    assert "version" in data
    assert "timestamp" in data


@pytest.mark.asyncio
async def test_health_overall_returns_503_when_db_disconnected(client: AsyncClient, monkeypatch: pytest.MonkeyPatch) -> None:
    """The overall health endpoint should return 503 when the DB is unreachable."""
    from repositories.health_repository import HealthRepository

    async def mock_ping_db(*args, **kwargs) -> dict[str, float | str]:
        return {"status": "disconnected", "latency_ms": 150.5}

    monkeypatch.setattr(HealthRepository, "ping_db", mock_ping_db)

    response = await client.get("/api/v1/health")

    assert response.status_code == 503
    data = response.json()

    assert data["status"] == "degraded"
    assert "version" in data


@pytest.mark.asyncio
async def test_health_db_returns_200_when_db_connected(client: AsyncClient) -> None:
    """The database health endpoint should return 200 OK when DB is reachable."""
    response = await client.get("/api/v1/health/db")

    assert response.status_code == 200
    data = response.json()

    assert data["status"] == "healthy"
    assert data["dbStatus"] == "connected"
    assert isinstance(data["dbLatencyMs"], float)


@pytest.mark.asyncio
async def test_health_db_returns_503_when_db_disconnected(client: AsyncClient, monkeypatch: pytest.MonkeyPatch) -> None:
    """The database health endpoint should return 503 when the DB is unreachable."""
    from repositories.health_repository import HealthRepository

    async def mock_ping_db(*args, **kwargs) -> dict[str, float | str]:
        return {"status": "disconnected", "latency_ms": 150.5}

    monkeypatch.setattr(HealthRepository, "ping_db", mock_ping_db)

    response = await client.get("/api/v1/health/db")

    assert response.status_code == 503
    data = response.json()

    assert data["status"] == "degraded"
    assert data["dbStatus"] == "disconnected"
    assert data["dbLatencyMs"] == 150.5
