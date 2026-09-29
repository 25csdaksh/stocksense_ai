"""
Market Data & OHLCV Pydantic Schemas.
"""
from typing import List, Optional
from pydantic import BaseModel, Field


class AssetResponse(BaseModel):
    ticker: str
    name: str
    sector: Optional[str] = "General"
    industry: Optional[str] = None
    asset_type: str = "EQUITY"
    market_cap: Optional[float] = None
    pe_ratio: Optional[float] = None
    pb_ratio: Optional[float] = None
    beta: Optional[float] = 1.0
    dividend_yield: Optional[float] = 0.0


class MarketQuoteResponse(BaseModel):
    ticker: str
    name: str
    price: float
    change: float
    change_pct: float
    open: float
    high: float
    low: float
    previous_close: float
    volume: float
    avg_volume: float
    market_cap: Optional[float] = None
    pe_ratio: Optional[float] = None
    week_52_high: float
    week_52_low: float
    is_synthetic: bool = False
    data_source: str = "EXCHANGE_FEED"
    timestamp: str


class OHLCVBar(BaseModel):
    time: str
    open: float
    high: float
    low: float
    close: float
    volume: float
    vwap: Optional[float] = None
    sma_20: Optional[float] = None
    sma_50: Optional[float] = None
    ema_20: Optional[float] = None
    rsi_14: Optional[float] = None


class HistoricalDataResponse(BaseModel):
    ticker: str
    interval: str
    range: str
    bars: List[OHLCVBar]
    is_synthetic: bool = False
    total_bars: int


class SectorItem(BaseModel):
    sector: str
    performance_pct: float
    momentum_score: float
    top_stock: str
    market_cap_weight: float


class SectorPerformanceResponse(BaseModel):
    sectors: List[SectorItem]
    timestamp: str


class MarketIndexItem(BaseModel):
    symbol: str
    name: str
    price: float
    change: float
    change_pct: float


class MarketOverviewResponse(BaseModel):
    indices: List[MarketIndexItem]
    top_gainers: List[MarketQuoteResponse]
    top_losers: List[MarketQuoteResponse]
    most_active: List[MarketQuoteResponse]
    market_regime: str  # 'BULLISH_EXPANSION', 'VOLATILITY_COMPRESSION', 'RISK_OFF'
    timestamp: str
