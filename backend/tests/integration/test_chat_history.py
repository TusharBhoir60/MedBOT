"""
Integration tests for the Chat History API.
Verifies GET /history, GET /history/{session_id}, PATCH /history/{session_id},
DELETE /history/{session_id}, and POST /history/{session_id}/archive.
"""
import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession
from models.chat import ChatSession
from repositories.chat_repository import ChatRepository
from core.security.jwt import auth_provider


# ─── Helpers ──────────────────────────────────────────────────────────────────

PATIENT_ID = "patient-history-test"
OTHER_PATIENT_ID = "patient-other"


def _auth_headers(patient_id: str = PATIENT_ID) -> dict:
    token = auth_provider.create_access_token(subject=patient_id, roles=["patient"])
    return {"Authorization": f"Bearer {token}"}


async def _create_session(
    db_session: AsyncSession,
    session_id: str,
    patient_id: str = PATIENT_ID,
    title: str = "Test Conversation",
    messages: list | None = None,
) -> ChatSession:
    repo = ChatRepository(db_session)
    session = ChatSession(
        session_id=session_id,
        patient_id=patient_id,
        title=title,
        state={"messages": messages or [{"role": "human", "content": "Hello"}, {"role": "ai", "content": "Hi there!"}]},
    )
    return await repo.create(session)


# ─── Tests ────────────────────────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_get_history_returns_sessions(client: AsyncClient, db_session: AsyncSession):
    """GET /history returns a summary list for the authenticated patient."""
    await _create_session(db_session, "hist-1", title="Headache Assessment")
    await _create_session(db_session, "hist-2", title="Fever Check")

    response = await client.get("/api/v1/chat/history", headers=_auth_headers())
    assert response.status_code == 200
    data = response.json()
    session_ids = [s["session_id"] for s in data]
    assert "hist-1" in session_ids
    assert "hist-2" in session_ids


@pytest.mark.asyncio
async def test_get_history_excludes_other_patient(client: AsyncClient, db_session: AsyncSession):
    """GET /history only returns sessions belonging to the authenticated patient."""
    await _create_session(db_session, "hist-own", patient_id=PATIENT_ID)
    await _create_session(db_session, "hist-other", patient_id=OTHER_PATIENT_ID)

    response = await client.get("/api/v1/chat/history", headers=_auth_headers())
    assert response.status_code == 200
    data = response.json()
    session_ids = [s["session_id"] for s in data]
    assert "hist-own" in session_ids
    assert "hist-other" not in session_ids


@pytest.mark.asyncio
async def test_get_history_summary_fields(client: AsyncClient, db_session: AsyncSession):
    """GET /history response includes all expected summary fields."""
    await _create_session(db_session, "hist-fields", title="Summary Fields Test")

    response = await client.get("/api/v1/chat/history", headers=_auth_headers())
    assert response.status_code == 200
    session = next(s for s in response.json() if s["session_id"] == "hist-fields")

    assert "session_id" in session
    assert "title" in session
    assert "is_archived" in session
    assert "updated_at" in session
    assert "created_at" in session
    assert "last_message_preview" in session
    assert "message_count" in session
    assert session["message_count"] == 2


@pytest.mark.asyncio
async def test_get_history_requires_auth(client: AsyncClient):
    """GET /history returns 403 without a valid token (FastAPI HTTPBearer default)."""
    response = await client.get("/api/v1/chat/history")
    # FastAPI's HTTPBearer returns 403 when no Authorization header is present
    assert response.status_code in (401, 403)


@pytest.mark.asyncio
async def test_get_session_detail(client: AsyncClient, db_session: AsyncSession):
    """GET /history/{session_id} returns full state for owned session."""
    await _create_session(db_session, "detail-1", title="Detail Test")

    response = await client.get("/api/v1/chat/history/detail-1", headers=_auth_headers())
    assert response.status_code == 200
    data = response.json()
    assert data["session_id"] == "detail-1"
    assert data["title"] == "Detail Test"
    assert "state" in data
    assert "messages" in data["state"]


@pytest.mark.asyncio
async def test_get_session_detail_not_found(client: AsyncClient):
    """GET /history/{session_id} returns 404 for non-existent session."""
    response = await client.get("/api/v1/chat/history/nonexistent-id", headers=_auth_headers())
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_get_session_detail_other_patient(client: AsyncClient, db_session: AsyncSession):
    """GET /history/{session_id} returns 404 for session owned by another patient."""
    await _create_session(db_session, "other-detail-1", patient_id=OTHER_PATIENT_ID)

    response = await client.get("/api/v1/chat/history/other-detail-1", headers=_auth_headers())
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_rename_session(client: AsyncClient, db_session: AsyncSession):
    """PATCH /history/{session_id} successfully renames a conversation."""
    await _create_session(db_session, "rename-1", title="Old Title")

    response = await client.patch(
        "/api/v1/chat/history/rename-1",
        json={"title": "New Title"},
        headers=_auth_headers(),
    )
    assert response.status_code == 200
    assert response.json()["status"] == "success"

    # Verify persisted
    detail = await client.get("/api/v1/chat/history/rename-1", headers=_auth_headers())
    assert detail.json()["title"] == "New Title"


@pytest.mark.asyncio
async def test_rename_session_not_found(client: AsyncClient):
    """PATCH /history/{session_id} returns 404 for non-existent session."""
    response = await client.patch(
        "/api/v1/chat/history/nonexistent-id",
        json={"title": "Title"},
        headers=_auth_headers(),
    )
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_delete_session(client: AsyncClient, db_session: AsyncSession):
    """DELETE /history/{session_id} removes the session."""
    await _create_session(db_session, "delete-1")

    response = await client.delete("/api/v1/chat/history/delete-1", headers=_auth_headers())
    assert response.status_code == 204

    # Verify gone
    detail = await client.get("/api/v1/chat/history/delete-1", headers=_auth_headers())
    assert detail.status_code == 404


@pytest.mark.asyncio
async def test_delete_session_not_owned(client: AsyncClient, db_session: AsyncSession):
    """DELETE /history/{session_id} returns 404 for session owned by another patient."""
    await _create_session(db_session, "delete-other-1", patient_id=OTHER_PATIENT_ID)

    response = await client.delete("/api/v1/chat/history/delete-other-1", headers=_auth_headers())
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_archive_session(client: AsyncClient, db_session: AsyncSession):
    """POST /history/{session_id}/archive marks the session as archived."""
    await _create_session(db_session, "archive-1")

    response = await client.post("/api/v1/chat/history/archive-1/archive", headers=_auth_headers())
    assert response.status_code == 200
    assert response.json()["status"] == "success"

    # Verify is_archived = True in detail
    detail = await client.get("/api/v1/chat/history/archive-1", headers=_auth_headers())
    assert detail.json()["is_archived"] is True


@pytest.mark.asyncio
async def test_archive_session_not_found(client: AsyncClient):
    """POST /history/{session_id}/archive returns 404 for non-existent session."""
    response = await client.post("/api/v1/chat/history/nonexistent-id/archive", headers=_auth_headers())
    assert response.status_code == 404
