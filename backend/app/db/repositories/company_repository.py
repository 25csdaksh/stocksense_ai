"""
Sector & Company Directory Repository.
"""
from typing import Optional, List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from app.db.repositories.base import BaseRepository
from app.db.models.company import Company, Sector


class CompanyRepository(BaseRepository[Company]):

    def __init__(self, session: AsyncSession):
        super().__init__(Company, session)

    async def get_by_ticker(self, ticker: str) -> Optional[Company]:
        stmt = (
            select(Company)
            .where(Company.ticker == ticker.strip().upper())
            .options(selectinload(Company.sector))
        )
        res = await self.session.execute(stmt)
        return res.scalar_one_or_none()

    async def list_sectors(self) -> List[Sector]:
        stmt = select(Sector).order_by(Sector.performance_pct.desc())
        res = await self.session.execute(stmt)
        return list(res.scalars().all())

    async def get_sector_by_code(self, code: str) -> Optional[Sector]:
        stmt = select(Sector).where(Sector.code == code.strip().upper())
        res = await self.session.execute(stmt)
        return res.scalar_one_or_none()

    async def create_sector(
        self,
        name: str,
        code: str,
        performance_pct: float = 0.0,
        momentum_score: float = 50.0,
        market_cap_weight: float = 0.0
    ) -> Sector:
        sector = Sector(
            name=name,
            code=code.upper(),
            performance_pct=performance_pct,
            momentum_score=momentum_score,
            market_cap_weight=market_cap_weight
        )
        self.session.add(sector)
        await self.session.flush()
        return sector
