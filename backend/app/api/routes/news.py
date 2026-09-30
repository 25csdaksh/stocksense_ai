"""
Financial News Feed & Real-Time Sentiment API Routes.
Phase 6.7: High-performance endpoints for market-wide news, ticker intelligence,
sector streams, event timelines, aggregate sentiment metrics, and data quality health.
"""
from typing import List, Dict, Any, Optional
from fastapi import APIRouter, Query, Path
from app.schemas.news import (
    NewsSentimentSummary,
    NewsArticleSchema,
    NewsHealthTelemetry,
    NewsSentimentAggregation,
    NewsTimelineEvent,
)
from app.services.news_service import news_service
from app.services.news_collector import news_collector

router = APIRouter(prefix="/news", tags=["Financial News & Sentiment"])


@router.get("/health", response_model=NewsHealthTelemetry)
async def get_news_health_telemetry():
    """Returns data quality metrics, provider health, and collection pipeline telemetry."""
    return news_collector.get_telemetry()


@router.get("/market", response_model=List[NewsArticleSchema])
async def get_market_news_feed(
    limit: int = Query(default=10, ge=1, le=50, description="Max news articles to return")
):
    """Retrieves real-time market-wide financial news headlines with sentiment annotations."""
    return await news_service.get_market_feed(limit=limit)


@router.get("/sectors/{sector}", response_model=List[NewsArticleSchema])
async def get_sector_news_feed(
    sector: str = Path(..., description="Target industry sector name"),
    limit: int = Query(default=10, ge=1, le=50, description="Max sector articles to return")
):
    """Retrieves news articles relevant to a specified industry sector."""
    return await news_service.get_sector_news(sector=sector, limit=limit)


@router.get("", response_model=List[NewsArticleSchema])
async def get_market_news(
    limit: int = Query(default=10, ge=1, le=50, description="Max news articles to return"),
    category: Optional[str] = Query(default=None, description="Optional news category filter"),
    event_type: Optional[str] = Query(default=None, description="Optional event classification filter"),
    sentiment: Optional[str] = Query(default=None, description="Optional sentiment filter")
):
    """Retrieves real-time market-wide financial news headlines with optional classification filters."""
    return await news_service.get_market_feed(
        limit=limit,
        category=category,
        event_type=event_type,
        sentiment=sentiment
    )


@router.get("/{symbol}/sentiment", response_model=NewsSentimentAggregation)
async def get_ticker_sentiment_aggregation(
    symbol: str = Path(..., description="Ticker symbol (e.g. RELIANCE.NS, NVDA)"),
    limit: int = Query(default=20, ge=1, le=50, description="Articles sample size for sentiment calculation")
):
    """Retrieves deep statistical sentiment distribution and trend for a ticker."""
    return await news_service.get_sentiment_summary(ticker=symbol, limit=limit)


@router.get("/{symbol}/timeline", response_model=List[NewsTimelineEvent])
async def get_ticker_news_timeline(
    symbol: str = Path(..., description="Ticker symbol (e.g. RELIANCE.NS, NVDA)"),
    limit: int = Query(default=10, ge=1, le=50, description="Max timeline events to return")
):
    """Retrieves chronological news timeline for correlating with price movements and anomalies."""
    return await news_service.get_timeline_for_ticker(ticker=symbol, limit=limit)


@router.get("/{symbol}", response_model=NewsSentimentSummary)
async def get_ticker_news(
    symbol: str = Path(..., description="Ticker symbol (e.g. RELIANCE.NS, AAPL)"),
    limit: int = Query(default=5, ge=1, le=20, description="Max ticker news articles to return")
):
    """Retrieves company-specific news articles with aggregate sentiment analysis."""
    return await news_service.get_news_for_ticker(symbol, limit=limit)
