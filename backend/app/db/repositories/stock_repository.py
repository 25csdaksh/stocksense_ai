"""
Stock Asset & Metadata Repository.
"""
from typing import Optional, List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from app.db.repositories.base import BaseRepository
from app.db.models.stock import Stock
from app.db.models.company import Company


class StockRepository(BaseRepository[Stock]):

    def __init__(self, session: AsyncSession):
        super().__init__(Stock, session)

    async def get_by_ticker(self, ticker: str) -> Optional[Stock]:
        stmt = (
            select(Stock)
            .where(Stock.ticker == ticker.strip().upper())
            .options(selectinload(Stock.company).selectinload(Company.sector))
        )
        res = await self.session.execute(stmt)
        return res.scalar_one_or_none()

    async def list_universe(self) -> List[Stock]:
        stmt = (
            select(Stock)
            .options(selectinload(Stock.company).selectinload(Company.sector))
            .order_by(Stock.ticker.asc())
        )
        res = await self.session.execute(stmt)
        return list(res.scalars().all())

    async def upsert_stock(
        self,
        ticker: str,
        company_id: str,
        exchange: str = "NASDAQ",
        beta: float = 1.0,
        pe_ratio: Optional[float] = None,
        pb_ratio: Optional[float] = None,
        dividend_yield: Optional[float] = None,
        market_cap: Optional[float] = None,
        week_52_high: Optional[float] = None,
        week_52_low: Optional[float] = None
    ) -> Stock:
        sym = ticker.strip().upper()
        existing = await self.get_by_ticker(sym)
        if existing:
            existing.company_id = company_id
            existing.exchange = exchange
            existing.beta = beta
            existing.pe_ratio = pe_ratio
            existing.pb_ratio = pb_ratio
            existing.dividend_yield = dividend_yield
            existing.market_cap = market_cap
            existing.week_52_high = week_52_high
            existing.week_52_low = week_52_low
            await self.session.flush()
            return existing
        else:
            return await self.create(
                ticker=sym,
                company_id=company_id,
                exchange=exchange,
                beta=beta,
                pe_ratio=pe_ratio,
                pb_ratio=pb_ratio,
                dividend_yield=dividend_yield,
                market_cap=market_cap,
                week_52_high=week_52_high,
                week_52_low=week_52_low
            )
