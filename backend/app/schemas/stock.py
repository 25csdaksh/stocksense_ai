"""
Stock Quotes & Historical OHLCV Schemas.
Phase 6.1: Enriched schemas with data provenance, exchange code, currency, and backward compatibility.
"""
from typing import List, Optional
from pydantic import BaseModel, Field


class StockQuoteResponse(BaseModel):
    ticker: str
    symbol: Optional[str] = None
    name: str
    exchange: Optional[str] = None
    currency: Optional[str] = "USD"
    price: float
    change: float
    change_pct: float
    change_percent: Optional[float] = None
    open: float
    high: float
    low: float
    previous_close: float
    volume: float
    market_cap: Optional[float] = None
    pe_ratio: Optional[float] = None
    week_52_high: float
    week_52_low: float
    is_synthetic: bool = False
    data_source: str
    data_status: Optional[str] = "DEMO"
    market_status: Optional[str] = "REGULAR"
    timestamp: str


class OHLCVBarSchema(BaseModel):
    time: str
    open: float
    high: float
    low: float
    close: float
    volume: float
    adjusted_close: Optional[float] = None
    sma_20: Optional[float] = None
    sma_50: Optional[float] = None
    ema_20: Optional[float] = None
    rsi_14: Optional[float] = None
    vwap: Optional[float] = None


class HistoricalOHLCVResponse(BaseModel):
    ticker: str
    symbol: Optional[str] = None
    timeframe: str
    interval: str
    currency: Optional[str] = "USD"
    bars: List[OHLCVBarSchema]
    is_synthetic: bool = False
    data_source: Optional[str] = "FEED"
    data_status: Optional[str] = "DEMO"
    total_bars: int
