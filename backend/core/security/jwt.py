import jwt
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, Optional
from abc import ABC, abstractmethod

from core.config import settings

class AuthProvider(ABC):
    """Abstract interface for Authentication Providers."""
    
    @abstractmethod
    def create_access_token(self, subject: str, roles: list[str]) -> str:
        pass
        
    @abstractmethod
    def decode_token(self, token: str) -> Dict[str, Any]:
        pass

class JWTAuthProvider(AuthProvider):
    """Standalone JWT implementation using PyJWT."""
    
    def __init__(self):
        self.secret_key = settings.security.secret_key
        self.algorithm = settings.security.algorithm
        self.expire_minutes = settings.security.access_token_expire_minutes

    def create_access_token(self, subject: str, roles: list[str]) -> str:
        expire = datetime.now(timezone.utc) + timedelta(minutes=self.expire_minutes)
        to_encode = {
            "sub": subject,
            "roles": roles,
            "exp": expire
        }
        return jwt.encode(to_encode, self.secret_key, algorithm=self.algorithm)

    def decode_token(self, token: str) -> Dict[str, Any]:
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
            return payload
        except jwt.ExpiredSignatureError:
            raise ValueError("Token has expired")
        except jwt.PyJWTError:
            raise ValueError("Invalid authentication token")

# Singleton instance to be used by dependencies
auth_provider: AuthProvider = JWTAuthProvider()
