"""
MarketMind AI — Indian Equities Financial News Provider.
Phase 6.7: Comprehensive news feed for NSE/BSE listed equities, RBI monetary policy,
SEBI corporate governance, earnings announcements, and sector developments.
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


class IndianNewsProvider(BaseNewsProvider):
    """News provider adapter for Indian financial markets (NSE/BSE)."""

    def _get_curated_indian_articles(self) -> List[Dict[str, Any]]:
        now = datetime.now(timezone.utc)
        return [
            {
                "id": "news_in_rel_1",
                "headline": "Reliance Industries Approves 1:1 Bonus Share Issue as Retail & Jio Segments Hit Record PAT",
                "summary": "The Board of Reliance Industries announced a 1:1 bonus issue to reward shareholders following consolidated quarterly operating revenue expansion across telecom and new energy initiatives.",
                "source": "Mint Financial",
                "url": "https://livemint.com/market/reliance-bonus-issue-earnings-2026",
                "published_at": (now - timedelta(minutes=25)).isoformat(),
                "country": "IN",
                "market": "INDIA",
                "ticker": "RELIANCE.NS",
                "symbols": ["RELIANCE.NS"],
                "category": NewsCategory.CORPORATE_ACTION.value,
                "event_type": NewsEventType.BUYBACK.value,
                "sentiment_label": "BULLISH",
                "sentiment_score": 0.85,
                "impact_score": 0.92,
                "data_source": NewsDataSource.INDIAN_PROVIDER.value,
                "data_status": NewsDataStatus.DEMO.value,
            },
            {
                "id": "news_in_tcs_1",
                "headline": "TCS Signs $1.2B Mega Deal with European Retail Group for AI-Powered Supply Chain Migration",
                "summary": "Tata Consultancy Services expands its multi-year AI enterprise contract pipeline, locking in high-margin cloud infrastructure modernization through FY28.",
                "source": "Economic Times",
                "url": "https://economictimes.indiatimes.com/tech/tcs-mega-deal-europe-2026",
                "published_at": (now - timedelta(hours=1, minutes=10)).isoformat(),
                "country": "IN",
                "market": "INDIA",
                "ticker": "TCS.NS",
                "symbols": ["TCS.NS", "INFY.NS"],
                "category": NewsCategory.TECHNOLOGY.value,
                "event_type": NewsEventType.PARTNERSHIP.value,
                "sentiment_label": "BULLISH",
                "sentiment_score": 0.82,
                "impact_score": 0.86,
                "data_source": NewsDataSource.INDIAN_PROVIDER.value,
                "data_status": NewsDataStatus.DEMO.value,
            },
            {
                "id": "news_in_infy_1",
                "headline": "Infosys Raises Constant Currency Revenue Guidance to 4.5%–5.0% on Strong Large Deal Bookings",
                "summary": "Infosys reported solid Q3 FY26 operating performance, citing increased adoption of generative enterprise assistants across banking and financial services clients.",
                "source": "Financial Express",
                "url": "https://financialexpress.com/market/infosys-guidance-upgrade-2026",
                "published_at": (now - timedelta(hours=2, minutes=45)).isoformat(),
                "country": "IN",
                "market": "INDIA",
                "ticker": "INFY.NS",
                "symbols": ["INFY.NS", "TCS.NS"],
                "category": NewsCategory.EARNINGS.value,
                "event_type": NewsEventType.GUIDANCE_CHANGE.value,
                "sentiment_label": "BULLISH",
                "sentiment_score": 0.78,
                "impact_score": 0.84,
                "data_source": NewsDataSource.INDIAN_PROVIDER.value,
                "data_status": NewsDataStatus.DEMO.value,
            },
            {
                "id": "news_in_hdfc_1",
                "headline": "HDFC Bank Net Interest Margin Expands to 3.65% as Asset Quality & CASA Ratio Improve",
                "summary": "India's largest private lender posts 16% YoY loan book growth with gross NPA dropping to 1.18%, underscoring solid post-merger deposit accretion.",
                "source": "Business Standard",
                "url": "https://business-standard.com/banking/hdfc-bank-q3-nim-2026",
                "published_at": (now - timedelta(hours=4)).isoformat(),
                "country": "IN",
                "market": "INDIA",
                "ticker": "HDFCBANK.NS",
                "symbols": ["HDFCBANK.NS", "ICICIBANK.NS", "SBIN.NS"],
                "category": NewsCategory.EARNINGS.value,
                "event_type": NewsEventType.EARNINGS.value,
                "sentiment_label": "BULLISH",
                "sentiment_score": 0.74,
                "impact_score": 0.88,
                "data_source": NewsDataSource.INDIAN_PROVIDER.value,
                "data_status": NewsDataStatus.DEMO.value,
            },
            {
                "id": "news_in_rbi_1",
                "headline": "RBI MPC Keeps Repo Rate Unchanged at 6.50%; Projects FY27 Real GDP Growth at 7.2%",
                "summary": "Reserve Bank of India Governor stresses headline inflation alignment to the 4% target while acknowledging exceptional macroeconomic resilience across manufacturing and services.",
                "source": "NDTV Profit",
                "url": "https://ndtvprofit.com/economy/rbi-monetary-policy-decision-2026",
                "published_at": (now - timedelta(hours=6)).isoformat(),
                "country": "IN",
                "market": "INDIA",
                "ticker": "^NSEI",
                "symbols": ["^NSEI", "^BSESN", "HDFCBANK.NS", "SBIN.NS"],
                "category": NewsCategory.MACRO.value,
                "event_type": NewsEventType.MACRO_EVENT.value,
                "sentiment_label": "NEUTRAL",
                "sentiment_score": 0.25,
                "impact_score": 0.90,
                "data_source": NewsDataSource.INDIAN_PROVIDER.value,
                "data_status": NewsDataStatus.DEMO.value,
            },
            {
                "id": "news_in_tatamotors_1",
                "headline": "Tata Motors Demerger Plan Receives NCLT Final Approval; Commercial & Passenger Entities To Trade Separately",
                "summary": "Tata Motors moves forward with corporate reorganization into two pure-play listed entities, unlocking distinct capital allocation for EV passenger mobility and global commercial fleets.",
                "source": "CNBC-TV18",
                "url": "https://cnbctv18.com/auto/tata-motors-demerger-nclt-nod-2026",
                "published_at": (now - timedelta(hours=8)).isoformat(),
                "country": "IN",
                "market": "INDIA",
                "ticker": "TATAMOTORS.NS",
                "symbols": ["TATAMOTORS.NS"],
                "category": NewsCategory.CORPORATE_ACTION.value,
                "event_type": NewsEventType.SPINOFF.value,
                "sentiment_label": "BULLISH",
                "sentiment_score": 0.70,
                "impact_score": 0.85,
                "data_source": NewsDataSource.INDIAN_PROVIDER.value,
                "data_status": NewsDataStatus.DEMO.value,
            },
            {
                "id": "news_in_itc_1",
                "headline": "ITC Hotels Listing Expected by End of Month as Shareholder Allotment Process Concludes",
                "summary": "ITC completes demerger formalities for hospitality business, with institutional brokerages assigning attractive sum-of-the-parts valuations.",
                "source": "The Hindu BusinessLine",
                "url": "https://thehindubusinessline.com/markets/itc-hotels-listing-update-2026",
                "published_at": (now - timedelta(hours=10)).isoformat(),
                "country": "IN",
                "market": "INDIA",
                "ticker": "ITC.NS",
                "symbols": ["ITC.NS"],
                "category": NewsCategory.CORPORATE_ACTION.value,
                "event_type": NewsEventType.SPINOFF.value,
                "sentiment_label": "BULLISH",
                "sentiment_score": 0.65,
                "impact_score": 0.72,
                "data_source": NewsDataSource.INDIAN_PROVIDER.value,
                "data_status": NewsDataStatus.DEMO.value,
            }
        ]

    async def get_latest_news(self, limit: int = 20) -> List[NewsArticleData]:
        raw_list = self._get_curated_indian_articles()
        results: List[NewsArticleData] = []
        for raw in raw_list[:limit]:
            valid, article, _ = news_validator.validate_and_sanitize(raw)
            if valid and article:
                results.append(article)
        return results

    async def get_stock_news(self, symbol: str, limit: int = 10) -> List[NewsArticleData]:
        norm = symbol_normalizer.normalize(symbol).display_symbol or symbol.upper()
        raw_list = self._get_curated_indian_articles()
        matching = []
        for raw in raw_list:
            symbols = raw.get("symbols", [])
            if norm in symbols or raw.get("ticker") == norm or any(norm in s for s in symbols):
                valid, article, _ = news_validator.validate_and_sanitize(raw)
                if valid and article:
                    matching.append(article)

        if not matching:
            # Fallback normalized article for queried Indian ticker
            clean_ticker = norm
            now_iso = datetime.now(timezone.utc).isoformat()
            synth_raw = {
                "id": f"gen_in_{clean_ticker}_1",
                "headline": f"{clean_ticker} Quarterly Financial Statement Analysis & Institutional Flow Monitor",
                "summary": f"Market intelligence telemetry highlights institutional positioning, cash flow stability, and corporate governance metrics for {clean_ticker}.",
                "source": "National Exchange Market Wire",
                "url": None,
                "published_at": now_iso,
                "country": "IN",
                "market": "INDIA",
                "ticker": clean_ticker,
                "symbols": [clean_ticker],
                "category": NewsCategory.MARKET.value,
                "event_type": NewsEventType.OTHER.value,
                "sentiment_label": "NEUTRAL",
                "sentiment_score": 0.10,
                "impact_score": 0.50,
                "data_source": NewsDataSource.INDIAN_PROVIDER.value,
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
