"""
MarketMind AI — Standardized Market Data Redis Caching Contract.
Phase 6.1: Enforces standardized cache key formats, TTLs, and serialized model caching.
"""
from typing import Optional, List, Dict, Any
from app.cache.redis_client import cache_client
from app.providers.market_data.models import (
    NormalizedQuote,
    HistoricalDataResponse,
    MarketIndexQuote,
    MarketSessionStatus,
    ProviderHealth
)
from app.providers.market_data.symbol_normalizer import normalize_symbol
from app.core.logging import logger


class MarketCacheContract:
    """Standardized keys and TTL policies for all market data cache entries."""

    # Default TTLs in seconds
    TTL_QUOTE = 10
    TTL_HISTORY = 300
    TTL_INDEX = 15
    TTL_SESSION = 60
    TTL_HEALTH = 30
    TTL_INSTRUMENT = 86400  # 24 hours for instrument master & tokens

    @staticmethod
    def quote_key(symbol: str) -> str:
        norm = normalize_symbol(symbol)
        return f"market:quote:{norm.canonical_symbol}"

    @staticmethod
    def instrument_key(exchange: str, tradingsymbol: str) -> str:
        return f"market:instrument:{exchange.strip().upper()}:{tradingsymbol.strip().upper()}"

    @staticmethod
    def history_key(symbol: str, timeframe: str = "6m", interval: str = "1d") -> str:
        norm = normalize_symbol(symbol)
        return f"market:history:{norm.canonical_symbol}:{timeframe.lower()}:{interval.lower()}"

    @staticmethod
    def index_key(symbol_or_market: str) -> str:
        clean = symbol_or_market.strip().upper()
        return f"market:index:{clean}"

    @staticmethod
    def session_key(exchange_or_market: str) -> str:
        clean = exchange_or_market.strip().upper()
        return f"market:status:{clean}"

    @staticmethod
    def health_key(provider_name: str) -> str:
        clean = provider_name.strip()
        return f"market:health:{clean}"

    # =========================================================================
    # High-level Cache Getters & Setters
    # =========================================================================

    @classmethod
    async def get_quote(cls, symbol: str) -> Optional[Dict[str, Any]]:
        key = cls.quote_key(symbol)
        return await cache_client.get_json(key)

    @classmethod
    async def set_quote(cls, symbol: str, quote_data: Dict[str, Any], ttl: Optional[int] = None) -> bool:
        key = cls.quote_key(symbol)
        return await cache_client.set_json(key, quote_data, expire=ttl or cls.TTL_QUOTE)

    @classmethod
    async def get_history(cls, symbol: str, timeframe: str = "6m", interval: str = "1d") -> Optional[Dict[str, Any]]:
        key = cls.history_key(symbol, timeframe, interval)
        return await cache_client.get_json(key)

    @classmethod
    async def set_history(
        cls,
        symbol: str,
        history_data: Dict[str, Any],
        timeframe: str = "6m",
        interval: str = "1d",
        ttl: Optional[int] = None
    ) -> bool:
        key = cls.history_key(symbol, timeframe, interval)
        return await cache_client.set_json(key, history_data, expire=ttl or cls.TTL_HISTORY)

    @classmethod
    async def get_indices(cls, market: str = "ALL") -> Optional[List[Dict[str, Any]]]:
        key = cls.index_key(market)
        return await cache_client.get_json(key)

    @classmethod
    async def set_indices(cls, market: str, indices_data: List[Dict[str, Any]], ttl: Optional[int] = None) -> bool:
        key = cls.index_key(market)
        return await cache_client.set_json(key, indices_data, expire=ttl or cls.TTL_INDEX)

    @classmethod
    async def get_session_status(cls, exchange_or_market: str) -> Optional[Dict[str, Any]]:
        key = cls.session_key(exchange_or_market)
        return await cache_client.get_json(key)

    @classmethod
    async def set_session_status(
        cls,
        exchange_or_market: str,
        status_data: Dict[str, Any],
        ttl: Optional[int] = None
    ) -> bool:
        key = cls.session_key(exchange_or_market)
        return await cache_client.set_json(key, status_data, expire=ttl or cls.TTL_SESSION)

    @classmethod
    async def get_instrument_token(cls, exchange: str, tradingsymbol: str) -> Optional[int]:
        key = cls.instrument_key(exchange, tradingsymbol)
        data = await cache_client.get_json(key)
        if data and isinstance(data, dict) and "token" in data:
            return data["token"]
        elif isinstance(data, int):
            return data
        return None

    @classmethod
    async def set_instrument_token(
        cls,
        exchange: str,
        tradingsymbol: str,
        token: int,
        ttl: Optional[int] = None
    ) -> bool:
        key = cls.instrument_key(exchange, tradingsymbol)
        return await cache_client.set_json(key, {"token": token}, expire=ttl or cls.TTL_INSTRUMENT)


market_cache = MarketCacheContract()
