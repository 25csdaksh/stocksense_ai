"""
MarketMind AI — Live Market Data Provider Normalized Models & Data Provenance Schemas.
Phase 6.1: Production-ready Pydantic schemas for Indian & US Markets, OHLCV candles, indices, and provider health.
"""
from enum import Enum
from typing import List, Optional, Dict, Any
from datetime import datetime, timezone
from pydantic import BaseModel, Field, ConfigDict


class DataStatus(str, Enum):
    """Data provenance status flag."""
    LIVE = "LIVE"
    DELAYED = "DELAYED"
    HISTORICAL = "HISTORICAL"
    DEMO = "DEMO"
    MODEL_DERIVED = "MODEL_DERIVED"


class ProviderStatus(str, Enum):
    """Health and operational status of a market data provider."""
    LIVE = "LIVE"
    DEMO = "DEMO"
    UNAVAILABLE = "UNAVAILABLE"
    CONFIGURATION_REQUIRED = "CONFIGURATION_REQUIRED"


class MarketSessionState(str, Enum):
    """Trading session state."""
    REGULAR = "REGULAR"
    PRE_MARKET = "PRE_MARKET"
    POST_MARKET = "POST_MARKET"
    CLOSED = "CLOSED"


class MarketType(str, Enum):
    """Market region categorization."""
    IN = "IN"          # Indian Markets (NSE/BSE)
    US = "US"          # United States Markets (NYSE/NASDAQ)
    GLOBAL = "GLOBAL"  # Cross-market benchmark


class NormalizedQuote(BaseModel):
    """
    Standardized, normalized market quote snapshot with full data provenance.
    Supports both new Normalized Quote contract and legacy frontend/API schemas.
    """
    model_config = ConfigDict(populate_by_name=True)

    symbol: str = Field(description="Canonical ticker symbol (e.g., RELIANCE.NS, AAPL)")
    ticker: str = Field(description="Display ticker alias for backward compatibility")
    name: str = Field(description="Company or index full legal/display name")
    exchange: str = Field(description="Exchange name: NSE, BSE, NASDAQ, NYSE")
    currency: str = Field(default="USD", description="Quotation currency: INR, USD")
    price: float = Field(description="Current / Last Traded Price (LTP)")
    open: float = Field(description="Day opening price")
    high: float = Field(description="Day high price")
    low: float = Field(description="Day low price")
    previous_close: float = Field(description="Previous session closing price")
    change: float = Field(description="Absolute price change vs previous close")
    change_percent: float = Field(description="Percentage price change (e.g., +1.25%)")
    change_pct: float = Field(description="Alias for change_percent for backward compatibility")
    volume: float = Field(default=0.0, description="Session accumulated traded volume")
    market_cap: Optional[float] = Field(default=None, description="Market Capitalization")
    pe_ratio: Optional[float] = Field(default=None, description="Trailing Price-to-Earnings ratio")
    week_52_high: float = Field(description="52-week rolling highest price")
    week_52_low: float = Field(description="52-week rolling lowest price")
    market_status: str = Field(default="REGULAR", description="Current exchange session status")
    data_source: str = Field(description="Original feed provider name")
    data_status: DataStatus = Field(default=DataStatus.DEMO, description="Provenance status flag")
    is_synthetic: bool = Field(default=False, description="Explicit flag for synthetic/mock data")
    timestamp: str = Field(description="ISO-8601 UTC timestamp of the quote observation")

    def __getitem__(self, item: str) -> Any:
        try:
            return getattr(self, item)
        except AttributeError:
            raise KeyError(item)

    def get(self, item: str, default: Any = None) -> Any:
        return getattr(self, item, default)

    def __contains__(self, item: str) -> bool:
        return hasattr(self, item)

    def keys(self):
        return self.model_dump().keys()

    def values(self):
        return self.model_dump().values()

    def items(self):
        return self.model_dump().items()


class HistoricalCandle(BaseModel):
    """
    Standardized OHLCV candlestick bar for charting, timeseries DB, and technical analytics.
    """
    model_config = ConfigDict(populate_by_name=True)

    timestamp: datetime = Field(description="Bar datetime in UTC")
    time: str = Field(description="Formatted date string (YYYY-MM-DD or ISO-8601)")
    open: float = Field(description="Bar opening price")
    high: float = Field(description="Bar highest price")
    low: float = Field(description="Bar lowest price")
    close: float = Field(description="Bar closing price")
    volume: float = Field(description="Traded volume in units")
    adjusted_close: Optional[float] = Field(default=None, description="Corporate-actions adjusted close")
    symbol: Optional[str] = Field(default=None, description="Symbol for the candle")
    exchange: Optional[str] = Field(default=None, description="Exchange code")
    currency: Optional[str] = Field(default=None, description="Currency")
    data_source: Optional[str] = Field(default=None, description="Provenance data feed")
    data_status: DataStatus = Field(default=DataStatus.DEMO, description="Data status")

    # Technical Indicators (Optional enrichments)
    sma_20: Optional[float] = Field(default=None, description="20-day Simple Moving Average")
    sma_50: Optional[float] = Field(default=None, description="50-day Simple Moving Average")
    ema_20: Optional[float] = Field(default=None, description="20-day Exponential Moving Average")
    rsi_14: Optional[float] = Field(default=None, description="14-period Relative Strength Index")
    vwap: Optional[float] = Field(default=None, description="Volume Weighted Average Price")


class HistoricalDataResponse(BaseModel):
    """
    Historical time-series response wrapper with technical indicator overlays.
    """
    symbol: str
    ticker: str
    timeframe: str
    interval: str
    currency: str = "USD"
    bars: List[HistoricalCandle]
    total_bars: int
    data_source: str
    data_status: DataStatus = DataStatus.DEMO
    is_synthetic: bool = False

    def __getitem__(self, item: str) -> Any:
        try:
            return getattr(self, item)
        except AttributeError:
            raise KeyError(item)

    def get(self, item: str, default: Any = None) -> Any:
        return getattr(self, item, default)

    def __contains__(self, item: str) -> bool:
        return hasattr(self, item)

    def keys(self):
        return self.model_dump().keys()

    def values(self):
        return self.model_dump().values()

    def items(self):
        return self.model_dump().items()


class MarketIndexQuote(BaseModel):
    """
    Benchmark market index quote (e.g. NIFTY 50, SENSEX, S&P 500, NASDAQ).
    """
    symbol: str = Field(description="Index identifier: ^NSEI, ^BSESN, ^GSPC, ^IXIC")
    name: str = Field(description="Index display name (e.g. NIFTY 50, S&P 500)")
    exchange: str = Field(description="Host exchange: NSE, BSE, NASDAQ, NYSE, GLOBAL")
    price: float = Field(description="Current index level")
    change: float = Field(description="Point change")
    change_pct: float = Field(description="Percentage change")
    currency: str = Field(default="INR", description="Currency of index")
    timestamp: str = Field(description="Observation ISO-8601 UTC timestamp")
    data_source: str = Field(default="MARKETMIND_INDEX_ENGINE")
    data_status: DataStatus = Field(default=DataStatus.DEMO)


class CompanyFundamentals(BaseModel):
    """
    Company fundamental metrics snapshot.
    """
    symbol: str
    name: str
    market_cap: Optional[float] = None
    pe_ratio: Optional[float] = None
    pb_ratio: Optional[float] = None
    dividend_yield: Optional[float] = None
    beta: Optional[float] = 1.0
    eps: Optional[float] = None
    currency: str = "USD"
    data_source: str = "FINANCIAL_FEED"
    data_status: DataStatus = DataStatus.DEMO


class CompanyProfile(BaseModel):
    """
    Company metadata and business profile.
    """
    symbol: str
    name: str
    exchange: str
    sector: str
    industry: Optional[str] = None
    description: Optional[str] = None
    currency: str = "USD"
    data_source: str = "MARKETMIND_REGISTRY"


class MarketNewsItem(BaseModel):
    """
    Market financial news record.
    """
    id: str
    title: str
    summary: str
    source: str
    url: Optional[str] = None
    published_at: str
    sentiment: Optional[str] = "NEUTRAL"
    sentiment_score: Optional[float] = 0.0
    symbols: List[str] = []


class MarketSessionStatus(BaseModel):
    """
    Real-time market session status for a specific exchange/market.
    """
    market: str = Field(description="Market region code: IN, US, GLOBAL")
    exchange: str = Field(description="Exchange code: NSE, BSE, NASDAQ, NYSE")
    is_open: bool = Field(description="Whether the exchange is currently open for regular trading")
    session_state: MarketSessionState = Field(description="Current session state: REGULAR, PRE_MARKET, POST_MARKET, CLOSED")
    session_start: str = Field(description="Session start time in local market timezone (HH:MM)")
    session_end: str = Field(description="Session close time in local market timezone (HH:MM)")
    timezone: str = Field(description="IANA Timezone string (e.g., Asia/Kolkata, America/New_York)")
    current_time_local: str = Field(description="Current time formatted in market timezone")
    next_open: str = Field(description="Next scheduled market open timestamp (ISO-8601 UTC)")
    next_close: str = Field(description="Next scheduled market close timestamp (ISO-8601 UTC)")


class ProviderHealth(BaseModel):
    """
    Provider telemetry, status, latency and operational health report.
    """
    provider_name: str = Field(description="Class / identifier name of the provider adapter")
    market: str = Field(description="Supported market: NSE, BSE, US, GLOBAL")
    status: ProviderStatus = Field(description="Operational status: LIVE, DEMO, UNAVAILABLE, CONFIGURATION_REQUIRED")
    last_successful_request: Optional[str] = Field(default=None, description="ISO timestamp of last successful fetch")
    latency_ms: Optional[float] = Field(default=None, description="Last roundtrip latency in milliseconds")
    configuration_status: str = Field(description="Human-readable configuration message")
    error_message: Optional[str] = Field(default=None, description="Last encountered error if any")
    requests_remaining: Optional[int] = Field(default=None, description="Rate limit remaining calls")
    rate_limit_status: str = Field(default="NORMAL", description="Rate limiter status: NORMAL, WARNING, THROTTLED")
