import pytest
from sqlalchemy.ext.asyncio import AsyncSession
from models.chat import ChatSession
from repositories.chat_repository import ChatRepository

@pytest.mark.asyncio
async def test_create_and_read_session(db_session: AsyncSession):
    repo = ChatRepository(db_session)
    session = ChatSession(
        session_id="test-session-1",
        patient_id="patient-1",
        title="Test Conversation",
        state={"messages": []}
    )
    
    created = await repo.create(session)
    assert created.session_id == "test-session-1"
    
    fetched = await repo.get_by_session_id("test-session-1")
    assert fetched is not None
    assert fetched.title == "Test Conversation"

@pytest.mark.asyncio
async def test_update_session(db_session: AsyncSession):
    repo = ChatRepository(db_session)
    session = ChatSession(
        session_id="test-session-2",
        patient_id="patient-1",
        title="Test",
        state={"messages": []}
    )
    await repo.create(session)
    
    session.title = "Updated Title"
    session.is_archived = True
    await repo.update(session)
    
    fetched = await repo.get_by_session_id("test-session-2")
    assert fetched.title == "Updated Title"
    assert fetched.is_archived is True

@pytest.mark.asyncio
async def test_get_all_for_patient(db_session: AsyncSession):
    repo = ChatRepository(db_session)
    await repo.create(ChatSession(session_id="test-session-3", patient_id="patient-2", title="C1", state={}))
    await repo.create(ChatSession(session_id="test-session-4", patient_id="patient-2", title="C2", state={}))
    
    sessions = await repo.get_all_for_patient("patient-2")
    assert len(sessions) == 2

@pytest.mark.asyncio
async def test_delete_session(db_session: AsyncSession):
    repo = ChatRepository(db_session)
    session = ChatSession(session_id="test-session-5", patient_id="patient-1", state={})
    await repo.create(session)
    
    await repo.delete(session)
    
    fetched = await repo.get_by_session_id("test-session-5")
    assert fetched is None
