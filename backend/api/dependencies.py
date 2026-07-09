"""
Dependency injection wiring for the API layer.

All FastAPI Depends factories live here. Each factory follows the
chain: Session → Repository → Service, ensuring clean separation
of layers and easy test-time overrides via app.dependency_overrides.
"""
from typing import Annotated, Any, Callable
import logging

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession

from database.session import get_db_session
from repositories.health_repository import HealthRepository
from services.health_service import HealthService
from core.security.jwt import auth_provider
from repositories.chat_repository import ChatRepository
from services.chat_service import ChatService
from repositories.metrics_repository import MetricsRepository
from services.metrics_service import MetricsService

logger = logging.getLogger(__name__)

# Type alias for the injected DB session
DatabaseSession = Annotated[AsyncSession, Depends(get_db_session)]


def get_health_repository(session: DatabaseSession) -> HealthRepository:
    """Construct a HealthRepository with the request-scoped DB session."""
    return HealthRepository(session=session)


def get_health_service(
    repository: Annotated[HealthRepository, Depends(get_health_repository)],
) -> HealthService:
    """Construct a HealthService with its HealthRepository dependency."""
    return HealthService(repository=repository)


# Type alias for use in route handlers
HealthServiceDep = Annotated[HealthService, Depends(get_health_service)]

def get_chat_repository(session: DatabaseSession) -> ChatRepository:
    """Construct a ChatRepository with the request-scoped DB session."""
    return ChatRepository(session=session)

def get_chat_service(
    repository: Annotated[ChatRepository, Depends(get_chat_repository)],
) -> ChatService:
    """Construct a ChatService with its ChatRepository dependency."""
    return ChatService(repository=repository)

ChatServiceDep = Annotated[ChatService, Depends(get_chat_service)]

def get_metrics_repository(session: DatabaseSession) -> MetricsRepository:
    """Construct a MetricsRepository with the request-scoped DB session."""
    return MetricsRepository(session=session)

def get_metrics_service(
    repository: Annotated[MetricsRepository, Depends(get_metrics_repository)],
    health_service: HealthServiceDep,
) -> MetricsService:
    """Construct a MetricsService with its MetricsRepository and HealthService dependencies."""
    return MetricsService(metrics_repository=repository, health_service=health_service)

MetricsServiceDep = Annotated[MetricsService, Depends(get_metrics_service)]

security = HTTPBearer()

def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)) -> dict[str, Any]:
    """
    Validates the bearer token and returns the user payload.
    """
    try:
        payload = auth_provider.decode_token(credentials.credentials)
        return payload
    except ValueError as e:
        logger.warning(f"Authentication failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e),
            headers={"WWW-Authenticate": "Bearer"},
        )

def require_role(required_role: str) -> Callable:
    """
    Dependency factory to check if the current user has the required role.
    """
    def role_checker(current_user: dict[str, Any] = Depends(get_current_user)) -> dict[str, Any]:
        roles = current_user.get("roles", [])
        if required_role not in roles and "admin" not in roles:
            logger.warning(f"User {current_user.get('sub')} denied access. Requires role: {required_role}")
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not enough permissions"
            )
        return current_user
    return role_checker