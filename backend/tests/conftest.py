"""
Pytest fixtures for AarogyaAgent v2 test suite.

Test Isolation Strategy — Option A: Connection-level Transaction Rollback

Schema lifecycle (session scope — once per test run):
  - Creates all tables at the start of the test session
  - Drops all tables at the end of the test session

Per-test isolation (function scope):
  1. Open an AsyncConnection
  2. Begin a root transaction
  3. Bind an AsyncSession to the connection
  4. Start a nested transaction (SAVEPOINT)
  5. Yield the session to the test
  6. Rollback the root transaction (undoes all mutations)
  7. Close the connection

This means even if application code calls session.commit(), it only
commits to the SAVEPOINT — which is rolled back by the root transaction.
No test data ever reaches the physical table storage.

Database: aarogya_test (created by scripts/init_test_db.sql on first
          Docker startup via docker-entrypoint-initdb.d).
"""
import os
os.environ.setdefault("OPENAI_API_KEY", "mock-key")
import asyncio
from collections.abc import AsyncGenerator
from typing import Any

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import (
    AsyncConnection,
    AsyncSession,
    create_async_engine,
)

from database.base import Base
from main import app

# ── Test database connection ─────────────────────────────────────────────────
TEST_DATABASE_URL = os.getenv(
    "TEST_DATABASE_URL",
    "sqlite+aiosqlite:///./test.db",
)

test_engine = create_async_engine(
    TEST_DATABASE_URL,
    echo=False,
    connect_args={"check_same_thread": False} if TEST_DATABASE_URL.startswith("sqlite") else {},
)


# ── Session-scoped: create / drop schema once per test run ───────────────────
@pytest_asyncio.fixture(scope="session")
async def setup_schema() -> AsyncGenerator[None, None]:
    """Create all tables before the session, drop them after."""
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    yield

    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

    await test_engine.dispose()


# ── Function-scoped: per-test transaction isolation ──────────────────────────
@pytest_asyncio.fixture
async def db_session(setup_schema: Any, monkeypatch: pytest.MonkeyPatch) -> AsyncGenerator[AsyncSession, None]:
    """Yield an AsyncSession that rolls back all mutations after each test.

    The SAVEPOINT pattern ensures application-level session.commit() calls
    are absorbed by the nested transaction and never committed to disk.
    It also monkeypatches async_session_factory globally so standalone code
    (like LangGraph nodes) shares the test transaction, avoiding SQLite locks.
    """
    from contextlib import asynccontextmanager

    connection: AsyncConnection = await test_engine.connect()
    await connection.begin()  # Root transaction

    session = AsyncSession(bind=connection, expire_on_commit=False)
    await session.begin_nested()  # SAVEPOINT

    @asynccontextmanager
    async def mock_factory():
        yield session

    import ai_engine.workflow
    import database.session
    monkeypatch.setattr(database.session, "async_session_factory", mock_factory)
    if hasattr(ai_engine.workflow, "async_session_factory"):
        monkeypatch.setattr(ai_engine.workflow, "async_session_factory", mock_factory)

    yield session

    # Rollback all mutations — leaves tables clean for next test
    await session.close()
    await connection.rollback()
    await connection.close()


# ── HTTP test client ─────────────────────────────────────────────────────────
@pytest_asyncio.fixture
async def client(db_session: AsyncSession) -> AsyncGenerator[AsyncClient, None]:
    """Yield an AsyncClient wired to the FastAPI test app.

    The db_session dependency override ensures HTTP-triggered DB operations
    use the isolated test session (with rollback on teardown).
    """
    from database.session import get_db_session

    async def _override_get_db() -> AsyncGenerator[AsyncSession, None]:
        yield db_session

    app.dependency_overrides[get_db_session] = _override_get_db

    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://testserver",
    ) as ac:
        yield ac

    app.dependency_overrides.clear()
