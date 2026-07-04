from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from models.chat import ChatSession

class ChatRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_by_session_id(self, session_id: str) -> Optional[ChatSession]:
        result = await self.session.execute(
            select(ChatSession).where(ChatSession.session_id == session_id)
        )
        return result.scalars().first()

    async def create(self, chat_session: ChatSession) -> ChatSession:
        self.session.add(chat_session)
        await self.session.flush()
        await self.session.refresh(chat_session)
        return chat_session

    async def update(self, chat_session: ChatSession) -> ChatSession:
        await self.session.flush()
        await self.session.refresh(chat_session)
        return chat_session
