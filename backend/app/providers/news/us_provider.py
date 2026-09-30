"""
MarketMind AI — US Equities Financial News Provider.
Phase 6.7: Comprehensive news feed for NASDAQ/NYSE listed equities, Federal Reserve FOMC policy,
SEC regulatory disclosures, semiconductor hardware, and hyperscaler cloud developments.
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
from app.providers.market_data.symbol_normalizer import symbol_normalizer


class USNewsProvider(BaseNewsProvider):
    """News provider adapter for US financial markets (NASDAQ/NYSE)."""

    def _get_curated_us_articles(self) -> List[Dict[str, Any]]:
        now = datetime.now(timezone.utc)
        return [
            {
                "id": "news_us_nvda_1",
                "headline": "NVIDIA Blackwell GPU Architecture Enters Mass Production with Full Cloud Order Backlog",
                "summary": "NVIDIA reports exceptional enterprise demand for its GB200 NVL72 rack-scale systems across Tier-1 hyperscalers, with management signaling double-digit sequential growth.",
                "source": "Bloomberg Financial",
                "url": "https://bloomberg.com/news/nvda-blackwell-volume-shipments-2026",
                "published_at": (now - timedelta(minutes=40)).isoformat(),
                "country": "US",
                "market": "US",
                "ticker": "NVDA",
                "symbols": ["NVDA"],
                "category": NewsCategory.TECHNOLOGY.value,
                "event_type": NewsEventType.PRODUCT_LAUNCH.value,
                "sentiment_label": "BULLISH",
                "sentiment_score": 0.88,
                "impact_score": 0.94,
                "data_source": NewsDataSource.US_PROVIDER.value,
                "data_status": NewsDataStatus.DEMO.value,
            },
            {
                "id": "news_us_aapl_1",
                "headline": "Apple Intelligence Hardware Cycle Drives Premium iPhone Upgrades in North America & Europe",
                "summary": "Supply chain channel checks indicate strong average selling price (ASP) resilience as users upgrade to on-device neural silicon architectures.",
                "source": "Reuters Financial",
                "url": "https://reuters.com/tech/apple-intelligence-cycle-2026",
                "published_at": (now - timedelta(hours=2, minutes=15)).isoformat(),
                "country": "US",
                "market": "US",
                "ticker": "AAPL",
                "symbols": ["AAPL"],
                "category": NewsCategory.PRODUCT.value,
                "event_type": NewsEventType.PRODUCT_LAUNCH.value,
                "sentiment_label": "BULLISH",
                "sentiment_score": 0.72,
                "impact_score": 0.80,
                "data_source": NewsDataSource.US_PROVIDER.value,
                "data_status": NewsDataStatus.DEMO.value,
            },
            {
                "id": "news_us_msft_1",
                "headline": "Microsoft Azure Commercial Cloud Operating Margins Expand 210 bps on Copilot Adoption",
                "summary": "Enterprise cloud ARR surpasses internal targets as Fortune 500 companies scale production AI workloads on Microsoft Azure infrastructure.",
                "source": "Wall Street Journal",
                "url": "https://wsj.com/tech/msft-azure-operating-margins-2026",
                "published_at": (now - timedelta(hours=4, minutes=30)).isoformat(),
                "country": "US",
                "market": "US",
                "ticker": "MSFT",
                "symbols": ["MSFT"],
                "category": NewsCategory.EARNINGS.value,
                "event_type": NewsEventType.EARNINGS.value,
                "sentiment_label": "BULLISH",
                "sentiment_score": 0.76,
                "impact_score": 0.85,
                "data_source": NewsDataSource.US_PROVIDER.value,
                "data_status": NewsDataStatus.DEMO.value,
            },
            {
                "id": "news_us_amzn_1",
                "headline": "Amazon Web Services Accelerates Custom Graviton & Trainium Silicon Deployment",
                "summary": "AWS expands its proprietary AI training cluster capacity, delivering up to 40% improved price-performance for enterprise model fine-tuning.",
                "source": "Financial Times",
                "url": "https://ft.com/tech/aws-trainium-cloud-2026",
                "published_at": (now - timedelta(hours=6, minutes=10)).isoformat(),
                "country": "US",
                "market": "US",
                "ticker": "AMZN",
                "symbols": ["AMZN"],
                "category": NewsCategory.TECHNOLOGY.value,
                "event_type": NewsEventType.PRODUCT_LAUNCH.value,
                "sentiment_label": "BULLISH",
                "sentiment_score": 0.68,
                "impact_score": 0.78,
                "data_source": NewsDataSource.US_PROVIDER.value,
                "data_status": NewsDataStatus.DEMO.value,
            },
            {
                "id": "news_us_fomc_1",
                "headline": "Federal Reserve Monetary Policy Committee Highlights Balanced Inflation & Labor Trajectory",
                "summary": "Minutes from the FOMC policy gathering demonstrate broad consensus for measured policy normalization, supporting equity market liquidity.",
                "source": "CNBC",
                "url": "https://cnbc.com/economy/fomc-minutes-balance-2026",
                "published_at": (now - timedelta(hours=9)).isoformat(),
                "country": "US",
                "market": "US",
                "ticker": "SPY",
                "symbols": ["SPY", "AAPL", "MSFT", "NVDA"],
                "category": NewsCategory.MACRO.value,
                "event_type": NewsEventType.MACRO_EVENT.value,
                "sentiment_label": "NEUTRAL",
                "sentiment_score": 0.30,
                "impact_score": 0.90,
                "data_source": NewsDataSource.US_PROVIDER.value,
                "data_status": NewsDataStatus.DEMO.value,
            }
        ]

    async def get_latest_news(self, limit: int = 20) -> List[NewsArticleData]:
        raw_list = self._get_curated_us_articles()
        results: List[NewsArticleData] = []
        for raw in raw_list[:limit]:
            valid, article, _ = news_validator.validate_and_sanitize(raw)
            if valid and article:
                results.append(article)
        return results

    async def get_stock_news(self, symbol: str, limit: int = 10) -> List[NewsArticleData]:
        norm = symbol.upper().strip()
        raw_list = self._get_curated_us_articles()
        matching = []
        for raw in raw_list:
            symbols = raw.get("symbols", [])
            if norm in symbols or raw.get("ticker") == norm:
                valid, article, _ = news_validator.validate_and_sanitize(raw)
                if valid and article:
                    matching.append(article)

        if not matching:
            clean_ticker = norm
            now_iso = datetime.now(timezone.utc).isoformat()
            synth_raw = {
                "id": f"gen_us_{clean_ticker}_1",
                "headline": f"{clean_ticker} Capital Allocation & SEC 10-Q Disclosure Filing Review",
                "summary": f"Institutional desk reviews cash conversion cycles, return on invested capital, and operating leverage for {clean_ticker}.",
                "source": "US Market Intelligence Wire",
                "url": None,
                "published_at": now_iso,
                "country": "US",
                "market": "US",
                "ticker": clean_ticker,
                "symbols": [clean_ticker],
                "category": NewsCategory.MARKET.value,
                "event_type": NewsEventType.OTHER.value,
                "sentiment_label": "NEUTRAL",
                "sentiment_score": 0.15,
                "impact_score": 0.55,
                "data_source": NewsDataSource.US_PROVIDER.value,
                "data_status": NewsDataStatus.DEMO.value,
            }
            valid, article, _ = news_validator.validate_and_sanitize(synth_raw)
            if valid and article:
                matching.append(article)

        return matching[:limit]

    async def get_sector_news(self, sector: str, limit: int = 10) -> List[NewsArticleData]:
        all_articles = await self.get_latest_news(limit=50)
        filtered = [a for a in all_articles if a.sector and sector.lower() in a.sector.lower()]
        return filtered[:limit] if filtered else all_articles[:limit]

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
        if symbol:
            return await self.get_stock_news(symbol, limit=limit)
        return await self.get_latest_news(limit=limit)
