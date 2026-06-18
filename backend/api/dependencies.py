"""
Dependency injection wiring for the API layer.

All FastAPI Depends factories live here. Each factory follows the
chain: Session → Repository → Service, ensuring clean separation
of layers and easy test-time overrides via app.dependency_overrides.
"""
from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from database.session import get_db_session
from repositories.health_repository import HealthRepository
from services.health_service import HealthService

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
