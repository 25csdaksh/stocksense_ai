"""
TimescaleDB OHLCV Time-Series & Market Indices Repository.
"""
from typing import List, Optional, Dict, Any
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc
from app.db.repositories.base import BaseRepository
from app.db.models.stock import StockOHLCV, MarketIndex
from app.db.base import utc_now


class MarketDataRepository:

    def __init__(self, session: AsyncSession):
        self.session = session

    async def insert_ohlcv_batch(self, bars: List[Dict[str, Any]]) -> int:
        instances = [StockOHLCV(**b) for b in bars]
        self.session.add_all(instances)
        await self.session.flush()
        return len(instances)

    async def get_ohlcv_range(
        self,
        ticker: str,
        limit: int = 180,
        interval: str = "1d"
    ) -> List[StockOHLCV]:
        stmt = (
            select(StockOHLCV)
            .where(
                StockOHLCV.ticker == ticker.strip().upper(),
                StockOHLCV.interval == interval
            )
            .order_by(StockOHLCV.timestamp.desc())
            .limit(limit)
        )
        res = await self.session.execute(stmt)
        bars = list(res.scalars().all())
        bars.reverse()  # Return in chronological order
        return bars

    async def get_latest_bar(self, ticker: str) -> Optional[StockOHLCV]:
        stmt = (
            select(StockOHLCV)
            .where(StockOHLCV.ticker == ticker.strip().upper())
            .order_by(StockOHLCV.timestamp.desc())
            .limit(1)
        )
        res = await self.session.execute(stmt)
        return res.scalar_one_or_none()

    async def list_indices(self) -> List[MarketIndex]:
        stmt = select(MarketIndex).order_by(MarketIndex.symbol.asc())
        res = await self.session.execute(stmt)
        return list(res.scalars().all())

    async def upsert_index(
        self,
        symbol: str,
        name: str,
        price: float,
        change: float,
        change_pct: float
    ) -> MarketIndex:
        stmt = select(MarketIndex).where(MarketIndex.symbol == symbol.strip())
        res = await self.session.execute(stmt)
        existing = res.scalar_one_or_none()

        if existing:
            existing.price = price
            existing.change = change
            existing.change_pct = change_pct
            existing.timestamp = utc_now()
            await self.session.flush()
            return existing
        else:
            idx = MarketIndex(
                symbol=symbol.strip(),
                name=name,
                price=price,
                change=change,
                change_pct=change_pct,
                timestamp=utc_now()
            )
            self.session.add(idx)
            await self.session.flush()
            return idx
