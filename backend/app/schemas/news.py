"""
Financial News & NLP Sentiment Schemas.
Phase 6.7: Schemas supporting breaking news feeds, structured event classifications,
multi-horizon impact, aggregate sentiment distributions, and health telemetry.
"""
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field
from app.providers.news.models import (
    NewsArticleData,
    NewsSentimentAggregation,
    SectorSentimentSummary,
    NewsTimelineEvent,
    NewsCategory,
    NewsEventType,
    SentimentLabel,
    ImpactDirection,
    ImpactHorizon,
    ImpactScope,
    NewsDataSource,
    NewsDataStatus,
)


class NewsArticleSchema(BaseModel):
    id: str
    ticker: Optional[str] = None
    title: str
    headline: Optional[str] = None
    summary: str
    content: Optional[str] = None
    source: str
    url: Optional[str] = None
    published_at: str
    sentiment_label: str = "NEUTRAL"
    sentiment_score: float = 0.0
    impact_score: float = 0.5
    category: Optional[str] = "MARKET"
    event_type: Optional[str] = "OTHER"
    impact_direction: Optional[str] = "NEUTRAL"
    impact_horizon: Optional[str] = "SHORT_TERM"
    impact_scope: Optional[str] = "STOCK"
    relevance_score: Optional[float] = 0.8
    sector: Optional[str] = None
    symbols: Optional[List[str]] = None
    data_source: Optional[str] = "DEMO"
    data_status: Optional[str] = "DEMO"


class NewsSentimentSummary(BaseModel):
    ticker: str
    overall_sentiment: str
    average_sentiment_score: float
    news_items: List[NewsArticleSchema]


class NewsHealthTelemetry(BaseModel):
    provider_status: str
    articles_processed: int
    articles_failed: int
    duplicates_prevented: int
    provider_failures: int
    missing_symbols: int
    classification_failures: int
    sentiment_failures: int
    last_successful_run: str
    freshness: str
