"""
Financial News & Aggregate Sentiment Service.
"""
from typing import Dict, Any, List
from app.providers.news.factory import get_news_provider
from app.utils.validators import validate_ticker


class NewsService:

    def __init__(self):
        self.provider = get_news_provider()

    async def get_news_for_ticker(self, ticker: str, limit: int = 5) -> Dict[str, Any]:
        sym = validate_ticker(ticker)
        items = await self.provider.get_news_for_ticker(sym, limit=limit)
        
        avg_score = sum(i["sentiment_score"] for i in items) / max(1, len(items))
        overall = "BULLISH" if avg_score > 0.20 else ("BEARISH" if avg_score < -0.20 else "NEUTRAL")

        return {
            "ticker": sym,
            "overall_sentiment": overall,
            "average_sentiment_score": round(float(avg_score), 3),
            "news_items": items
        }

    async def get_market_feed(self, limit: int = 10) -> List[Dict[str, Any]]:
        return await self.provider.get_market_news(limit=limit)


news_service = NewsService()
