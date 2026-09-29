"""
Curated Financial News Provider with Sentiment & Market Impact Scoring.
"""
from typing import Dict, Any, List
from datetime import datetime, timedelta
from app.providers.news.base import NewsProvider


class MockNewsProvider(NewsProvider):

    SAMPLE_NEWS = [
        {
            "id": "news_nvda_1",
            "ticker": "NVDA",
            "title": "NVIDIA Blackwell GPU Platform Ramps Up Datacenter Volume Shipments",
            "summary": "Hyperscaler demand remains robust for high-performance generative AI accelerators, with supply commitments locking in double-digit sequential growth.",
            "source": "Bloomberg Financial",
            "url": "https://bloomberg.com/sample/nvda-blackwell",
            "published_at": (datetime.utcnow() - timedelta(hours=2)).strftime("%Y-%m-%d %H:%M:%S UTC"),
            "sentiment_label": "BULLISH",
            "sentiment_score": 0.82,
            "impact_score": 0.90
        },
        {
            "id": "news_aapl_1",
            "ticker": "AAPL",
            "title": "Apple Intelligence Hardware Cycle Gains Institutional Upgrade Endorsements",
            "summary": "Early device telemetry indicates strong enterprise and consumer upgrade intent across premium silicon models.",
            "source": "Reuters Financial",
            "url": "https://reuters.com/sample/aapl-intelligence",
            "published_at": (datetime.utcnow() - timedelta(hours=5)).strftime("%Y-%m-%d %H:%M:%S UTC"),
            "sentiment_label": "BULLISH",
            "sentiment_score": 0.68,
            "impact_score": 0.75
        },
        {
            "id": "news_msft_1",
            "ticker": "MSFT",
            "title": "Microsoft Azure Commercial Cloud Accelerates Operating Margins",
            "summary": "Enterprise adoption of Copilot and scalable cloud compute drives 180 bps gross margin expansion.",
            "source": "Wall Street Journal",
            "url": "https://wsj.com/sample/msft-azure",
            "published_at": (datetime.utcnow() - timedelta(hours=7)).strftime("%Y-%m-%d %H:%M:%S UTC"),
            "sentiment_label": "BULLISH",
            "sentiment_score": 0.74,
            "impact_score": 0.82
        },
        {
            "id": "news_spy_1",
            "ticker": "SPY",
            "title": "Federal Reserve Monetary Policy Committee Highlights Balanced Inflation Outlook",
            "summary": "Minutes from the latest FOMC meeting emphasize data-dependent calibration and resilient labor market conditions.",
            "source": "Financial Times",
            "url": "https://ft.com/sample/fed-minutes",
            "published_at": (datetime.utcnow() - timedelta(hours=12)).strftime("%Y-%m-%d %H:%M:%S UTC"),
            "sentiment_label": "BULLISH",
            "sentiment_score": 0.45,
            "impact_score": 0.88
        }
    ]

    async def get_news_for_ticker(self, ticker: str, limit: int = 5) -> List[Dict[str, Any]]:
        ticker = ticker.upper()
        matches = [n for n in self.SAMPLE_NEWS if n["ticker"] == ticker]
        if not matches:
            matches = [
                {
                    "id": f"gen_{ticker}_1",
                    "ticker": ticker,
                    "title": f"{ticker} Capital Allocation & Quarterly Free Cash Flow Assessment",
                    "summary": f"Institutional analysts examine capital expenditures, return on invested capital, and operating gross margins for {ticker}.",
                    "source": "Financial Intelligence Desk",
                    "url": None,
                    "published_at": datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC"),
                    "sentiment_label": "NEUTRAL",
                    "sentiment_score": 0.15,
                    "impact_score": 0.60
                }
            ]
        return matches[:limit]

    async def get_market_news(self, limit: int = 10) -> List[Dict[str, Any]]:
        return self.SAMPLE_NEWS[:limit]
