"""
User Portfolio, Position Holdings & Transaction Ledger Repository.
"""
from typing import Optional, List, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete
from sqlalchemy.orm import selectinload
from app.db.repositories.base import BaseRepository
from app.db.models.portfolio import Portfolio, Position, Transaction
from app.db.base import utc_now


class PortfolioRepository(BaseRepository[Portfolio]):

    def __init__(self, session: AsyncSession):
        super().__init__(Portfolio, session)

    async def get_or_create_default(self, user_id: str) -> Portfolio:
        stmt = (
            select(Portfolio)
            .where(Portfolio.user_id == user_id)
            .options(selectinload(Portfolio.positions), selectinload(Portfolio.transactions))
            .limit(1)
        )
        res = await self.session.execute(stmt)
        portfolio = res.scalar_one_or_none()

        if not portfolio:
            portfolio = Portfolio(
                user_id=user_id,
                name="Primary Portfolio",
                description="Default intelligence platform portfolio",
                cash_balance=100000.0,
                total_value=0.0
            )
            self.session.add(portfolio)
            await self.session.flush()
            await self.session.refresh(portfolio, ["positions", "transactions"])

        return portfolio

    async def get_positions(self, portfolio_id: str) -> List[Position]:
        stmt = select(Position).where(Position.portfolio_id == portfolio_id).order_by(Position.ticker.asc())
        res = await self.session.execute(stmt)
        return list(res.scalars().all())

    async def add_transaction(
        self,
        portfolio_id: str,
        ticker: str,
        shares: float,
        price: float,
        tx_type: str = "BUY",
        sector: str = "Information Technology",
        beta: float = 1.0
    ) -> Dict[str, Any]:
        sym = ticker.strip().upper()
        
        # 1. Log transaction
        tx = Transaction(
            portfolio_id=portfolio_id,
            ticker=sym,
            shares=shares,
            price=price,
            transaction_type=tx_type.upper(),
            executed_at=utc_now()
        )
        self.session.add(tx)

        # 2. Update Position
        stmt = select(Position).where(Position.portfolio_id == portfolio_id, Position.ticker == sym)
        res = await self.session.execute(stmt)
        pos = res.scalar_one_or_none()

        if pos:
            if tx_type.upper() == "BUY":
                tot_shares = pos.shares + shares
                tot_cost = (pos.shares * pos.avg_cost) + (shares * price)
                pos.shares = tot_shares
                pos.avg_cost = round(tot_cost / tot_shares, 2)
            elif tx_type.upper() == "SELL":
                pos.shares = max(0.0, pos.shares - shares)
                if pos.shares == 0:
                    await self.session.delete(pos)
        else:
            if tx_type.upper() == "BUY":
                new_pos = Position(
                    portfolio_id=portfolio_id,
                    ticker=sym,
                    shares=shares,
                    avg_cost=price,
                    sector=sector,
                    beta=beta
                )
                self.session.add(new_pos)

        await self.session.flush()
        return {
            "status": "SUCCESS",
            "portfolio_id": portfolio_id,
            "ticker": sym,
            "type": tx_type.upper(),
            "shares": shares,
            "price": price
        }
