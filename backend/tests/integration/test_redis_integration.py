"""
Integration Tests: Redis Cache Hit/Miss & TTL Expiration with Service Layer.
"""
import pytest
import time
from app.cache.redis_client import cache_client


@pytest.mark.asyncio
async def test_redis_cache_hit_and_miss_lifecycle():
    key = "stock:quote:TEST_AAPL"
    
    # 1. Cache Miss
    cached_miss = await cache_client.get_json(key)
    assert cached_miss is None

    # 2. Populate Cache
    quote_data = {"ticker": "TEST_AAPL", "price": 225.40, "cached": True}
    await cache_client.set_json(key, quote_data, expire=60)

    # 3. Cache Hit
    cached_hit = await cache_client.get_json(key)
    assert cached_hit is not None
    assert cached_hit["ticker"] == "TEST_AAPL"
    assert cached_hit["price"] == 225.40
    assert cached_hit["cached"] is True

    # 4. Invalidation / Delete
    await cache_client.delete(key)
    assert await cache_client.get_json(key) is None


@pytest.mark.asyncio
async def test_redis_cache_ttl_expiration_integration():
    key = "market:fast_tick"
    await cache_client.set(key, "tick_value", expire=1)
    
    assert await cache_client.get(key) == "tick_value"
    time.sleep(1.2)
    assert await cache_client.get(key) is None
