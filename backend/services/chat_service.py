from typing import Any, Dict, Optional, List
from repositories.chat_repository import ChatRepository
from models.chat import ChatSession

class ChatService:
    def __init__(self, repository: ChatRepository):
        self._repository = repository

    async def get_session_state(self, session_id: str) -> Optional[Dict[str, Any]]:
        session = await self._repository.get_by_session_id(session_id)
        if session:
            return session.state
        return None

    async def save_session_state(self, session_id: str, state: Dict[str, Any], patient_id: Optional[str] = None):
        session = await self._repository.get_by_session_id(session_id)
        if session:
            session.state = state
            if patient_id:
                session.patient_id = patient_id
            await self._repository.update(session)
        else:
            session = ChatSession(
                session_id=session_id,
                patient_id=patient_id,
                state=state
            )
            await self._repository.create(session)

    async def get_all_sessions(self, patient_id: str) -> List[ChatSession]:
        return await self._repository.get_all_for_patient(patient_id)

    async def get_session(self, session_id: str) -> Optional[ChatSession]:
        return await self._repository.get_by_session_id(session_id)

    async def rename_session(self, session_id: str, title: str) -> bool:
        session = await self._repository.get_by_session_id(session_id)
        if session:
            session.title = title
            await self._repository.update(session)
            return True
        return False

    async def archive_session(self, session_id: str) -> bool:
        session = await self._repository.get_by_session_id(session_id)
        if session:
            session.is_archived = True
            await self._repository.update(session)
            return True
        return False

    async def delete_session(self, session_id: str) -> bool:
        session = await self._repository.get_by_session_id(session_id)
        if session:
            await self._repository.delete(session)
            return True
        return False
