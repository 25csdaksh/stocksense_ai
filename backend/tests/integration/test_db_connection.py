"""
Integration Tests: Database Connection Pool & Lifecycle Management.
"""
import pytest
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy import text
from app.core.config import settings
from app.db.session import engine, init_db, close_db


@pytest.mark.asyncio
async def test_async_database_connection_and_ping(db_engine):
    """Verifies that async engine executes queries and health pings reliably."""
    async with db_engine.connect() as conn:
        res = await conn.execute(text("SELECT 1 AS alive"))
        row = res.fetchone()
        assert row is not None
        assert row[0] == 1


@pytest.mark.asyncio
async def test_async_session_transaction_commit_and_rollback(db_engine):
    """Verifies async session transaction boundaries."""
    session_factory = async_sessionmaker(bind=db_engine, class_=AsyncSession, expire_on_commit=False)
    
    # 1. Successful transaction
    async with session_factory() as session:
        await session.execute(text("CREATE TABLE IF NOT EXISTS test_ping (id INTEGER PRIMARY KEY, msg TEXT);"))
        await session.execute(text("INSERT INTO test_ping (msg) VALUES ('connected');"))
        await session.commit()

    # 2. Verify commit persisted
    async with session_factory() as session:
        res = await session.execute(text("SELECT msg FROM test_ping WHERE msg = 'connected';"))
        assert res.scalar_one() == "connected"

    # 3. Rollback on exception
    try:
        async with session_factory() as session:
            await session.execute(text("INSERT INTO test_ping (msg) VALUES ('should_rollback');"))
            raise RuntimeError("Forced rollback")
    except RuntimeError:
        pass

    async with session_factory() as session:
        res = await session.execute(text("SELECT msg FROM test_ping WHERE msg = 'should_rollback';"))
        assert res.scalar_one_or_none() is None
