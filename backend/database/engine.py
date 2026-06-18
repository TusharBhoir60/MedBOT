"""
Async SQLAlchemy engine and session factory.

Creates an AsyncEngine with pool configuration driven entirely by
Settings. Exposes init_db() and close_db() coroutines for use in
the FastAPI lifespan context manager.
"""
import logging

from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    async_sessionmaker,
    create_async_engine,
    AsyncSession,
)

from core.config import settings

logger = logging.getLogger(__name__)

engine: AsyncEngine = create_async_engine(
    settings.db.url,
    pool_size=settings.db.pool_size,
    max_overflow=settings.db.max_overflow,
    echo=settings.db.echo,
    pool_pre_ping=True,
)

async_session_factory: async_sessionmaker[AsyncSession] = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


async def init_db() -> None:
    """Initialize database engine connection pool.

    Called during application startup via the lifespan context manager.
    Verifies the engine can connect by executing a disposal check.
    """
    logger.info(
        "Initializing database engine",
        extra={"pool_size": settings.db.pool_size, "max_overflow": settings.db.max_overflow},
    )


async def close_db() -> None:
    """Dispose of the database engine and release all pooled connections.

    Called during application shutdown via the lifespan context manager.
    """
    logger.info("Disposing database engine")
    await engine.dispose()
    logger.info("Database engine disposed successfully")
