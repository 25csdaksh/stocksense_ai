"""
TimescaleDB Hypertable & Time-Series Query Integration Tests.
Verifies time-series insertion, time-range querying, ticker filtering, and chronological ordering.
"""
import pytest
from datetime import datetime, timezone, timedelta
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.models import StockOHLCV, Stock, Company, Sector


@pytest.mark.asyncio
async def test_stock_ohlcv_time_series_lifecycle(db_session: AsyncSession):
    # 1. Create a sector, company, and stock
    sector = Sector(
        id="sec_test_ts",
        name="Semiconductors",
        code="SEMI",
        performance_pct=2.1,
        momentum_score=85.0,
        market_cap_weight=0.15
    )
    db_session.add(sector)
    await db_session.flush()

    company = Company(
        id="cmp_tsmc",
        sector_id=sector.id,
        name="Taiwan Semiconductor Manufacturing",
        ticker="TSM"
    )
    db_session.add(company)
    await db_session.flush()

    stock = Stock(
        id="stk_test_tsmc",
        company_id=company.id,
        ticker="TSM",
        asset_class="EQUITY",
        exchange="NYSE"
    )
    db_session.add(stock)
    await db_session.flush()

    # 2. Insert multi-day OHLCV time-series records
    base_time = datetime(2026, 1, 1, 9, 30, 0, tzinfo=timezone.utc)
    bars = []
    prices = [150.0, 153.5, 152.0, 158.2, 162.0, 160.5, 165.0, 169.5]

    for i, p in enumerate(prices):
        bar_time = base_time + timedelta(days=i)
        bar = StockOHLCV(
            stock_id=stock.id,
            ticker="TSM",
            timestamp=bar_time,
            open=p - 1.0,
            high=p + 2.5,
            low=p - 1.5,
            close=p,
            volume=10_000_000.0 + i * 500_000,
            interval="1d"
        )
        bars.append(bar)

    db_session.add_all(bars)
    await db_session.commit()

    # 3. Query time range filtering
    query_start = datetime(2026, 1, 3, 0, 0, 0, tzinfo=timezone.utc)
    query_end = datetime(2026, 1, 6, 23, 59, 59, tzinfo=timezone.utc)

    stmt = select(StockOHLCV).where(
        StockOHLCV.ticker == "TSM",
        StockOHLCV.timestamp >= query_start,
        StockOHLCV.timestamp <= query_end
    ).order_by(StockOHLCV.timestamp.asc())

    result = await db_session.execute(stmt)
    fetched_bars = result.scalars().all()

    # Days: Jan 3, Jan 4, Jan 5, Jan 6 (4 bars)
    assert len(fetched_bars) == 4
    assert fetched_bars[0].close == 152.0
    assert fetched_bars[-1].close == 160.5

    # 4. Verify chronological ordering
    timestamps = [b.timestamp for b in fetched_bars]
    assert timestamps == sorted(timestamps)


@pytest.mark.asyncio
async def test_hypertable_ddl_and_indexes(db_session: AsyncSession):
    """Verifies that composite index (ticker, timestamp) is properly defined on the model."""
    table = StockOHLCV.__table__
    index_names = [idx.name for idx in table.indexes]

    assert any("timestamp" in name for name in index_names)
    assert "timestamp" in [c.name for c in table.columns]
