"""
Stock & Time-Series Data Service Layer.
"""
from typing import Dict, Any, List
from app.providers.market_data.factory import get_market_data_provider
from app.utils.constants import SUPPORTED_UNIVERSE
from app.utils.validators import validate_ticker, validate_timeframe, validate_interval
from app.cache.redis_client import cache_client


class StockService:

    def __init__(self):
        self.provider = get_market_data_provider()

    async def get_stock_universe(self) -> List[Dict[str, Any]]:
        assets = []
        for sym, meta in SUPPORTED_UNIVERSE.items():
            assets.append({
                "ticker": sym,
                "name": meta["name"],
                "sector": meta["sector"],
                "industry": meta.get("industry"),
                "beta": meta.get("beta", 1.0),
                "pe_ratio": meta.get("pe"),
                "pb_ratio": meta.get("pb"),
                "dividend_yield": meta.get("dividend_yield")
            })
        return assets

    async def get_quote(self, ticker: str) -> Dict[str, Any]:
        sym = validate_ticker(ticker)
        cache_key = f"stock:quote:{sym}"
        cached = await cache_client.get_json(cache_key)
        if cached:
            return cached

        res = await self.provider.get_quote(sym)
        await cache_client.set_json(cache_key, res, expire=5)
        return res

    async def get_history(self, ticker: str, timeframe: str = "6m", interval: str = "1d") -> Dict[str, Any]:
        sym = validate_ticker(ticker)
        tf = validate_timeframe(timeframe)
        iv = validate_interval(interval)

        cache_key = f"stock:history:{sym}:{tf}:{iv}"
        cached = await cache_client.get_json(cache_key)
        if cached:
            return cached

        res = await self.provider.get_history(sym, timeframe=tf, interval=iv)
        await cache_client.set_json(cache_key, res, expire=60)
        return res


stock_service = StockService()
