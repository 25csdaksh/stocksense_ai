"""
Market Intelligence Service Layer.
"""
from typing import Dict, Any, List
from datetime import datetime
from app.providers.market_data.factory import get_market_data_provider
from app.utils.constants import SUPPORTED_UNIVERSE
from app.cache.redis_client import cache_client


class MarketService:

    def __init__(self):
        self.provider = get_market_data_provider()

    async def get_overview(self) -> Dict[str, Any]:
        cache_key = "market:overview:v1"
        cached = await cache_client.get_json(cache_key)
        if cached:
            return cached

        indices = await self.provider.get_indices()
        
        # Aggregate quick quotes for top assets
        tickers = list(SUPPORTED_UNIVERSE.keys())[:6]
        quotes = [await self.provider.get_quote(t) for t in tickers]
        sorted_by_change = sorted(quotes, key=lambda x: x["change_pct"], reverse=True)

        res = {
            "indices": indices,
            "top_gainers": sorted_by_change[:3],
            "top_losers": sorted_by_change[-3:],
            "market_regime": "BULLISH_EXPANSION" if indices[0]["change_pct"] > 0 else "DEFENSIVE_CHOP",
            "timestamp": datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC")
        }

        await cache_client.set_json(cache_key, res, expire=15)
        return res

    async def get_indices(self) -> List[Dict[str, Any]]:
        return await self.provider.get_indices()

    async def get_sectors(self) -> List[Dict[str, Any]]:
        return [
            {"sector": "Information Technology", "performance_pct": +1.42, "momentum_score": 88.5, "top_stock": "NVDA", "market_cap_weight": 0.31},
            {"sector": "Communication Services", "performance_pct": +0.85, "momentum_score": 74.2, "top_stock": "GOOGL", "market_cap_weight": 0.09},
            {"sector": "Consumer Discretionary", "performance_pct": +0.62, "momentum_score": 68.0, "top_stock": "AMZN", "market_cap_weight": 0.10},
            {"sector": "Financials", "performance_pct": +0.34, "momentum_score": 62.1, "top_stock": "JPM", "market_cap_weight": 0.13},
            {"sector": "Health Care", "performance_pct": -0.18, "momentum_score": 45.3, "top_stock": "UNH", "market_cap_weight": 0.12},
            {"sector": "Energy", "performance_pct": -0.85, "momentum_score": 31.0, "top_stock": "XOM", "market_cap_weight": 0.04},
        ]


market_service = MarketService()
