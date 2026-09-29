"""
RAG Research and News Sentiment Schemas.
"""
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field


class DocumentSearchRequest(BaseModel):
    query: str = Field(..., min_length=2)
    ticker: Optional[str] = None
    doc_type: Optional[str] = Field(default="ALL", description="10-K, 10-Q, 8-K, EARNINGS, ALL")
    top_k: int = Field(default=5, ge=1, le=20)


class DocumentCitation(BaseModel):
    id: str
    ticker: str
    title: str
    filing_type: str
    fiscal_year: Optional[int] = None
    section: str
    content_snippet: str
    relevance_score: float
    page_number: Optional[int] = None


class DocumentSearchResponse(BaseModel):
    query: str
    total_results: int
    citations: List[DocumentCitation]
    synthesis_summary: Optional[str] = None


class NewsItem(BaseModel):
    id: str
    ticker: str
    title: str
    summary: str
    source: str
    url: Optional[str] = None
    published_at: str
    sentiment_label: str  # 'BULLISH', 'BEARISH', 'NEUTRAL'
    sentiment_score: float
    impact_score: float


class NewsSentimentResponse(BaseModel):
    ticker: str
    overall_sentiment: str
    average_sentiment_score: float
    news_items: List[NewsItem]
    sentiment_breakdown: Dict[str, int]
