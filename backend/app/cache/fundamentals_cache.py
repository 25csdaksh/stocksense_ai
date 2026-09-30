"""
MarketMind AI — Standardized Fundamentals Redis Caching Contract.
Phase 6.6: Enforces structured cache key namespaces, isolated market scopes,
and deterministic TTLs for company profiles, statements, and ratios.
"""
from typing import Optional, List, Dict, Any
from app.cache.redis_client import cache_client
from app.providers.market_data.symbol_normalizer import normalize_symbol
from app.core.logging import logger


class FundamentalsCacheContract:
    """Standardized Redis cache keys & TTL policies for financial fundamentals."""

    TTL_PROFILE = 86400       # 24 hours
    TTL_OVERVIEW = 21600      # 6 hours
    TTL_STATEMENTS = 86400    # 24 hours
    TTL_RATIOS = 21600        # 6 hours

    @staticmethod
    def profile_key(symbol: str) -> str:
        norm = normalize_symbol(symbol)
        return f"fundamentals:profile:{norm.exchange.upper()}:{norm.canonical_symbol}"

    @staticmethod
    def overview_key(symbol: str) -> str:
        norm = normalize_symbol(symbol)
        return f"fundamentals:overview:{norm.exchange.upper()}:{norm.canonical_symbol}"

    @staticmethod
    def statements_key(symbol: str, statement_type: str = "income", period_type: str = "annual") -> str:
        norm = normalize_symbol(symbol)
        return f"fundamentals:statements:{norm.exchange.upper()}:{norm.canonical_symbol}:{statement_type.lower()}:{period_type.lower()}"

    @staticmethod
    def ratios_key(symbol: str) -> str:
        norm = normalize_symbol(symbol)
        return f"fundamentals:ratios:{norm.exchange.upper()}:{norm.canonical_symbol}"

    # =========================================================================
    # High-level Cache Getters & Setters
    # =========================================================================

    @classmethod
    async def get_profile(cls, symbol: str) -> Optional[Dict[str, Any]]:
        key = cls.profile_key(symbol)
        return await cache_client.get_json(key)

    @classmethod
    async def set_profile(cls, symbol: str, profile_data: Dict[str, Any], ttl: Optional[int] = None) -> bool:
        key = cls.profile_key(symbol)
        return await cache_client.set_json(key, profile_data, expire=ttl or cls.TTL_PROFILE)

    @classmethod
    async def get_overview(cls, symbol: str) -> Optional[Dict[str, Any]]:
        key = cls.overview_key(symbol)
        return await cache_client.get_json(key)

    @classmethod
    async def set_overview(cls, symbol: str, overview_data: Dict[str, Any], ttl: Optional[int] = None) -> bool:
        key = cls.overview_key(symbol)
        return await cache_client.set_json(key, overview_data, expire=ttl or cls.TTL_OVERVIEW)

    @classmethod
    async def get_statements(cls, symbol: str, statement_type: str = "income", period_type: str = "annual") -> Optional[Dict[str, Any]]:
        key = cls.statements_key(symbol, statement_type, period_type)
        return await cache_client.get_json(key)

    @classmethod
    async def set_statements(
        cls,
        symbol: str,
        statements_data: Dict[str, Any],
        statement_type: str = "income",
        period_type: str = "annual",
        ttl: Optional[int] = None
    ) -> bool:
        key = cls.statements_key(symbol, statement_type, period_type)
        return await cache_client.set_json(key, statements_data, expire=ttl or cls.TTL_STATEMENTS)

    @classmethod
    async def get_ratios(cls, symbol: str) -> Optional[Dict[str, Any]]:
        key = cls.ratios_key(symbol)
        return await cache_client.get_json(key)

    @classmethod
    async def set_ratios(cls, symbol: str, ratios_data: Dict[str, Any], ttl: Optional[int] = None) -> bool:
        key = cls.ratios_key(symbol)
        return await cache_client.set_json(key, ratios_data, expire=ttl or cls.TTL_RATIOS)

    @classmethod
    async def invalidate_symbol(cls, symbol: str) -> bool:
        """Evicts all fundamental cache keys for a given symbol."""
        try:
            await cache_client.delete(cls.profile_key(symbol))
            await cache_client.delete(cls.overview_key(symbol))
            await cache_client.delete(cls.ratios_key(symbol))
            for st in ["income", "balance_sheet", "cash_flow"]:
                for pt in ["annual", "quarterly", "ttm"]:
                    await cache_client.delete(cls.statements_key(symbol, st, pt))
            return True
        except Exception as e:
            logger.warning(f"Error invalidating cache for symbol {symbol}: {e}")
            return False


fundamentals_cache = FundamentalsCacheContract()
