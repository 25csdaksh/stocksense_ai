from typing import List, Optional, Any
from pydantic import BaseModel


class MarketIndexItem(BaseModel):
    symbol: str
    name: str
    price: float
    change: float
    change_pct: float


class SectorItem(BaseModel):
    sector: str
    performance_pct: float
    momentum_score: float
    top_stock: str
    market_cap_weight: float


class MarketOverviewResponse(BaseModel):
    indices: List[MarketIndexItem]
    top_gainers: List[Any] = []
    top_losers: List[Any] = []
    market_regime: str
    timestamp: str
