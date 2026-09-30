"""
MarketMind AI — Curated Financial News Mock Provider.
Phase 6.7: High-fidelity mock adapter with sentiment scoring, event classification,
and legacy dictionary mapping for isolated unit and integration testing.
"""
from typing import Dict, Any, List, Optional
from datetime import datetime, timezone, timedelta
from app.providers.news.base import BaseNewsProvider
from app.providers.news.models import (
    NewsArticleData,
    NewsCategory,
    NewsEventType,
    SentimentLabel,
    ImpactDirection,
    ImpactHorizon,
    ImpactScope,
    NewsDataSource,
    NewsDataStatus
)
from app.providers.news.validator import news_validator
from app.analytics.news_nlp_engine import news_nlp_engine


class MockNewsProvider(BaseNewsProvider):
    """Deterministic mock provider for news pipeline testing."""

    SAMPLE_NEWS: List[Dict[str, Any]] = [
        {
            "id": "news_nvda_1",
            "ticker": "NVDA",
            "symbols": ["NVDA"],
            "title": "NVIDIA Blackwell GPU Platform Ramps Up Datacenter Volume Shipments",
            "headline": "NVIDIA Blackwell GPU Platform Ramps Up Datacenter Volume Shipments",
            "summary": "Hyperscaler demand remains robust for high-performance generative AI accelerators, with supply commitments locking in double-digit sequential growth.",
            "source": "Bloomberg Financial",
            "url": "https://bloomberg.com/sample/nvda-blackwell",
            "published_at": (datetime.now(timezone.utc) - timedelta(hours=2)).strftime("%Y-%m-%d %H:%M:%S UTC"),
            "sentiment_label": "BULLISH",
            "sentiment": "POSITIVE",
            "sentiment_score": 0.82,
            "impact_score": 0.90,
            "category": "TECHNOLOGY",
            "event_type": "PRODUCT_LAUNCH",
            "data_source": "DEMO",
            "data_status": "DEMO",
        },
        {
            "id": "news_aapl_1",
            "ticker": "AAPL",
            "symbols": ["AAPL"],
            "title": "Apple Intelligence Hardware Cycle Gains Institutional Upgrade Endorsements",
            "headline": "Apple Intelligence Hardware Cycle Gains Institutional Upgrade Endorsements",
            "summary": "Early device telemetry indicates strong enterprise and consumer upgrade intent across premium silicon models.",
            "source": "Reuters Financial",
            "url": "https://reuters.com/sample/aapl-intelligence",
            "published_at": (datetime.now(timezone.utc) - timedelta(hours=5)).strftime("%Y-%m-%d %H:%M:%S UTC"),
            "sentiment_label": "BULLISH",
            "sentiment": "POSITIVE",
            "sentiment_score": 0.68,
            "impact_score": 0.75,
            "category": "PRODUCT",
            "event_type": "PRODUCT_LAUNCH",
            "data_source": "DEMO",
            "data_status": "DEMO",
        },
        {
            "id": "news_msft_1",
            "ticker": "MSFT",
            "symbols": ["MSFT"],
            "title": "Microsoft Azure Commercial Cloud Accelerates Operating Margins",
            "headline": "Microsoft Azure Commercial Cloud Accelerates Operating Margins",
            "summary": "Enterprise adoption of Copilot and scalable cloud compute drives 180 bps gross margin expansion.",
            "source": "Wall Street Journal",
            "url": "https://wsj.com/sample/msft-azure",
            "published_at": (datetime.now(timezone.utc) - timedelta(hours=7)).strftime("%Y-%m-%d %H:%M:%S UTC"),
            "sentiment_label": "BULLISH",
            "sentiment": "POSITIVE",
            "sentiment_score": 0.74,
            "impact_score": 0.82,
            "category": "EARNINGS",
            "event_type": "EARNINGS",
            "data_source": "DEMO",
            "data_status": "DEMO",
        },
        {
            "id": "news_spy_1",
            "ticker": "SPY",
            "symbols": ["SPY"],
            "title": "Federal Reserve Monetary Policy Committee Highlights Balanced Inflation Outlook",
            "headline": "Federal Reserve Monetary Policy Committee Highlights Balanced Inflation Outlook",
            "summary": "Minutes from the latest FOMC meeting emphasize data-dependent calibration and resilient labor market conditions.",
            "source": "Financial Times",
            "url": "https://ft.com/sample/fed-minutes",
            "published_at": (datetime.now(timezone.utc) - timedelta(hours=12)).strftime("%Y-%m-%d %H:%M:%S UTC"),
            "sentiment_label": "BULLISH",
            "sentiment": "POSITIVE",
            "sentiment_score": 0.45,
            "impact_score": 0.88,
            "category": "MACRO",
            "event_type": "MACRO_EVENT",
            "data_source": "DEMO",
            "data_status": "DEMO",
        }
    ]

    async def get_latest_news(self, limit: int = 20) -> List[NewsArticleData]:
        results: List[NewsArticleData] = []
        for raw in self.SAMPLE_NEWS[:limit]:
            valid, article, _ = news_validator.validate_and_sanitize(raw)
            if valid and article:
                results.append(article)
        return results

    async def get_stock_news(self, symbol: str, limit: int = 10) -> List[NewsArticleData]:
        sym = symbol.upper().strip()
        matches: List[NewsArticleData] = []
        for raw in self.SAMPLE_NEWS:
            if raw["ticker"] == sym or sym in raw.get("symbols", []):
                valid, article, _ = news_validator.validate_and_sanitize(raw)
                if valid and article:
                    matches.append(article)

        if not matches:
            gen_raw = {
                "id": f"gen_{sym}_1",
                "ticker": sym,
                "symbols": [sym],
                "title": f"{sym} Capital Allocation & Quarterly Free Cash Flow Assessment",
                "headline": f"{sym} Capital Allocation & Quarterly Free Cash Flow Assessment",
                "summary": f"Institutional analysts examine capital expenditures, return on invested capital, and operating gross margins for {sym}.",
                "source": "Financial Intelligence Desk",
                "url": None,
                "published_at": datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC"),
                "sentiment_label": "NEUTRAL",
                "sentiment": "NEUTRAL",
                "sentiment_score": 0.15,
                "impact_score": 0.60,
                "category": "MARKET",
                "event_type": "OTHER",
                "data_source": "DEMO",
                "data_status": "DEMO",
            }
            valid, article, _ = news_validator.validate_and_sanitize(gen_raw)
            if valid and article:
                matches.append(article)

        return matches[:limit]

    async def get_sector_news(self, sector: str, limit: int = 10) -> List[NewsArticleData]:
        return await self.get_latest_news(limit=limit)

    async def get_news_for_ticker(self, ticker: str, limit: int = 5) -> List[Dict[str, Any]]:
        articles = await self.get_stock_news(ticker, limit=limit)
        return [a.model_dump() for a in articles]

    async def get_market_news(self, limit: int = 10) -> List[Dict[str, Any]]:
        articles = await self.get_latest_news(limit=limit)
        return [a.model_dump() for a in articles]

    async def get_historical_news(
        self,
        symbol: Optional[str] = None,
        from_date: Optional[str] = None,
        to_date: Optional[str] = None,
        limit: int = 20
    ) -> List[NewsArticleData]:
        if symbol:
            return await self.get_stock_news(symbol, limit=limit)
        return await self.get_latest_news(limit=limit)
