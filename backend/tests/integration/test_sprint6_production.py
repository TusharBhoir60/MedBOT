import pytest
from httpx import AsyncClient
from datetime import datetime, timezone
import jwt
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from main import app
from core.config import settings
from models.review import ReviewTask, ReviewStatus
from database.session import get_db_session

@pytest.fixture
def auth_headers():
    token = jwt.encode(
        {"sub": "dr_smith", "roles": ["physician"], "exp": datetime.now(timezone.utc).timestamp() + 3600},
        settings.security.secret_key,
        algorithm=settings.security.algorithm
    )
    return {"Authorization": f"Bearer {token}"}

@pytest.mark.asyncio
async def test_review_lifecycle(db_session: AsyncSession, client: AsyncClient, auth_headers):
    # 1. Setup - Create a ReviewTask simulating handoff
    task = ReviewTask(
        session_id="test-session-1",
        patient_info={"age": 45},
        symptoms=["chest pain"],
        diagnosis_output={"urgency_level": "emergency"}
    )
    db_session.add(task)
    await db_session.commit()
    await db_session.refresh(task)
    task_id = str(task.id)
    
    # 2. Get Queue
    response = await client.get("/api/v1/review/queue", headers=auth_headers)
    assert response.status_code == 200
    tasks = response.json()
    assert any(t["id"] == task_id for t in tasks)
    
    # 3. Assign Task
    response = await client.post(f"/api/v1/review/{task_id}/assign", headers=auth_headers)
    assert response.status_code == 200
    # BaseSchema uses camelCase alias_generator
    assert response.json()["assigneeId"] == "dr_smith"
    assert response.json()["status"] == "ASSIGNED"
    
    # 4. Add Comment
    response = await client.post(
        f"/api/v1/review/{task_id}/comments",
        json={"content": "Looks like an emergency, please override."},
        headers=auth_headers
    )
    assert response.status_code == 200
    assert response.json()["status"] == "UNDER_REVIEW"
    assert len(response.json()["comments"]) == 1
    
    # 5. Override Task
    override_payload = {
        "final_response": {
            "diagnosis": "Acute Coronary Syndrome",
            "urgency_level": "emergency"
        }
    }
    response = await client.post(
        f"/api/v1/review/{task_id}/override",
        json=override_payload,
        headers=auth_headers
    )
    assert response.status_code == 200
    assert response.status_code == 200
    assert response.json()["status"] == "OVERRIDDEN"

@pytest.mark.asyncio
async def test_review_get_and_reject(db_session: AsyncSession, client: AsyncClient, auth_headers):
    # 1. Setup - Create a ReviewTask
    task = ReviewTask(
        session_id="test-session-reject",
        patient_info={"age": 30},
        symptoms=["headache"],
        diagnosis_output={"urgency_level": "routine"}
    )
    db_session.add(task)
    await db_session.commit()
    await db_session.refresh(task)
    task_id = str(task.id)
    
    # 2. Get Single Task
    response = await client.get(f"/api/v1/review/{task_id}", headers=auth_headers)
    assert response.status_code == 200
    assert response.json()["id"] == task_id
    
    # 3. Reject Task
    response = await client.post(
        f"/api/v1/review/{task_id}/reject",
        json={"reason": "Not enough information"},
        headers=auth_headers
    )
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "REJECTED"
    assert len(data["comments"]) == 1
    assert data["comments"][0]["content"] == "Not enough information"

@pytest.mark.asyncio
async def test_auth_rejection(client: AsyncClient):
    response = await client.get("/api/v1/review/queue")
    # No token
    assert response.status_code in (401, 403)

@pytest.mark.asyncio
async def test_health_component_diagnostics(client: AsyncClient):
    response = await client.get("/api/v1/health")
    assert response.status_code == 200
    data = response.json()
    # BaseSchema uses camelCase alias_generator
    assert "uptimeSeconds" in data
    assert "vectorStoreStatus" in data
    assert "aiServicesStatus" in data
    assert "reviewQueueStatus" in data

@pytest.mark.asyncio
async def test_rate_limiter_and_correlation_id(client: AsyncClient):
    # Test Correlation ID
    response = await client.get("/api/v1/health/live", headers={"x-request-id": "my-custom-id"})
    assert response.status_code == 200
    assert response.headers["x-request-id"] == "my-custom-id"
    
    # Trigger rate limiter.
    import asyncio
    tasks = []
    for _ in range(105):
        tasks.append(client.get("/api/v1/health/live"))
        
    responses = await asyncio.gather(*tasks)
    status_codes = [r.status_code for r in responses]
    
    # Verify at least some requests were rate limited (429)
    assert 429 in status_codes
