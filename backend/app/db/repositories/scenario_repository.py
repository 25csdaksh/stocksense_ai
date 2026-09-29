"""
Scenario Simulation Reports Repository.
"""
from typing import List, Dict, Any, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc
from app.db.repositories.base import BaseRepository
from app.db.models.scenario import ScenarioReport


class ScenarioRepository(BaseRepository[ScenarioReport]):

    def __init__(self, session: AsyncSession):
        super().__init__(ScenarioReport, session)

    async def save_report(
        self,
        ticker: str,
        scenario_type: str,
        parameters: Dict[str, Any],
        results: Dict[str, Any],
        stock_id: Optional[str] = None
    ) -> ScenarioReport:
        return await self.create(
            ticker=ticker.strip().upper(),
            stock_id=stock_id,
            scenario_type=scenario_type.upper(),
            parameters=parameters,
            results=results
        )

    async def list_by_ticker(self, ticker: str, limit: int = 10) -> List[ScenarioReport]:
        stmt = (
            select(ScenarioReport)
            .where(ScenarioReport.ticker == ticker.strip().upper())
            .order_by(ScenarioReport.created_at.desc())
            .limit(limit)
        )
        res = await self.session.execute(stmt)
        return list(res.scalars().all())
