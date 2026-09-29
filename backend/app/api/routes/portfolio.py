"""
Portfolio Holdings, Risk Summary & Stress Testing API Routes.
"""
from typing import Dict, Any, List
from fastapi import APIRouter, Body, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.schemas.portfolio import PortfolioSummary, TransactionCreate, PortfolioStressTestRequest
from app.services.portfolio_service import portfolio_service
from app.db.session import get_db_session

router = APIRouter(prefix="/portfolio", tags=["Portfolio Management"])


@router.get("", response_model=Dict[str, Any])
async def get_portfolio_summary(db: AsyncSession = Depends(get_db_session)):
    """Retrieves current portfolio holdings, market value, weighted beta, and daily 95% VaR."""
    return await portfolio_service.get_portfolio_summary(db=db)


@router.post("/transactions")
async def add_portfolio_transaction(
    tx: TransactionCreate,
    db: AsyncSession = Depends(get_db_session)
):
    """Ingests a BUY or SELL transaction and recalculates cost basis."""
    return await portfolio_service.add_transaction(
        ticker=tx.ticker,
        shares=tx.shares,
        price=tx.price,
        tx_type=tx.transaction_type,
        db=db
    )


@router.post("/stress-test")
async def stress_test_portfolio(req: PortfolioStressTestRequest = Body(default=None)):
    """Simulates multi-crisis historical drawdowns on current or custom portfolio holdings."""
    holdings_dict = [h.model_dump() for h in req.holdings] if req and req.holdings else None
    return await portfolio_service.stress_test_portfolio(holdings=holdings_dict)
