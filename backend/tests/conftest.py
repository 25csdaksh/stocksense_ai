"""
Master Pytest Fixtures & Configuration for MarketMind AI.
Provides isolated in-memory test database, test AsyncSession, and FastAPI TestClient.
"""
import pytest
import pytest_asyncio
from typing import AsyncGenerator
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from app.main import app
from app.db.base import Base
from app.db.session import get_db_session
try:
    from scripts.seed import seed_database
except ImportError:
    seed_database = None


@pytest_asyncio.fixture(scope="function")
async def db_engine():
    """Provides a fresh, isolated in-memory SQLite async database engine for each test."""
    test_engine = create_async_engine(
        "sqlite+aiosqlite:///:memory:",
        echo=False,
        future=True
    )
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    yield test_engine

    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    await test_engine.dispose()


@pytest_asyncio.fixture(scope="function")
async def db_session(db_engine) -> AsyncGenerator[AsyncSession, None]:
    """Yields an active AsyncSession connected to the test database."""
    session_factory = async_sessionmaker(
        bind=db_engine,
        class_=AsyncSession,
        expire_on_commit=False,
        autoflush=False
    )
    async with session_factory() as session:
        yield session


@pytest.fixture(scope="function")
def test_client(db_session: AsyncSession):
    """
    FastAPI TestClient with the database session dependency overridden
    to use the isolated in-memory test database.
    """
    async def override_get_db_session():
        yield db_session

    app.dependency_overrides[get_db_session] = override_get_db_session
    with TestClient(app) as client:
        yield client
    app.dependency_overrides.clear()
