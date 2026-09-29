"""
Stock Quotes & Historical OHLCV Schemas.
"""
from typing import List, Optional
from pydantic import BaseModel


class StockQuoteResponse(BaseModel):
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
    market_cap: Optional[float] = None
    pe_ratio: Optional[float] = None
    week_52_high: float
    week_52_low: float
    is_synthetic: bool = False
    data_source: str
    timestamp: str


class OHLCVBarSchema(BaseModel):
    time: str
    open: float
    high: float
    low: float
    close: float
    volume: float
    sma_20: Optional[float] = None
    sma_50: Optional[float] = None
    ema_20: Optional[float] = None
    rsi_14: Optional[float] = None
    vwap: Optional[float] = None


class HistoricalOHLCVResponse(BaseModel):
    ticker: str
    timeframe: str
    interval: str
    bars: List[OHLCVBarSchema]
    is_synthetic: bool = False
    total_bars: int
