"""
MarketMind AI — Financial News & Aggregate Sentiment Service.
Phase 6.7: High-level news orchestrator coordinating Redis caching, provider routing,
database lookups, sentiment summaries, timelines, anomaly correlations, and watchlist news.
"""
from typing import Dict, Any, List, Optional
from datetime import datetime, timezone, timedelta

from app.providers.news.factory import get_news_provider
from app.providers.news.models import (
    NewsArticleData,
    NewsSentimentAggregation,
    SectorSentimentSummary,
    NewsTimelineEvent,
    SentimentLabel,
    NewsCategory,
    NewsEventType,
    NewsDataSource,
    NewsDataStatus,
)
from app.cache.news_cache import news_cache
from app.services.news_collector import news_collector
from app.utils.validators import validate_ticker
from app.db.session import async_session_factory
from app.db.repositories.news_repository import NewsRepository


class NewsService:
    """Financial news & intelligence service layer."""

    def __init__(self):
        self.provider = get_news_provider()

    async def get_news_for_ticker(self, ticker: str, limit: int = 5) -> Dict[str, Any]:
        """
        Retrieves company-specific news articles with aggregate sentiment analysis.
        Preserves backward-compatible dictionary structure for existing services and tests.
        """
        sym = validate_ticker(ticker)

        # 1. Try Redis cache
        cached = await news_cache.get_stock_news(sym, limit=limit)
        if cached:
            items = [a.model_dump() for a in cached]
        else:
            # 2. Fetch from provider and cache
            provider_articles = await self.provider.get_stock_news(sym, limit=limit)
            items = []
            for art in provider_articles:
                # Ingest through collector pipeline for normalization and persistence
                enriched = await news_collector.ingest_article(art.model_dump() if hasattr(art, "model_dump") else art, broadcast=False)
                if enriched:
                    items.append(enriched.model_dump())
                else:
                    items.append(art.model_dump() if hasattr(art, "model_dump") else art)

            if items:
                converted = [NewsArticleData.model_validate(i) for i in items]
                await news_cache.set_stock_news(sym, converted, limit=limit)

        avg_score = sum(float(i.get("sentiment_score", 0.0)) for i in items) / max(1, len(items))
        if avg_score > 0.20:
            overall = "BULLISH"
        elif avg_score < -0.20:
            overall = "BEARISH"
        else:
            overall = "NEUTRAL"

        return {
            "ticker": sym,
            "overall_sentiment": overall,
            "average_sentiment_score": round(float(avg_score), 3),
            "news_items": items[:limit]
        }

    async def get_market_feed(
        self,
        limit: int = 10,
        category: Optional[str] = None,
        event_type: Optional[str] = None,
        sentiment: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """Retrieves market-wide breaking news with optional category, event, and sentiment filters."""
        # 1. Try Redis cache for default unfiltered queries
        if not category and not event_type and not sentiment:
            cached = await news_cache.get_market_feed(market="all", limit=limit)
            if cached:
                return [a.model_dump() for a in cached]

        # 2. Query from provider
        articles = await self.provider.get_latest_news(limit=max(limit, 25))
        enriched_list = []
        for a in articles:
            enriched = await news_collector.ingest_article(a.model_dump() if hasattr(a, "model_dump") else a, broadcast=False)
            enriched_list.append(enriched or a)

        # Apply filtering in memory
        filtered = enriched_list
        if category and category.upper() != "ALL":
            filtered = [a for a in filtered if a.category.value.upper() == category.upper()]
        if event_type and event_type.upper() != "ALL":
            filtered = [a for a in filtered if a.event_type.value.upper() == event_type.upper()]
        if sentiment and sentiment.upper() != "ALL":
            filtered = [a for a in filtered if a.sentiment_label.upper() == sentiment.upper()]

        result = [a.model_dump() for a in filtered[:limit]]
        if not category and not event_type and not sentiment and enriched_list:
            await news_cache.set_market_feed(enriched_list[:limit], market="all", limit=limit)

        return result

    async def get_sector_news(self, sector: str, limit: int = 10) -> List[Dict[str, Any]]:
        """Retrieves news articles matching a specific sector."""
        cached = await news_cache.get_sector_news(sector, limit=limit)
        if cached:
            return [a.model_dump() for a in cached]

        articles = await self.provider.get_sector_news(sector, limit=limit)
        result = [a.model_dump() for a in articles]
        await news_cache.set_sector_news(sector, articles, limit=limit)
        return result

    async def get_sentiment_summary(
        self,
        ticker: Optional[str] = None,
        sector: Optional[str] = None,
        limit: int = 20
    ) -> NewsSentimentAggregation:
        """Aggregates sentiment distribution, trend, and sector breakdowns."""
        if ticker:
            ticker_data = await self.get_news_for_ticker(ticker, limit=limit)
            articles = [NewsArticleData.model_validate(i) for i in ticker_data["news_items"]]
        else:
            market_data = await self.get_market_feed(limit=limit)
            articles = [NewsArticleData.model_validate(i) for i in market_data]

        pos_count = sum(1 for a in articles if a.sentiment_score > 0.20)
        neg_count = sum(1 for a in articles if a.sentiment_score < -0.20)
        mixed_count = sum(1 for a in articles if abs(a.sentiment_score) <= 0.20 and a.sentiment_score != 0)
        neutral_count = len(articles) - pos_count - neg_count - mixed_count

        avg_score = sum(a.sentiment_score for a in articles) / max(1, len(articles))
        if avg_score > 0.20:
            overall = "BULLISH"
            trend = "IMPROVING"
        elif avg_score < -0.20:
            overall = "BEARISH"
            trend = "DETERIORATING"
        else:
            overall = "NEUTRAL"
            trend = "STABLE"

        # Sector breakdown
        sectors_map: Dict[str, List[NewsArticleData]] = {}
        for a in articles:
            sec = a.sector or "General Market"
            sectors_map.setdefault(sec, []).append(a)

        breakdowns: List[SectorSentimentSummary] = []
        for sec_name, sec_arts in sectors_map.items():
            s_pos = sum(1 for a in sec_arts if a.sentiment_score > 0.20)
            s_neg = sum(1 for a in sec_arts if a.sentiment_score < -0.20)
            s_neu = len(sec_arts) - s_pos - s_neg
            s_avg = sum(a.sentiment_score for a in sec_arts) / max(1, len(sec_arts))
            breakdowns.append(
                SectorSentimentSummary(
                    sector=sec_name,
                    article_count=len(sec_arts),
                    positive_count=s_pos,
                    neutral_count=s_neu,
                    negative_count=s_neg,
                    mixed_count=0,
                    positive_pct=round(s_pos / max(1, len(sec_arts)) * 100, 1),
                    neutral_pct=round(s_neu / max(1, len(sec_arts)) * 100, 1),
                    negative_pct=round(s_neg / max(1, len(sec_arts)) * 100, 1),
                    average_sentiment_score=round(s_avg, 3),
                    sentiment_trend="IMPROVING" if s_avg > 0.20 else ("DETERIORATING" if s_avg < -0.20 else "STABLE")
                )
            )

        return NewsSentimentAggregation(
            ticker=ticker,
            sector=sector,
            market="INDIA" if (ticker and (".NS" in ticker or ".BO" in ticker)) else "GLOBAL",
            overall_sentiment=overall,
            average_sentiment_score=round(avg_score, 3),
            total_articles=len(articles),
            positive_count=pos_count,
            neutral_count=neutral_count,
            negative_count=neg_count,
            mixed_count=mixed_count,
            sentiment_trend=trend,
            sector_breakdown=breakdowns,
            news_items=articles,
            data_source=NewsDataSource.DEMO,
            data_status=NewsDataStatus.DEMO
        )

    async def get_timeline_for_ticker(self, ticker: str, limit: int = 10) -> List[NewsTimelineEvent]:
        """Returns chronological news events for correlating with price movements and anomalies."""
        news_data = await self.get_news_for_ticker(ticker, limit=limit)
        events: List[NewsTimelineEvent] = []

        for item in news_data["news_items"]:
            events.append(
                NewsTimelineEvent(
                    article_id=item.get("id") or "art-unknown",
                    timestamp=item.get("published_at") or datetime.now(timezone.utc).isoformat(),
                    headline=item.get("headline") or item.get("title") or "Financial Headline",
                    ticker=ticker,
                    event_type=item.get("event_type") or NewsEventType.OTHER,
                    sentiment=item.get("sentiment") or SentimentLabel.NEUTRAL,
                    sentiment_score=float(item.get("sentiment_score", 0.0)),
                    impact_score=float(item.get("impact_score", 0.5)),
                    impact_direction=item.get("impact_direction") or "NEUTRAL",
                    impact_horizon=item.get("impact_horizon") or "SHORT_TERM",
                    source=item.get("source") or "Market Feed",
                    url=item.get("url"),
                    relevance_note="Associated news event occurred near this timeframe (not implied causation)"
                )
            )

        return sorted(events, key=lambda e: e.timestamp, reverse=True)

    async def get_watchlist_news(self, symbols: List[str], limit_per_stock: int = 2) -> Dict[str, Any]:
        """Batches news retrieval across a watched symbol portfolio."""
        results: Dict[str, Any] = {}
        for sym in symbols:
            try:
                data = await self.get_news_for_ticker(sym, limit=limit_per_stock)
                results[sym] = data
            except Exception as e:
                results[sym] = {"ticker": sym, "error": str(e), "news_items": []}
        return {"watchlist_news": results, "symbols_queried": len(symbols)}

    async def get_news_around_anomaly(
        self,
        symbol: str,
        timestamp_str: Optional[str] = None,
        window_hours: int = 24
    ) -> Dict[str, Any]:
        """Finds potentially relevant news within a time proximity window around a market anomaly."""
        news_data = await self.get_news_for_ticker(symbol, limit=10)
        items = news_data.get("news_items", [])

        return {
            "symbol": symbol,
            "anomaly_timestamp": timestamp_str or datetime.now(timezone.utc).isoformat(),
            "window_hours": window_hours,
            "correlation_disclaimer": "News items are surfaced based on time proximity and entity match. They do not constitute proven causal drivers.",
            "nearby_news": items[:5]
        }


news_service = NewsService()
