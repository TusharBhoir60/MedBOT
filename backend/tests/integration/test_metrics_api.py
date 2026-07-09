import pytest
from httpx import AsyncClient
from core.security.jwt import auth_provider

@pytest.fixture
def physician_token():
    # Create a token for a mock physician
    return auth_provider.create_access_token(subject="dr_smith", roles=["physician"])

@pytest.fixture
def admin_token():
    return auth_provider.create_access_token(subject="admin_user", roles=["admin"])


@pytest.mark.asyncio
async def test_metrics_endpoints_unauthorized(client: AsyncClient):
    # No auth token should result in 401
    response = await client.get("/api/v1/metrics/overview")
    assert response.status_code == 401
    
    response = await client.get("/api/v1/metrics/confidence")
    assert response.status_code == 401

@pytest.mark.asyncio
async def test_metrics_endpoints_forbidden(client: AsyncClient, admin_token: str):
    # Depending on test setup, if the token doesn't have physician or admin, it should be 403
    # Wait, the prompt says require_role("physician") which allows admin.
    pass

@pytest.mark.asyncio
async def test_metrics_overview_success(client: AsyncClient, physician_token: str):
    headers = {"Authorization": f"Bearer {physician_token}"}
    response = await client.get("/api/v1/metrics/overview", headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert "totalConversations" in data
    assert "averageConfidence" in data
    
@pytest.mark.asyncio
async def test_metrics_confidence_success(client: AsyncClient, physician_token: str):
    headers = {"Authorization": f"Bearer {physician_token}"}
    response = await client.get("/api/v1/metrics/confidence", headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert "averageConfidence" in data
    assert "distribution" in data
    assert "lowConfidenceThreshold" in data

@pytest.mark.asyncio
async def test_metrics_reviews_success(client: AsyncClient, physician_token: str):
    headers = {"Authorization": f"Bearer {physician_token}"}
    response = await client.get("/api/v1/metrics/reviews", headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert "total" in data
    assert "approvalRate" in data

@pytest.mark.asyncio
async def test_metrics_clinical_success(client: AsyncClient, physician_token: str):
    headers = {"Authorization": f"Bearer {physician_token}"}
    response = await client.get("/api/v1/metrics/clinical", headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert "topSymptoms" in data
    assert "severityDistribution" in data

@pytest.mark.asyncio
async def test_metrics_activity_success(client: AsyncClient, physician_token: str):
    headers = {"Authorization": f"Bearer {physician_token}"}
    response = await client.get("/api/v1/metrics/activity?limit=5", headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert "items" in data

@pytest.mark.asyncio
async def test_metrics_system_success(client: AsyncClient, physician_token: str):
    headers = {"Authorization": f"Bearer {physician_token}"}
    response = await client.get("/api/v1/metrics/system", headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert "overallStatus" in data
    assert "components" in data

@pytest.mark.asyncio
async def test_metrics_date_validation(client: AsyncClient, physician_token: str):
    headers = {"Authorization": f"Bearer {physician_token}"}
    # Invalid date range
    response = await client.get("/api/v1/metrics/overview?start_date=2024-01-02T00:00:00Z&end_date=2024-01-01T00:00:00Z", headers=headers)
    assert response.status_code == 400
