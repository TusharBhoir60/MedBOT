import logging
from typing import Any
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from pydantic import BaseModel

from core.security.jwt import auth_provider

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/auth", tags=["Authentication"])

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"

class RegisterRequest(BaseModel):
    username: str
    password: str

# Hardcoded users for Sprint 6.5
MOCK_USERS = {
    "dr_smith": {
        "password": "password123",
        "roles": ["physician"]
    },
    "admin": {
        "password": "admin",
        "roles": ["admin", "physician"]
    }
}

@router.post("/login", response_model=TokenResponse)
async def login(form_data: OAuth2PasswordRequestForm = Depends()) -> Any:
    """
    Authenticate user and issue a JWT access token.
    Uses mock credentials or users created in memory.
    """
    user = MOCK_USERS.get(form_data.username)
    if not user or user["password"] != form_data.password:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
        
    access_token = auth_provider.create_access_token(
        subject=form_data.username,
        roles=user["roles"]
    )
    
    return {"access_token": access_token, "token_type": "bearer"}

@router.post("/register")
async def register(data: RegisterRequest) -> Any:
    """
    Register a new user in memory.
    """
    if data.username in MOCK_USERS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already registered"
        )
    
    MOCK_USERS[data.username] = {
        "password": data.password,
        "roles": ["physician"]
    }
    
    return {"message": "User created successfully"}
