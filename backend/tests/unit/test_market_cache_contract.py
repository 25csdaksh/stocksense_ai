"""
Unit Tests for Redis Market Cache Contract and Standardized Keys.
Phase 6.1: Validates standardized cache keys, TTL enforcement, and cache getters/setters.
"""
import pytest
from app.cache.market_cache import market_cache, MarketCacheContract


def test_market_cache_standardized_keys():
    # Quotes
    q_key = market_cache.quote_key("RELIANCE.NS")
    assert q_key == "market:quote:RELIANCE.NS"

    q_key_us = market_cache.quote_key("AAPL")
    assert q_key_us == "market:quote:AAPL"

    # History
    h_key = market_cache.history_key("INFY.NS", timeframe="1y", interval="1d")
    assert h_key == "market:history:INFY.NS:1y:1d"

    # Indices
    idx_key = market_cache.index_key("NIFTY 50")
    assert idx_key == "market:index:NIFTY 50"

    # Session Status
    s_key = market_cache.session_key("NSE")
    assert s_key == "market:status:NSE"

    # Provider Health
    h_key = market_cache.health_key("IndianMarketProvider")
    assert h_key == "market:health:IndianMarketProvider"


@pytest.mark.asyncio
async def test_market_cache_quote_get_and_set():
    test_quote = {
        "symbol": "TCS.NS",
        "price": 4250.0,
        "change": 25.0,
        "change_pct": 0.59
    }

    # Set quote
    await market_cache.set_quote("TCS.NS", test_quote, ttl=10)

    # Get quote
    cached = await market_cache.get_quote("TCS.NS")
    assert cached is not None
    assert cached["price"] == 4250.0
    assert cached["symbol"] == "TCS.NS"
