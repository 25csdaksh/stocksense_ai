"""
Portfolio Risk & Multi-Asset Stress Testing Endpoints.
"""
from typing import List, Dict, Any
from pydantic import BaseModel, Field
from fastapi import APIRouter
from core.guardrails import FINANCIAL_DISCLAIMER_MD

import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", "ml-engine")))
from engine import ml_engine

router = APIRouter(prefix="/portfolio", tags=["Portfolio Risk & Stress Testing"])


class HoldingItem(BaseModel):
    ticker: str
    shares: float
    price: float
    sector: str = "Information Technology"
    beta: float = 1.0


class PortfolioStressRequest(BaseModel):
    holdings: List[HoldingItem] = Field(
        default=[
            HoldingItem(ticker="AAPL", shares=50, price=224.50, sector="Information Technology", beta=1.12),
            HoldingItem(ticker="NVDA", shares=80, price=121.40, sector="Information Technology", beta=1.68),
            HoldingItem(ticker="MSFT", shares=40, price=428.10, sector="Information Technology", beta=0.95),
            HoldingItem(ticker="JPM", shares=60, price=218.40, sector="Financials", beta=1.08),
            HoldingItem(ticker="SPY", shares=30, price=570.20, sector="Index ETF", beta=1.00)
        ]
    )


@router.post("/stress-test")
async def stress_test_portfolio(req: PortfolioStressRequest):
    """Stress tests custom multi-asset portfolio against 2008 GFC, 2020 COVID, 2022 Rates, and 2000 Dot-com."""
    holdings_dict = [h.dict() for h in req.holdings]
    results = ml_engine.historical_stress_tester.stress_test_portfolio(holdings_dict)
    results["disclaimer"] = FINANCIAL_DISCLAIMER_MD.strip()
    return results
