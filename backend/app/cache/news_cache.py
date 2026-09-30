"""
MarketMind AI — Multi-Tier Redis Caching Layer for Financial News.
Phase 6.7: Namespaced cache keys, market isolation, and configurable TTL strategies.
"""
import json
from typing import Dict, Any, List, Optional
from app.cache.redis_client import redis_client
from app.core.logging import logger

from app.providers.news.models import NewsArticleData, NewsSentimentAggregation


class NewsCache:
    """Redis cache manager for high-frequency financial news queries."""

    # TTL constants in seconds
    TTL_MARKET_NEWS = 300      # 5 minutes
    TTL_STOCK_NEWS = 300       # 5 minutes
    TTL_SECTOR_NEWS = 600      # 10 minutes
    TTL_ARTICLE_DETAIL = 3600  # 1 hour
    TTL_AI_SUMMARY = 3600      # 1 hour

    @staticmethod
    def _make_key(market: str, scope: str, identifier: str, filters: str = "default") -> str:
        clean_market = (market or "global").lower()
        clean_scope = (scope or "feed").lower()
        clean_id = (identifier or "all").lower().replace(":", "_").replace(" ", "_")
        clean_filters = (filters or "default").lower().replace(":", "_")
        return f"marketmind:news:{clean_market}:{clean_scope}:{clean_id}:{clean_filters}"

    async def get_market_feed(self, market: str = "all", limit: int = 10) -> Optional[List[NewsArticleData]]:
        key = self._make_key(market, "feed", "market", f"limit_{limit}")
        try:
            val = await redis_client.get(key)
            if val:
                raw_list = json.loads(val)
                return [NewsArticleData.model_validate(item) for item in raw_list]
        except Exception as err:
            logger.debug(f"[NewsCache] Cache read error for {key}: {err}")
        return None

    async def set_market_feed(self, articles: List[NewsArticleData], market: str = "all", limit: int = 10) -> None:
        key = self._make_key(market, "feed", "market", f"limit_{limit}")
        try:
            dumped = [a.model_dump() for a in articles]
            await redis_client.set(key, json.dumps(dumped), expire=self.TTL_MARKET_NEWS)
        except Exception as err:
            logger.debug(f"[NewsCache] Cache write error for {key}: {err}")

    async def get_stock_news(self, ticker: str, limit: int = 5) -> Optional[List[NewsArticleData]]:
        key = self._make_key("stock", "ticker", ticker, f"limit_{limit}")
        try:
            val = await redis_client.get(key)
            if val:
                raw_list = json.loads(val)
                return [NewsArticleData.model_validate(item) for item in raw_list]
        except Exception as err:
            logger.debug(f"[NewsCache] Cache read error for {key}: {err}")
        return None

    async def set_stock_news(self, ticker: str, articles: List[NewsArticleData], limit: int = 5) -> None:
        key = self._make_key("stock", "ticker", ticker, f"limit_{limit}")
        try:
            dumped = [a.model_dump() for a in articles]
            await redis_client.set(key, json.dumps(dumped), expire=self.TTL_STOCK_NEWS)
        except Exception as err:
            logger.debug(f"[NewsCache] Cache write error for {key}: {err}")

    async def get_sector_news(self, sector: str, limit: int = 10) -> Optional[List[NewsArticleData]]:
        key = self._make_key("sector", "category", sector, f"limit_{limit}")
        try:
            val = await redis_client.get(key)
            if val:
                raw_list = json.loads(val)
                return [NewsArticleData.model_validate(item) for item in raw_list]
        except Exception as err:
            logger.debug(f"[NewsCache] Cache read error for {key}: {err}")
        return None

    async def set_sector_news(self, sector: str, articles: List[NewsArticleData], limit: int = 10) -> None:
        key = self._make_key("sector", "category", sector, f"limit_{limit}")
        try:
            dumped = [a.model_dump() for a in articles]
            await redis_client.set(key, json.dumps(dumped), expire=self.TTL_SECTOR_NEWS)
        except Exception as err:
            logger.debug(f"[NewsCache] Cache write error for {key}: {err}")

    async def get_article_detail(self, article_id: str) -> Optional[NewsArticleData]:
        key = self._make_key("article", "id", article_id)
        try:
            val = await redis_client.get(key)
            if val:
                return NewsArticleData.model_validate(json.loads(val))
        except Exception as err:
            logger.debug(f"[NewsCache] Cache read error for {key}: {err}")
        return None

    async def set_article_detail(self, article: NewsArticleData) -> None:
        key = self._make_key("article", "id", article.id)
        try:
            await redis_client.set(key, json.dumps(article.model_dump()), expire=self.TTL_ARTICLE_DETAIL)
        except Exception as err:
            logger.debug(f"[NewsCache] Cache write error for {key}: {err}")


news_cache = NewsCache()
