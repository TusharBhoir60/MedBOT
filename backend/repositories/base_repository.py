"""
Generic async repository base with typed CRUD operations.

Uses Python generics to provide type-safe data access for any
SQLAlchemy ORM model. Concrete repositories inherit from this
base and get standard CRUD methods without reimplementation.

A RepositoryProtocol is also defined using structural subtyping
(typing.Protocol) so that concrete repositories can be tested
and swapped without formal ABC inheritance.
"""
import logging
from typing import Generic, TypeVar, Protocol, runtime_checkable
from uuid import UUID

from sqlalchemy import select, func, delete as sa_delete
from sqlalchemy.ext.asyncio import AsyncSession

from database.base import Base

logger = logging.getLogger(__name__)

T = TypeVar("T", bound=Base)


@runtime_checkable
class RepositoryProtocol(Protocol[T]):
    """Structural protocol defining the repository contract.

    Any class that implements these methods satisfies this protocol
    without needing to inherit from it. Used for type checking and
    test-time dependency injection.
    """

    async def get_by_id(self, entity_id: UUID) -> T | None: ...
    async def get_all(self, skip: int = 0, limit: int = 100) -> list[T]: ...
    async def create(self, entity: T) -> T: ...
    async def update(self, entity: T) -> T: ...
    async def delete(self, entity_id: UUID) -> bool: ...
    async def count(self) -> int: ...


class BaseRepository(Generic[T]):
    """Generic async CRUD repository for SQLAlchemy ORM models.

    Args:
        model: The SQLAlchemy ORM model class this repository manages.
        session: The async database session for the current request scope.
    """

    def __init__(self, model: type[T], session: AsyncSession) -> None:
        self._model = model
        self._session = session
        self._logger = logging.getLogger(f"{__name__}.{model.__name__}")

    async def get_by_id(self, entity_id: UUID) -> T | None:
        """Retrieve a single entity by its primary key.

        Returns None if the entity does not exist.
        """
        self._logger.debug("get_by_id: %s", entity_id)
        result = await self._session.get(self._model, entity_id)
        return result

    async def get_all(self, skip: int = 0, limit: int = 100) -> list[T]:
        """Retrieve a paginated list of entities.

        Args:
            skip: Number of records to skip (offset).
            limit: Maximum number of records to return.
        """
        self._logger.debug("get_all: skip=%d limit=%d", skip, limit)
        stmt = select(self._model).offset(skip).limit(limit)
        result = await self._session.execute(stmt)
        return list(result.scalars().all())

    async def create(self, entity: T) -> T:
        """Persist a new entity to the database.

        The entity is added to the session and flushed (but not committed,
        as commit is handled by the session lifecycle in session.py).
        """
        self._logger.debug("create: %s", type(entity).__name__)
        self._session.add(entity)
        await self._session.flush()
        await self._session.refresh(entity)
        return entity

    async def update(self, entity: T) -> T:
        """Merge changes to an existing entity.

        The entity must already have a valid primary key.
        """
        self._logger.debug("update: %s", type(entity).__name__)
        merged = await self._session.merge(entity)
        await self._session.flush()
        await self._session.refresh(merged)
        return merged

    async def delete(self, entity_id: UUID) -> bool:
        """Delete an entity by its primary key.

        Returns True if the entity was found and deleted, False otherwise.
        """
        self._logger.debug("delete: %s", entity_id)
        entity = await self.get_by_id(entity_id)
        if entity is None:
            return False
        await self._session.delete(entity)
        await self._session.flush()
        return True

    async def count(self) -> int:
        """Return the total count of entities in the table."""
        stmt = select(func.count()).select_from(self._model)
        result = await self._session.execute(stmt)
        count_value = result.scalar_one()
        return int(count_value)
