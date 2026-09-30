"""
MarketMind AI — Strongly Typed Normalized News Intelligence Models.
Phase 6.7: Complete domain models for financial news articles, multi-market feeds,
sentiment annotations, event classifications, impact & relevance scores, and data provenance.
"""
from datetime import datetime, timezone
from enum import Enum
from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field, ConfigDict, model_validator


# =========================================================================
# Domain Enums
# =========================================================================

class NewsCategory(str, Enum):
    MARKET = "MARKET"
    EARNINGS = "EARNINGS"
    CORPORATE_ACTION = "CORPORATE_ACTION"
    M_AND_A = "M_AND_A"
    MANAGEMENT = "MANAGEMENT"
    REGULATORY = "REGULATORY"
    MACRO = "MACRO"
    ECONOMIC = "ECONOMIC"
    PRODUCT = "PRODUCT"
    TECHNOLOGY = "TECHNOLOGY"
    LEGAL = "LEGAL"
    GEOPOLITICAL = "GEOPOLITICAL"
    ANALYST = "ANALYST"
    DIVIDEND = "DIVIDEND"
    BUYBACK = "BUYBACK"
    FUNDRAISING = "FUNDRAISING"
    RISK = "RISK"
    OTHER = "OTHER"


class NewsEventType(str, Enum):
    EARNINGS = "EARNINGS"
    GUIDANCE_CHANGE = "GUIDANCE_CHANGE"
    DIVIDEND = "DIVIDEND"
    BUYBACK = "BUYBACK"
    MERGER = "MERGER"
    ACQUISITION = "ACQUISITION"
    M_AND_A = "M_AND_A"
    SPINOFF = "SPINOFF"
    MANAGEMENT_CHANGE = "MANAGEMENT_CHANGE"
    REGULATORY_ACTION = "REGULATORY_ACTION"
    LEGAL_EVENT = "LEGAL_EVENT"
    PRODUCT_LAUNCH = "PRODUCT_LAUNCH"
    PARTNERSHIP = "PARTNERSHIP"
    FUNDRAISING = "FUNDRAISING"
    CREDIT_EVENT = "CREDIT_EVENT"
    BANKRUPTCY = "BANKRUPTCY"
    RATING_CHANGE = "RATING_CHANGE"
    MACRO_EVENT = "MACRO_EVENT"
    OTHER = "OTHER"
    UNKNOWN = "UNKNOWN"



class SentimentLabel(str, Enum):
    POSITIVE = "POSITIVE"
    NEUTRAL = "NEUTRAL"
    NEGATIVE = "NEGATIVE"
    MIXED = "MIXED"
    BULLISH = "BULLISH"
    BEARISH = "BEARISH"
    UNKNOWN = "UNKNOWN"


class ImpactDirection(str, Enum):
    POSITIVE = "POSITIVE"
    NEGATIVE = "NEGATIVE"
    NEUTRAL = "NEUTRAL"
    MIXED = "MIXED"
    UNKNOWN = "UNKNOWN"


class ImpactHorizon(str, Enum):
    INTRADAY = "INTRADAY"
    SHORT_TERM = "SHORT_TERM"
    MEDIUM_TERM = "MEDIUM_TERM"
    LONG_TERM = "LONG_TERM"
    UNKNOWN = "UNKNOWN"


class ImpactScope(str, Enum):
    STOCK = "STOCK"
    SECTOR = "SECTOR"
    MARKET = "MARKET"
    MACRO = "MACRO"


class NewsDataSource(str, Enum):
    DEMO = "DEMO"
    INDIAN_PROVIDER = "INDIAN_PROVIDER"
    US_PROVIDER = "US_PROVIDER"
    REUTERS = "REUTERS"
    BLOOMBERG = "BLOOMBERG"
    YFINANCE = "YFINANCE"
    ECONOMIC_TIMES = "ECONOMIC_TIMES"
    FINANCIAL_EXPRESS = "FINANCIAL_EXPRESS"
    MINT = "MINT"
    SEC_EDGAR = "SEC_EDGAR"
    OTHER = "OTHER"


class NewsDataStatus(str, Enum):
    DEMO = "DEMO"
    LIVE = "LIVE"
    STALE = "STALE"
    UNAVAILABLE = "UNAVAILABLE"


# =========================================================================
# Normalized News Article Model
# =========================================================================

class NewsArticleData(BaseModel):
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    id: str
    headline: str
    title: Optional[str] = None  # Backward-compatible mirror for headline
    summary: str
    content: Optional[str] = None
    url: Optional[str] = None
    source: str
    author: Optional[str] = None
    published_at: str
    updated_at: Optional[str] = None
    language: str = "en"
    country: str = "IN"
    market: str = "INDIA"  # INDIA, US, GLOBAL
    ticker: Optional[str] = None  # Primary ticker
    symbols: List[str] = Field(default_factory=list)
    companies: List[str] = Field(default_factory=list)
    sectors: List[str] = Field(default_factory=list)
    sector: Optional[str] = None
    topics: List[str] = Field(default_factory=list)
    category: NewsCategory = NewsCategory.MARKET
    event_type: NewsEventType = NewsEventType.OTHER
    event_confidence: float = 0.85
    classification_source: str = "RULE_BASED_NLP"
    sentiment: SentimentLabel = SentimentLabel.NEUTRAL
    sentiment_label: str = "NEUTRAL"
    sentiment_score: float = Field(default=0.0, ge=-1.0, le=1.0)
    sentiment_confidence: float = Field(default=0.80, ge=0.0, le=1.0)
    relevance_score: float = Field(default=0.80, ge=0.0, le=1.0)
    impact_score: float = Field(default=0.50, ge=0.0, le=1.0)
    impact_direction: ImpactDirection = ImpactDirection.NEUTRAL
    impact_horizon: ImpactHorizon = ImpactHorizon.SHORT_TERM
    impact_scope: ImpactScope = ImpactScope.STOCK
    data_source: NewsDataSource = NewsDataSource.DEMO
    data_status: NewsDataStatus = NewsDataStatus.DEMO
    content_hash: Optional[str] = None

    @model_validator(mode="after")
    def sync_legacy_and_derived_fields(self) -> "NewsArticleData":
        if not self.title:
            self.title = self.headline
        elif not self.headline:
            self.headline = self.title

        if not self.ticker and self.symbols:
            self.ticker = self.symbols[0]
        elif self.ticker and self.ticker not in self.symbols:
            self.symbols.insert(0, self.ticker)

        if not self.sector and self.sectors:
            self.sector = self.sectors[0]
        elif self.sector and self.sector not in self.sectors:
            self.sectors.append(self.sector)

        if self.sentiment_label != self.sentiment.value:
            self.sentiment_label = self.sentiment.value

        return self

    def __contains__(self, item: Any) -> bool:
        return hasattr(self, item) or item in self.__dict__

    def __iter__(self):
        return iter(self.model_dump())

    def keys(self):
        return self.model_dump().keys()

    def values(self):
        return self.model_dump().values()

    def items(self):
        return self.model_dump().items()

    def __getitem__(self, item: str) -> Any:
        if hasattr(self, item):
            val = getattr(self, item)
            if hasattr(val, "value"):
                return val.value
            return val
        data = self.model_dump()
        if item in data:
            return data[item]
        raise KeyError(item)

    def get(self, item: str, default: Any = None) -> Any:
        try:
            return self[item]
        except KeyError:
            return default


# =========================================================================
# Sentiment Summary & Aggregation Models
# =========================================================================

class SectorSentimentSummary(BaseModel):
    sector: str
    article_count: int = 0
    positive_count: int = 0
    neutral_count: int = 0
    negative_count: int = 0
    mixed_count: int = 0
    positive_pct: float = 0.0
    neutral_pct: float = 0.0
    negative_pct: float = 0.0
    average_sentiment_score: float = 0.0
    sentiment_trend: str = "STABLE"  # IMPROVING, DETERIORATING, STABLE


class NewsSentimentAggregation(BaseModel):
    ticker: Optional[str] = None
    sector: Optional[str] = None
    market: Optional[str] = None
    overall_sentiment: str = "NEUTRAL"
    average_sentiment_score: float = 0.0
    total_articles: int = 0
    positive_count: int = 0
    neutral_count: int = 0
    negative_count: int = 0
    mixed_count: int = 0
    sentiment_trend: str = "STABLE"
    sector_breakdown: List[SectorSentimentSummary] = Field(default_factory=list)
    news_items: List[NewsArticleData] = Field(default_factory=list)
    data_source: NewsDataSource = NewsDataSource.DEMO
    data_status: NewsDataStatus = NewsDataStatus.DEMO
    generated_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

    def __contains__(self, item: Any) -> bool:
        return hasattr(self, item) or item in self.__dict__

    def __iter__(self):
        return iter(self.model_dump())

    def keys(self):
        return self.model_dump().keys()

    def values(self):
        return self.model_dump().values()

    def items(self):
        return self.model_dump().items()

    def __getitem__(self, item: str) -> Any:
        if hasattr(self, item):
            val = getattr(self, item)
            if hasattr(val, "value"):
                return val.value
            return val
        data = self.model_dump()
        if item in data:
            return data[item]
        raise KeyError(item)

    def get(self, item: str, default: Any = None) -> Any:
        try:
            return self[item]
        except KeyError:
            return default


# =========================================================================
# News Timeline Item Model
# =========================================================================

class NewsTimelineEvent(BaseModel):
    article_id: str
    timestamp: str
    headline: str
    ticker: Optional[str] = None
    event_type: NewsEventType = NewsEventType.OTHER
    sentiment: SentimentLabel = SentimentLabel.NEUTRAL
    sentiment_score: float = 0.0
    impact_score: float = 0.5
    impact_direction: ImpactDirection = ImpactDirection.NEUTRAL
    impact_horizon: ImpactHorizon = ImpactHorizon.SHORT_TERM
    source: str
    url: Optional[str] = None
    relevance_note: str = "Potentially relevant event near timestamp"
