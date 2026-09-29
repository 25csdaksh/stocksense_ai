"""
Portfolio Holdings, Risk Summary & Stress Testing API Routes.
"""
from typing import Dict, Any, List
from fastapi import APIRouter, Body
from app.schemas.portfolio import PortfolioSummary, TransactionCreate, PortfolioStressTestRequest
from app.services.portfolio_service import portfolio_service

router = APIRouter(prefix="/portfolio", tags=["Portfolio Management"])


@router.get("", response_model=Dict[str, Any])
async def get_portfolio_summary():
    """Retrieves current portfolio holdings, market value, weighted beta, and daily 95% VaR."""
    return await portfolio_service.get_portfolio_summary()


@router.post("/transactions")
async def add_portfolio_transaction(tx: TransactionCreate):
    """Ingests a BUY or SELL transaction and recalculates cost basis."""
    return await portfolio_service.add_transaction(
        ticker=tx.ticker,
        shares=tx.shares,
        price=tx.price,
        tx_type=tx.transaction_type
    )


@router.post("/stress-test")
async def stress_test_portfolio(req: PortfolioStressTestRequest = Body(default=None)):
    """Simulates multi-crisis historical drawdowns on current or custom portfolio holdings."""
    holdings_dict = [h.model_dump() for h in req.holdings] if req and req.holdings else None
    return await portfolio_service.stress_test_portfolio(holdings=holdings_dict)
