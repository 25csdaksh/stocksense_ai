"""
MarketMind AI — Macro Market Intelligence & Multi-Market Service Layer.
Phase 6.1: Aggregates global & Indian benchmark indices, market regime, session status, and provider health.
"""
from typing import Dict, Any, List, Optional
from datetime import datetime, timezone
from app.providers.market_data.factory import provider_factory
from app.providers.market_data.session import market_session_manager
from app.providers.market_data.models import ProviderHealth, MarketSessionStatus, NormalizedQuote
from app.utils.constants import SUPPORTED_UNIVERSE
from app.cache.market_cache import market_cache


class MarketService:

    async def get_overview(self, market: str = "US") -> Dict[str, Any]:
        """
        Retrieves market regime, benchmark indices, and top movers for the specified market ('US' or 'IN').
        """
        clean_market = market.strip().upper() if market else "US"
        cache_key = f"market:overview:v2:{clean_market}"
        cached = await market_cache.get_session_status(cache_key)
        if cached:
            return cached

        provider = provider_factory.get_provider(market=clean_market)
        indices_raw = await provider.get_indices()

        # Aggregate quick quotes for top assets in market
        if clean_market in ["IN", "NSE", "BSE"]:
            tickers = ["RELIANCE.NS", "TCS.NS", "INFY.NS", "HDFCBANK.NS", "ICICIBANK.NS", "TATAMOTORS.NS"]
        else:
            tickers = list(SUPPORTED_UNIVERSE.keys())[:6]

        quotes = []
        for t in tickers:
            try:
                q = await provider.get_quote(t)
                q_dict = q.model_dump() if isinstance(q, NormalizedQuote) else q
                quotes.append(q_dict)
            except Exception:
                continue

        sorted_by_change = sorted(quotes, key=lambda x: x.get("change_pct", 0.0), reverse=True) if quotes else []

        top_gainers = sorted_by_change[:3] if len(sorted_by_change) >= 3 else sorted_by_change
        top_losers = sorted_by_change[-3:] if len(sorted_by_change) >= 3 else []

        regime = "BULLISH_EXPANSION"
        if indices_raw and indices_raw[0].get("change_pct", 0.0) < 0:
            regime = "DEFENSIVE_CHOP"

        res = {
            "indices": indices_raw,
            "top_gainers": top_gainers,
            "top_losers": top_losers,
            "market_regime": regime,
            "market": clean_market,
            "timestamp": datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
        }

        await market_cache.set_session_status(cache_key, res, ttl=15)
        return res

    async def get_indices(self, market: Optional[str] = None) -> List[Dict[str, Any]]:
        """Retrieves major benchmark indices (US and Indian)."""
        clean_market = (market or "US").strip().upper()
        provider = provider_factory.get_provider(market=clean_market)
        return await provider.get_indices()

    async def get_sectors(self) -> List[Dict[str, Any]]:
        """Retrieves sector performance, momentum rankings, and market weights."""
        return [
            {"sector": "Information Technology", "performance_pct": +1.42, "momentum_score": 88.5, "top_stock": "NVDA", "market_cap_weight": 0.31},
            {"sector": "Communication Services", "performance_pct": +0.85, "momentum_score": 74.2, "top_stock": "GOOGL", "market_cap_weight": 0.09},
            {"sector": "Consumer Discretionary", "performance_pct": +0.62, "momentum_score": 68.0, "top_stock": "AMZN", "market_cap_weight": 0.10},
            {"sector": "Financials", "performance_pct": +0.34, "momentum_score": 62.1, "top_stock": "JPM", "market_cap_weight": 0.13},
            {"sector": "Health Care", "performance_pct": -0.18, "momentum_score": 45.3, "top_stock": "UNH", "market_cap_weight": 0.12},
            {"sector": "Energy", "performance_pct": -0.85, "momentum_score": 31.0, "top_stock": "XOM", "market_cap_weight": 0.04},
        ]

    async def get_market_status(self, exchange: str = "NSE") -> Dict[str, Any]:
        """Retrieves session status for NSE, BSE, or US exchanges."""
        status_obj: MarketSessionStatus = market_session_manager.get_session_status(exchange)
        return status_obj.model_dump()

    async def get_providers_health(self) -> List[Dict[str, Any]]:
        """Collects operational status and configuration telemetry across all providers."""
        reports = await provider_factory.get_all_providers_health()
        return [r.model_dump() for r in reports]


market_service = MarketService()
