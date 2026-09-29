"""
Company Fundamentals & Financial Statements Repository.
"""
from typing import Optional, List, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc
from app.db.repositories.base import BaseRepository
from app.db.models.fundamental import Fundamental, FinancialStatement
from app.db.models.company import Company


class FundamentalRepository(BaseRepository[Fundamental]):

    def __init__(self, session: AsyncSession):
        super().__init__(Fundamental, session)

    async def get_latest_by_ticker(self, ticker: str) -> Optional[Fundamental]:
        stmt = (
            select(Fundamental)
            .join(Company, Fundamental.company_id == Company.id)
            .where(Company.ticker == ticker.strip().upper())
            .order_by(Fundamental.fiscal_year.desc())
            .limit(1)
        )
        res = await self.session.execute(stmt)
        return res.scalar_one_or_none()

    async def get_statements_by_ticker(
        self,
        ticker: str,
        statement_type: str = "income"
    ) -> List[FinancialStatement]:
        stmt = (
            select(FinancialStatement)
            .join(Company, FinancialStatement.company_id == Company.id)
            .where(
                Company.ticker == ticker.strip().upper(),
                FinancialStatement.statement_type == statement_type.strip().lower()
            )
            .order_by(FinancialStatement.fiscal_year.desc())
        )
        res = await self.session.execute(stmt)
        return list(res.scalars().all())

    async def create_statement(
        self,
        company_id: str,
        statement_type: str,
        fiscal_year: int,
        fiscal_period: str,
        raw_data: Dict[str, Any]
    ) -> FinancialStatement:
        stmt_obj = FinancialStatement(
            company_id=company_id,
            statement_type=statement_type.lower(),
            fiscal_year=fiscal_year,
            fiscal_period=fiscal_period,
            raw_data=raw_data
        )
        self.session.add(stmt_obj)
        await self.session.flush()
        return stmt_obj
