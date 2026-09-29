"""
Portfolio Risk & Watchlist Schemas.
"""
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field


class PortfolioPosition(BaseModel):
    ticker: str
    shares: float
    price: float
    sector: str = "Information Technology"
    beta: float = 1.0


class PortfolioSummary(BaseModel):
    total_value: float
    weighted_beta: float
    daily_var_95_pct: float
    positions_count: int
    positions: List[PortfolioPosition]


class PortfolioStressTestRequest(BaseModel):
    holdings: List[PortfolioPosition]


class TransactionCreate(BaseModel):
    ticker: str
    shares: float
    price: float
    transaction_type: str = "BUY"  # BUY, SELL


class WatchlistItem(BaseModel):
    ticker: str
    added_at: str
    target_price: Optional[float] = None
    notes: Optional[str] = None
