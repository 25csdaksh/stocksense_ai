"""
Financial News Feed & Real-Time Sentiment API Routes.
"""
from typing import List, Dict, Any
from fastapi import APIRouter, Query
from app.schemas.news import NewsSentimentSummary, NewsArticleSchema
from app.services.news_service import news_service

router = APIRouter(prefix="/news", tags=["Financial News & Sentiment"])


@router.get("", response_model=List[NewsArticleSchema])
async def get_market_news(
    limit: int = Query(default=10, ge=1, le=50, description="Max news articles to return")
):
    """Retrieves real-time market-wide financial news headlines with sentiment annotations."""
    return await news_service.get_market_feed(limit=limit)


@router.get("/{symbol}", response_model=NewsSentimentSummary)
async def get_ticker_news(
    symbol: str,
    limit: int = Query(default=5, ge=1, le=20, description="Max ticker news articles to return")
):
    """Retrieves company-specific news articles with aggregate sentiment analysis."""
    return await news_service.get_news_for_ticker(symbol, limit=limit)
