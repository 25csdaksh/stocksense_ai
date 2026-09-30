"""
MarketMind AI — Intelligent Multi-Market News Provider Factory & Router.
Phase 6.7: Pluggable provider selection with automatic symbol and market dispatching.
"""
from typing import Dict, Any, List, Optional
from app.providers.news.base import BaseNewsProvider
from app.providers.news.models import NewsArticleData
from app.providers.news.indian_provider import IndianNewsProvider
from app.providers.news.us_provider import USNewsProvider
from app.providers.news.mock_news import MockNewsProvider
from app.providers.market_data.symbol_normalizer import symbol_normalizer


class RoutingNewsProvider(BaseNewsProvider):
    """
    Intelligent router dispatching news queries to the appropriate market provider
    (Indian NSE/BSE vs US NASDAQ/NYSE) based on ticker pattern and asset classification.
    """

    def __init__(self):
        self.indian_provider = IndianNewsProvider()
        self.us_provider = USNewsProvider()
        self.mock_provider = MockNewsProvider()

    def _is_indian_symbol(self, symbol: str) -> bool:
        if not symbol:
            return True
        norm = symbol_normalizer.normalize(symbol)
        if norm.exchange in ("NSE", "BSE") or norm.display_symbol.endswith(".NS") or norm.display_symbol.endswith(".BO") or norm.display_symbol.startswith("^"):
            return True
        # Known Indian tickers
        indian_tickers = {"RELIANCE", "TCS", "INFY", "HDFCBANK", "ICICIBANK", "SBIN", "ITC", "TATAMOTORS", "MARUTI", "ONGC", "BHARTIARTL", "NIFTY", "SENSEX"}
        return symbol.upper() in indian_tickers

    def _get_provider_for_symbol(self, symbol: Optional[str]) -> BaseNewsProvider:
        if not symbol:
            return self.indian_provider
        if self._is_indian_symbol(symbol):
            return self.indian_provider
        return self.us_provider

    async def get_latest_news(self, limit: int = 20) -> List[NewsArticleData]:
        # Merge top breaking news from both Indian and US providers
        in_half = max(1, limit // 2)
        us_half = limit - in_half

        in_news = await self.indian_provider.get_latest_news(limit=in_half)
        us_news = await self.us_provider.get_latest_news(limit=us_half)

        combined = in_news + us_news
        # Sort by published_at descending if available
        return sorted(combined, key=lambda x: x.published_at or "", reverse=True)[:limit]

    async def get_stock_news(self, symbol: str, limit: int = 10) -> List[NewsArticleData]:
        provider = self._get_provider_for_symbol(symbol)
        return await provider.get_stock_news(symbol, limit=limit)

    async def get_sector_news(self, sector: str, limit: int = 10) -> List[NewsArticleData]:
        in_news = await self.indian_provider.get_sector_news(sector, limit=limit)
        if in_news:
            return in_news
        return await self.us_provider.get_sector_news(sector, limit=limit)

    async def get_market_news(self, limit: int = 10) -> List[Dict[str, Any]]:
        articles = await self.get_latest_news(limit=limit)
        return [a.model_dump() for a in articles]

    async def get_news_for_ticker(self, ticker: str, limit: int = 5) -> List[Dict[str, Any]]:
        articles = await self.get_stock_news(ticker, limit=limit)
        return [a.model_dump() for a in articles]

    async def get_historical_news(
        self,
        symbol: Optional[str] = None,
        from_date: Optional[str] = None,
        to_date: Optional[str] = None,
        limit: int = 20
    ) -> List[NewsArticleData]:
        provider = self._get_provider_for_symbol(symbol)
        return await provider.get_historical_news(
            symbol=symbol,
            from_date=from_date,
            to_date=to_date,
            limit=limit
        )


_routing_provider = RoutingNewsProvider()


def get_news_provider(symbol: Optional[str] = None) -> BaseNewsProvider:
    """Returns the routing news provider or a targeted provider for the symbol."""
    return _routing_provider
