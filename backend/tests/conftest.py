"""
Shared test fixtures.

- client:  FastAPI TestClient — Clerk auth bypassed, isolated in-memory DB
- mock_ai: patches the AI dispatch so no provider is ever called
"""
import pytest
from unittest.mock import patch
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from backend.db.database import Base, get_db
from backend.main import app
from backend.middleware.verify_clerk import get_current_user

FAKE_USER_ID = "user_test_123"

# In-memory SQLite shared across connections (StaticPool keeps one connection)
_test_engine = create_async_engine(
    "sqlite+aiosqlite:///:memory:",
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
_TestSession = sessionmaker(_test_engine, class_=AsyncSession, expire_on_commit=False)


async def _override_get_db():
    async with _TestSession() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise


@pytest.fixture
def client():
    app.dependency_overrides[get_current_user] = lambda: FAKE_USER_ID
    app.dependency_overrides[get_db] = _override_get_db

    # Create tables on the test engine before the app runs
    import asyncio

    async def _create():
        async with _test_engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)

    asyncio.get_event_loop().run_until_complete(_create())

    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()


@pytest.fixture
def mock_ai():
    """Patch the provider dispatch — tests never hit Gemini/Anthropic."""
    with patch(
        "backend.services.ai_service._dispatch",
        return_value="Mocked AI reply ⚠️ educational purposes only",
    ) as m:
        yield m
