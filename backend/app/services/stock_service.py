"""
MarketMind AI — Stock & Time-Series Data Service Layer.
Phase 6.1: Multi-market routing across Indian (NSE/BSE) and US equities with standardized caching.
"""
from typing import Dict, Any, List, Optional
from app.providers.market_data.factory import provider_factory, get_market_data_provider
from app.providers.market_data.symbol_normalizer import normalize_symbol
from app.providers.market_data.models import NormalizedQuote, HistoricalDataResponse
from app.utils.constants import SUPPORTED_UNIVERSE
from app.providers.market_data.indian_market_provider import INDIAN_EQUITIES_UNIVERSE
from app.utils.validators import validate_ticker, validate_timeframe, validate_interval
from app.cache.market_cache import market_cache


class StockService:

    async def get_stock_universe(self) -> List[Dict[str, Any]]:
        """Aggregates all supported US and Indian assets in the universe."""
        assets = []
        # US Assets
        for sym, meta in SUPPORTED_UNIVERSE.items():
            assets.append({
                "ticker": sym,
                "name": meta["name"],
                "sector": meta["sector"],
                "industry": meta.get("industry"),
                "beta": meta.get("beta", 1.0),
                "pe_ratio": meta.get("pe"),
                "pb_ratio": meta.get("pb"),
                "dividend_yield": meta.get("dividend_yield"),
                "currency": "USD",
                "exchange": "NASDAQ" if sym in ["AAPL", "MSFT", "NVDA", "GOOGL", "AMZN", "TSLA", "QQQ"] else "NYSE"
            })
        # Indian Assets
        for sym, meta in INDIAN_EQUITIES_UNIVERSE.items():
            assets.append({
                "ticker": sym,
                "name": meta["name"],
                "sector": meta["sector"],
                "industry": meta.get("industry"),
                "beta": meta.get("beta", 1.0),
                "pe_ratio": meta.get("pe"),
                "pb_ratio": meta.get("pb"),
                "dividend_yield": meta.get("dividend_yield"),
                "currency": "INR",
                "exchange": meta.get("exchange", "NSE")
            })
        return assets

    async def get_quote(self, ticker: str) -> Dict[str, Any]:
        """Fetches real-time quote for any Indian or US asset with multi-market routing and caching."""
        sym = validate_ticker(ticker)
        norm = normalize_symbol(sym)
        canonical = norm.canonical_symbol

        cached = await market_cache.get_quote(canonical)
        if cached:
            return cached

        provider = provider_factory.get_provider(symbol=canonical)
        quote_obj = await provider.get_quote(canonical)
        res = quote_obj.model_dump() if isinstance(quote_obj, NormalizedQuote) else quote_obj

        await market_cache.set_quote(canonical, res, ttl=10)
        return res

    async def get_history(self, ticker: str, timeframe: str = "6m", interval: str = "1d") -> Dict[str, Any]:
        """Fetches historical OHLCV candlesticks with technical indicators."""
        sym = validate_ticker(ticker)
        norm = normalize_symbol(sym)
        canonical = norm.canonical_symbol
        tf = validate_timeframe(timeframe)
        iv = validate_interval(interval)

        cached = await market_cache.get_history(canonical, timeframe=tf, interval=iv)
        if cached:
            return cached

        provider = provider_factory.get_provider(symbol=canonical)
        hist_data = await provider.get_historical_data(canonical, timeframe=tf, interval=iv)

        if isinstance(hist_data, HistoricalDataResponse):
            res = {
                "ticker": hist_data.ticker,
                "timeframe": hist_data.timeframe,
                "interval": hist_data.interval,
                "currency": hist_data.currency,
                "bars": [b.model_dump() for b in hist_data.bars],
                "is_synthetic": hist_data.is_synthetic,
                "total_bars": hist_data.total_bars,
                "data_source": hist_data.data_source,
                "data_status": hist_data.data_status.value
            }
        else:
            res = hist_data

        await market_cache.set_history(canonical, res, timeframe=tf, interval=iv, ttl=300)
        return res

    async def get_fundamentals(self, ticker: str) -> Dict[str, Any]:
        """Fetches fundamental financial metrics for a symbol."""
        sym = validate_ticker(ticker)
        norm = normalize_symbol(sym)
        canonical = norm.canonical_symbol

        provider = provider_factory.get_provider(symbol=canonical)
        fund = await provider.get_fundamentals(canonical)
        return fund.model_dump()

    async def get_company_profile(self, ticker: str) -> Dict[str, Any]:
        """Fetches company profile and sector information."""
        sym = validate_ticker(ticker)
        norm = normalize_symbol(sym)
        canonical = norm.canonical_symbol

        provider = provider_factory.get_provider(symbol=canonical)
        prof = await provider.get_company_profile(canonical)
        return prof.model_dump()


stock_service = StockService()
