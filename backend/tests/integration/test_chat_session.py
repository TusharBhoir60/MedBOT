import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession
from models.chat import ChatSession
from sqlalchemy.future import select

@pytest.mark.asyncio
async def test_persistent_chat_session(db_session: AsyncSession, client: AsyncClient):
    # Call invoke which should now save to the DB
    response = await client.post(
        "/api/v1/chat/invoke",
        json={
            "session_id": "test-persist-session",
            "message": "I have a headache",
            "patient_info": {"age": 30},
            "symptoms": ["headache"]
        }
    )
    
    assert response.status_code == 200
    data = response.json()
    assert "messages" in data
    
    # Verify in DB
    result = await db_session.execute(
        select(ChatSession).where(ChatSession.session_id == "test-persist-session")
    )
    session_record = result.scalars().first()
    
    assert session_record is not None
    assert session_record.session_id == "test-persist-session"
    assert "messages" in session_record.state
