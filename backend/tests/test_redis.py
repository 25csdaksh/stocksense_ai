"""
Redis Cache Client & In-Memory Fallback Unit Tests.
"""
import pytest
import time
from app.cache.redis_client import RedisCacheClient


@pytest.mark.asyncio
async def test_redis_cache_client_in_memory_fallback():
    client = RedisCacheClient()
    # Ensure offline fallback mode
    client.is_connected = False
    client._client = None

    # Test String Set/Get
    await client.set("test_key_1", "marketmind_value", expire=60)
    val = await client.get("test_key_1")
    assert val == "marketmind_value"

    # Test JSON Set/Get
    sample_payload = {
        "ticker": "AAPL",
        "price": 228.50,
        "metrics": {"pe": 33.2, "beta": 1.12}
    }
    await client.set_json("test_quote:AAPL", sample_payload, expire=60)
    retrieved_json = await client.get_json("test_quote:AAPL")
    assert retrieved_json is not None
    assert retrieved_json["ticker"] == "AAPL"
    assert retrieved_json["price"] == 228.50
    assert retrieved_json["metrics"]["beta"] == 1.12

    # Test Delete
    await client.delete("test_key_1")
    deleted_val = await client.get("test_key_1")
    assert deleted_val is None


@pytest.mark.asyncio
async def test_redis_cache_ttl_expiration():
    client = RedisCacheClient()
    client.is_connected = False
    client._client = None

    # Set key with 1 second TTL
    await client.set("short_lived_key", "expires_soon", expire=1)
    val_immediate = await client.get("short_lived_key")
    assert val_immediate == "expires_soon"

    # Sleep past expiration
    time.sleep(1.2)
    val_expired = await client.get("short_lived_key")
    assert val_expired is None
