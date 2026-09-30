"""
MarketMind AI — Financial News Collector & Ingestion Pipeline.
Phase 6.7: High-performance batch collector coordinating provider fetch,
normalization, NLP sentiment enrichment, deduplication, Redis caching,
PostgreSQL persistence, and real-time streaming WebSocket broadcasting.
"""
import asyncio
import time
from typing import Dict, Any, List, Optional, Set
from datetime import datetime, timezone

from app.core.logging import logger
from app.db.session import async_session_factory
from app.db.repositories.news_repository import NewsRepository
from app.providers.news.factory import get_news_provider
from app.providers.news.models import (
    NewsArticleData,
    NewsCategory,
    NewsEventType,
    NewsDataSource,
    NewsDataStatus,
)
from app.providers.news.validator import news_validator
from app.analytics.news_nlp_engine import news_nlp_engine
from app.cache.news_cache import news_cache
from app.providers.market_data.streaming_events import (
    event_bus,
    MarketDataEvent,
    MarketEventType,
)
from app.providers.market_data.models import DataStatus


class NewsCollector:
    """Batch and streaming collector for financial news intelligence."""

    DEFAULT_UNIVERSE = [
        "RELIANCE.NS", "TCS.NS", "INFY.NS", "HDFCBANK.NS", "ICICIBANK.NS",
        "ITC.NS", "SBIN.NS", "TATAMOTORS.NS", "^NSEI", "^BSESN",
        "AAPL", "MSFT", "NVDA", "AMZN", "GOOGL", "SPY"
    ]

    def __init__(self):
        self.provider = get_news_provider()
        self._processed_hashes: Set[str] = set()

        # Telemetry Metrics
        self._articles_processed: int = 0
        self._articles_failed: int = 0
        self._duplicates_prevented: int = 0
        self._provider_failures: int = 0
        self._missing_symbols: int = 0
        self._classification_failures: int = 0
        self._sentiment_failures: int = 0
        self._last_successful_run: Optional[str] = None

    def get_telemetry(self) -> Dict[str, Any]:
        """Returns runtime data quality and collector health metrics."""
        return {
            "provider_status": "HEALTHY" if self._provider_failures == 0 else "DEGRADED",
            "articles_processed": self._articles_processed,
            "articles_failed": self._articles_failed,
            "duplicates_prevented": self._duplicates_prevented,
            "provider_failures": self._provider_failures,
            "missing_symbols": self._missing_symbols,
            "classification_failures": self._classification_failures,
            "sentiment_failures": self._sentiment_failures,
            "last_successful_run": self._last_successful_run or datetime.now(timezone.utc).isoformat(),
            "freshness": "REALTIME",
        }

    async def ingest_article(self, raw_article: Dict[str, Any], broadcast: bool = True) -> Optional[NewsArticleData]:
        """
        Ingests, validates, enriches, deduplicates, caches, persists, and broadcasts a single news article.
        """
        try:
            # 1. Validation & sanitization
            valid, article, err = news_validator.validate_and_sanitize(raw_article)
            if not valid or not article:
                self._articles_failed += 1
                logger.debug(f"[NewsCollector] Validation rejected article: {err}")
                return None

            # 2. In-memory & Hash Deduplication
            if article.content_hash in self._processed_hashes:
                self._duplicates_prevented += 1
                return article
            self._processed_hashes.add(article.content_hash)

            # 3. Entity Linking Enrichment (Symbols, Companies, Sectors)
            linked_symbols, linked_companies, linked_sectors = news_nlp_engine.link_entities(
                f"{article.headline} {article.summary}",
                provided_symbols=article.symbols
            )
            if linked_symbols:
                article.symbols = linked_symbols
                article.ticker = linked_symbols[0]
            if linked_companies:
                article.companies = linked_companies
            if linked_sectors:
                article.sectors = linked_sectors
                article.sector = linked_sectors[0]

            if not article.symbols:
                self._missing_symbols += 1

            # 4. Sentiment Analysis Enrichment
            try:
                sent_label, sent_score, sent_conf = news_nlp_engine.analyze_sentiment(
                    f"{article.headline} {article.summary}"
                )
                article.sentiment = sent_label
                article.sentiment_label = sent_label.value
                article.sentiment_score = sent_score
                article.sentiment_confidence = sent_conf
            except Exception as e:
                self._sentiment_failures += 1
                logger.debug(f"[NewsCollector] Sentiment analysis error: {e}")

            # 5. Event Classification Enrichment
            try:
                ev_type, ev_conf = news_nlp_engine.classify_event(f"{article.headline} {article.summary}")
                article.event_type = ev_type
                article.event_confidence = ev_conf
                article.category = news_nlp_engine.classify_category(f"{article.headline} {article.summary}")
            except Exception as e:
                self._classification_failures += 1
                logger.debug(f"[NewsCollector] Event classification error: {e}")

            # 6. Impact & Relevance Scoring
            impact_dir, impact_score, horizon, scope = news_nlp_engine.evaluate_impact(
                article.sentiment_score,
                article.event_type,
                len(article.symbols)
            )
            article.impact_direction = impact_dir
            article.impact_score = impact_score
            article.impact_horizon = horizon
            article.impact_scope = scope
            article.relevance_score = news_nlp_engine.compute_relevance(
                article.ticker,
                article.symbols,
                article.headline,
                article.summary
            )

            # 7. Redis Cache Write
            await news_cache.set_article_detail(article)

            # 8. PostgreSQL Persistence (Non-blocking async)
            try:
                async with async_session_factory() as session:
                    repo = NewsRepository(session)
                    await repo.upsert_article(article)
            except Exception as db_err:
                logger.warning(f"[NewsCollector] DB persistence non-fatal error: {db_err}")

            # 9. Realtime WebSocket Broadcasting via EventBus
            if broadcast:
                data_status_enum = DataStatus.DEMO
                if article.data_status == NewsDataStatus.LIVE:
                    data_status_enum = DataStatus.LIVE

                event = MarketDataEvent(
                    event_type=MarketEventType.NEWS_PUBLISHED,
                    symbol=article.ticker or "MARKET",
                    exchange="NSE" if article.market == "INDIA" else "US",
                    timestamp=datetime.now(timezone.utc).isoformat(),
                    data_source=article.data_source.value,
                    data_status=data_status_enum,
                    payload={
                        "article_id": article.id,
                        "headline": article.headline,
                        "title": article.title,
                        "summary": article.summary,
                        "source": article.source,
                        "url": article.url,
                        "published_at": article.published_at,
                        "ticker": article.ticker,
                        "symbols": article.symbols,
                        "category": article.category.value,
                        "event_type": article.event_type.value,
                        "sentiment": article.sentiment_label,
                        "sentiment_label": article.sentiment_label,
                        "sentiment_score": article.sentiment_score,
                        "impact_score": article.impact_score,
                        "impact_direction": article.impact_direction.value,
                        "relevance_score": article.relevance_score,
                        "sector": article.sector,
                    }
                )
                await event_bus.publish(event)

            self._articles_processed += 1
            self._last_successful_run = datetime.now(timezone.utc).isoformat()
            return article

        except Exception as exc:
            self._articles_failed += 1
            logger.error(f"[NewsCollector] Unexpected error ingesting article: {exc}")
            return None

    async def run_batch_collection(self, symbols: Optional[List[str]] = None) -> List[NewsArticleData]:
        """
        Fetches breaking news from configured providers across the target universe
        with isolated failure handling.
        """
        universe = symbols or self.DEFAULT_UNIVERSE
        ingested: List[NewsArticleData] = []

        try:
            # 1. Ingest general breaking market news
            latest_raw = await self.provider.get_latest_news(limit=25)
            for raw_art in latest_raw:
                res = await self.ingest_article(raw_art.model_dump() if hasattr(raw_art, "model_dump") else raw_art)
                if res:
                    ingested.append(res)
        except Exception as e:
            self._provider_failures += 1
            logger.error(f"[NewsCollector] Provider failure fetching general news: {e}")

        # 2. Ingest ticker-specific feeds with error isolation
        for sym in universe:
            try:
                stock_news = await self.provider.get_stock_news(sym, limit=5)
                for raw_art in stock_news:
                    res = await self.ingest_article(raw_art.model_dump() if hasattr(raw_art, "model_dump") else raw_art)
                    if res:
                        ingested.append(res)
            except Exception as sym_err:
                logger.warning(f"[NewsCollector] Provider error for symbol {sym}: {sym_err}")

        # Update cache for market feed
        if ingested:
            await news_cache.set_market_feed(ingested, market="all", limit=len(ingested))

        return ingested


news_collector = NewsCollector()
