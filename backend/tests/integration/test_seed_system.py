"""
Integration Tests: Development Seed Populator & Entity Counts.
"""
import pytest
from sqlalchemy import select, func
from scripts.seed import seed_database
from app.db.models import (
    User, Sector, Company, Stock, StockOHLCV, MarketIndex,
    Fundamental, FinancialStatement, News, Portfolio, Position,
    Watchlist, ResearchDocument, ResearchChunk
)


@pytest.mark.asyncio
async def test_seed_database_execution(db_engine):
    """Verifies that the seed populator seeds all universe assets, OHLCVs, and documents."""
    await seed_database(custom_engine=db_engine)

    from sqlalchemy.ext.asyncio import async_sessionmaker, AsyncSession
    session_factory = async_sessionmaker(bind=db_engine, class_=AsyncSession, expire_on_commit=False)

    async with session_factory() as session:
        # Check Admin User
        admin_res = await session.execute(select(User).where(User.username == "admin"))
        admin = admin_res.scalar_one_or_none()
        assert admin is not None
        assert admin.email == "admin@marketmind.ai"

        # Check Sectors
        sec_count = await session.scalar(select(func.count(Sector.id)))
        assert sec_count == 7

        # Check Companies & Stocks
        comp_count = await session.scalar(select(func.count(Company.id)))
        assert comp_count == 9

        stk_count = await session.scalar(select(func.count(Stock.id)))
        assert stk_count == 9

        # Check OHLCV Bars
        ohlcv_count = await session.scalar(select(func.count(StockOHLCV.id)))
        assert ohlcv_count == 9 * 120  # 1080 bars

        # Check News
        news_count = await session.scalar(select(func.count(News.id)))
        assert news_count >= 5

        # Check Portfolio & Positions
        port_count = await session.scalar(select(func.count(Portfolio.id)))
        assert port_count >= 1

        pos_count = await session.scalar(select(func.count(Position.id)))
        assert pos_count >= 4

        # Check SEC Filings
        doc_count = await session.scalar(select(func.count(ResearchDocument.id)))
        assert doc_count >= 3
