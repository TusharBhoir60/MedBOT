import pytest
from unittest.mock import AsyncMock
from services.chat_service import ChatService
from models.chat import ChatSession

@pytest.fixture
def mock_repo():
    return AsyncMock()

@pytest.fixture
def chat_service(mock_repo):
    return ChatService(repository=mock_repo)

@pytest.mark.asyncio
async def test_get_all_sessions(chat_service, mock_repo):
    mock_repo.get_all_for_patient.return_value = [ChatSession(session_id="s1"), ChatSession(session_id="s2")]
    
    sessions = await chat_service.get_all_sessions("patient-1")
    assert len(sessions) == 2
    mock_repo.get_all_for_patient.assert_called_once_with("patient-1")

@pytest.mark.asyncio
async def test_rename_session(chat_service, mock_repo):
    session = ChatSession(session_id="s1", title="Old")
    mock_repo.get_by_session_id.return_value = session
    
    result = await chat_service.rename_session("s1", "New")
    
    assert result is True
    assert session.title == "New"
    mock_repo.update.assert_called_once_with(session)

@pytest.mark.asyncio
async def test_archive_session(chat_service, mock_repo):
    session = ChatSession(session_id="s1", is_archived=False)
    mock_repo.get_by_session_id.return_value = session
    
    result = await chat_service.archive_session("s1")
    
    assert result is True
    assert session.is_archived is True
    mock_repo.update.assert_called_once_with(session)

@pytest.mark.asyncio
async def test_delete_session(chat_service, mock_repo):
    session = ChatSession(session_id="s1")
    mock_repo.get_by_session_id.return_value = session
    
    result = await chat_service.delete_session("s1")
    
    assert result is True
    mock_repo.delete.assert_called_once_with(session)
