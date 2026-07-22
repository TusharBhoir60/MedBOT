from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from models.user import User

class UserRepository:
    def __init__(self, session: AsyncSession):
        self.session = session
        
    async def get_by_username(self, username: str) -> Optional[User]:
        stmt = select(User).where(User.username == username)
        result = await self.session.execute(stmt)
        return result.scalars().first()
        
    async def create(self, user: User) -> User:
        self.session.add(user)
        await self.session.commit()
        await self.session.refresh(user)
        return user
        
    async def update(self, user: User) -> User:
        await self.session.commit()
        await self.session.refresh(user)
        return user
