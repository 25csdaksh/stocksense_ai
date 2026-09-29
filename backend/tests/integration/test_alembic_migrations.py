"""
Integration Tests: Alembic Migrations & Schema Table Verification.
"""
import pytest
from sqlalchemy import inspect
from app.db.base import Base


@pytest.mark.asyncio
async def test_all_19_tables_exist(db_engine):
    """Verifies that all 19 database models are registered and generated in the database schema."""
    expected_tables = {
        "users",
        "sectors",
        "companies",
        "stocks",
        "stock_ohlcv",
        "market_indices",
        "fundamentals",
        "financial_statements",
        "news",
        "anomalies",
        "scenario_reports",
        "portfolios",
        "positions",
        "transactions",
        "watchlists",
        "chat_sessions",
        "ai_queries",
        "research_documents",
        "research_chunks"
    }

    async with db_engine.connect() as conn:
        tables = await conn.run_sync(lambda sync_conn: inspect(sync_conn).get_table_names())
        for expected in expected_tables:
            assert expected in tables, f"Expected table '{expected}' not found in database schema."
