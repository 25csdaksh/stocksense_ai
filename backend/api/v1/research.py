"""
RAG SEC Search and Financial News Endpoints.
"""
from typing import List, Optional
from fastapi import APIRouter
from schemas.research_schema import (
    DocumentSearchRequest,
    DocumentSearchResponse,
    NewsSentimentResponse,
    NewsItem
)
from services.rag_service import rag_service
from services.news_service import news_service

router = APIRouter(prefix="/research", tags=["RAG Knowledge & News Intelligence"])


@router.post("/search-filings", response_model=DocumentSearchResponse)
async def search_sec_filings(req: DocumentSearchRequest):
    """Semantic vector search across SEC 10-K/10-Q disclosures with exact citation page references."""
    return rag_service.search_filings(
        query=req.query,
        ticker=req.ticker,
        filing_type=req.doc_type or "ALL",
        top_k=req.top_k
    )


@router.get("/news/{ticker}", response_model=NewsSentimentResponse)
async def get_ticker_news_sentiment(ticker: str):
    """Retrieves news feed and computes aggregate sentiment polarity for a ticker."""
    return news_service.get_news_for_ticker(ticker)


@router.get("/news-feed", response_model=List[NewsItem])
async def get_market_news_feed(limit: int = 10):
    """Returns top macro and corporate financial news articles with impact scores."""
    return news_service.get_market_news_feed(limit=limit)
