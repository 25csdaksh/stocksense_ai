"""
MarketMind AI — Financial News Provider Interface.
Phase 6.7: Complete async contract supporting multi-market news retrieval,
ticker intelligence, sector streams, macro feeds, and historical queries.
"""
from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional
from app.providers.news.models import NewsArticleData


class BaseNewsProvider(ABC):
    """Abstract interface for all financial news provider adapters."""

    @abstractmethod
    async def get_latest_news(self, limit: int = 20) -> List[NewsArticleData]:
        """Fetches latest breaking market-wide financial news."""
        pass

    @abstractmethod
    async def get_stock_news(self, symbol: str, limit: int = 10) -> List[NewsArticleData]:
        """Fetches news specifically linked to a target company or ticker."""
        pass

    @abstractmethod
    async def get_sector_news(self, sector: str, limit: int = 10) -> List[NewsArticleData]:
        """Fetches news relevant to a specific industry or market sector."""
        pass

    @abstractmethod
    async def get_market_news(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Legacy dictionary compatibility endpoint."""
        pass

    @abstractmethod
    async def get_news_for_ticker(self, ticker: str, limit: int = 5) -> List[Dict[str, Any]]:
        """Legacy dictionary compatibility endpoint."""
        pass

    @abstractmethod
    async def get_historical_news(
        self,
        symbol: Optional[str] = None,
        from_date: Optional[str] = None,
        to_date: Optional[str] = None,
        limit: int = 20
    ) -> List[NewsArticleData]:
        """Queries historical financial news articles across a time window."""
        pass


# Alias for legacy compatibility
NewsProvider = BaseNewsProvider
