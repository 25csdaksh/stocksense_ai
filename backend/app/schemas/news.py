"""
Financial News & NLP Sentiment Schemas.
"""
from typing import List, Dict, Any, Optional
from pydantic import BaseModel


class NewsArticleSchema(BaseModel):
    id: str
    ticker: str
    title: str
    summary: str
    source: str
    url: Optional[str] = None
    published_at: str
    sentiment_label: str  # BULLISH, BEARISH, NEUTRAL
    sentiment_score: float
    impact_score: float


class NewsSentimentSummary(BaseModel):
    ticker: str
    overall_sentiment: str
    average_sentiment_score: float
    news_items: List[NewsArticleSchema]
