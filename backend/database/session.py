"""
Request-scoped database session generator.

Yields an AsyncSession bound to the request lifecycle.
On normal completion the session is committed.
On exception the session is rolled back.
The session is always closed on exit.
"""
import logging
from collections.abc import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession

from database.engine import async_session_factory

logger = logging.getLogger(__name__)


async def get_db_session() -> AsyncGenerator[AsyncSession, None]:
    """Yield a request-scoped async database session.

    Usage via FastAPI Depends:
        session: AsyncSession = Depends(get_db_session)

    The session automatically commits on success and rolls back
    on unhandled exceptions. It is always closed after the request.
    """
    session = async_session_factory()
    try:
        yield session
        await session.commit()
    except Exception:
        await session.rollback()
        raise
    finally:
        await session.close()
