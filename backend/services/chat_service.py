from typing import Any, Dict, Optional
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
