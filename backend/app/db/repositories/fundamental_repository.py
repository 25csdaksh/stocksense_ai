"""
MarketMind AI — Company Fundamentals & Financial Statements Repository.
Phase 6.6: Multi-period persistence, deduplication, and historical statements.
"""
from typing import Optional, List, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc, and_
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
            .order_by(Fundamental.fiscal_year.desc(), Fundamental.fiscal_quarter.desc().nullslast())
            .limit(1)
        )
        res = await self.session.execute(stmt)
        return res.scalar_one_or_none()

    async def get_history_by_ticker(self, ticker: str, limit: int = 10) -> List[Fundamental]:
        stmt = (
            select(Fundamental)
            .join(Company, Fundamental.company_id == Company.id)
            .where(Company.ticker == ticker.strip().upper())
            .order_by(Fundamental.fiscal_year.desc(), Fundamental.fiscal_quarter.desc().nullslast())
            .limit(limit)
        )
        res = await self.session.execute(stmt)
        return list(res.scalars().all())

    async def get_statements_by_ticker(
        self,
        ticker: str,
        statement_type: str = "income",
        fiscal_period: Optional[str] = None
    ) -> List[FinancialStatement]:
        conditions = [
            Company.ticker == ticker.strip().upper(),
            FinancialStatement.statement_type == statement_type.strip().lower()
        ]
        if fiscal_period:
            conditions.append(FinancialStatement.fiscal_period == fiscal_period.strip().upper())

        stmt = (
            select(FinancialStatement)
            .join(Company, FinancialStatement.company_id == Company.id)
            .where(and_(*conditions))
            .order_by(FinancialStatement.fiscal_year.desc())
        )
        res = await self.session.execute(stmt)
        return list(res.scalars().all())

    async def upsert_fundamental(
        self,
        company_id: str,
        fiscal_year: int,
        fiscal_quarter: Optional[int] = None,
        **kwargs
    ) -> Fundamental:
        """Finds existing fundamental record for the same period or creates a new one."""
        conditions = [
            Fundamental.company_id == company_id,
            Fundamental.fiscal_year == fiscal_year,
        ]
        if fiscal_quarter is not None:
            conditions.append(Fundamental.fiscal_quarter == fiscal_quarter)
        else:
            conditions.append(Fundamental.fiscal_quarter.is_(None))

        stmt = select(Fundamental).where(and_(*conditions))
        res = await self.session.execute(stmt)
        existing = res.scalar_one_or_none()

        if existing:
            for k, v in kwargs.items():
                if hasattr(existing, k) and v is not None:
                    setattr(existing, k, v)
            await self.session.flush()
            return existing
        else:
            new_obj = Fundamental(
                company_id=company_id,
                fiscal_year=fiscal_year,
                fiscal_quarter=fiscal_quarter,
                **kwargs
            )
            self.session.add(new_obj)
            await self.session.flush()
            return new_obj

    async def upsert_statement(
        self,
        company_id: str,
        statement_type: str,
        fiscal_year: int,
        fiscal_period: str,
        raw_data: Dict[str, Any]
    ) -> FinancialStatement:
        """Finds existing financial statement or creates a new one."""
        stmt = select(FinancialStatement).where(
            and_(
                FinancialStatement.company_id == company_id,
                FinancialStatement.statement_type == statement_type.lower(),
                FinancialStatement.fiscal_year == fiscal_year,
                FinancialStatement.fiscal_period == fiscal_period.upper()
            )
        )
        res = await self.session.execute(stmt)
        existing = res.scalar_one_or_none()

        if existing:
            existing.raw_data = raw_data
            await self.session.flush()
            return existing
        else:
            new_stmt = FinancialStatement(
                company_id=company_id,
                statement_type=statement_type.lower(),
                fiscal_year=fiscal_year,
                fiscal_period=fiscal_period.upper(),
                raw_data=raw_data
            )
            self.session.add(new_stmt)
            await self.session.flush()
            return new_stmt

    async def create_statement(
        self,
        company_id: str,
        statement_type: str,
        fiscal_year: int,
        fiscal_period: str,
        raw_data: Dict[str, Any]
    ) -> FinancialStatement:
        return await self.upsert_statement(
            company_id=company_id,
            statement_type=statement_type,
            fiscal_year=fiscal_year,
            fiscal_period=fiscal_period,
            raw_data=raw_data
        )
