from typing import Optional
import bcrypt
from models.user import User
from repositories.user_repository import UserRepository

class UserService:
    def __init__(self, repository: UserRepository):
        self.repository = repository
        
    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        return bcrypt.checkpw(plain_password.encode('utf-8'), hashed_password.encode('utf-8'))
        
    def get_password_hash(self, password: str) -> str:
        salt = bcrypt.gensalt()
        hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
        return hashed.decode('utf-8')
        
    async def authenticate(self, username: str, password: str) -> Optional[User]:
        user = await self.repository.get_by_username(username)
        if not user:
            return None
        if not self.verify_password(password, user.hashed_password):
            return None
        return user
        
    async def get_by_username(self, username: str) -> Optional[User]:
        return await self.repository.get_by_username(username)
        
    async def update_password(self, user: User, new_password: str) -> User:
        user.hashed_password = self.get_password_hash(new_password)
        return await self.repository.update(user)
        
    async def register(self, username: str, password: str, role: str = "customer") -> User:
        hashed_password = self.get_password_hash(password)
        user = User(username=username, hashed_password=hashed_password, role=role)
        return await self.repository.create(user)
