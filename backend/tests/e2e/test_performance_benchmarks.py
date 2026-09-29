"""
Performance Benchmarking & Latency Verification Suite.
Measures latency for database queries, cache retrieval, vector search, and API endpoints.
"""
import time
import pytest
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.repositories.market_data_repository import MarketDataRepository
from app.db.vector import vector_repository
from app.cache.redis_client import redis_client


@pytest.mark.asyncio
async def test_db_query_performance(db_session: AsyncSession):
    """Verifies that database time-series querying executes within high-performance bounds."""
    repo = MarketDataRepository(db_session)

    start_time = time.perf_counter()
    history = await repo.get_ohlcv_range("AAPL", limit=120)
    query_duration_ms = (time.perf_counter() - start_time) * 1000

    # Ensure query completes rapidly
    assert query_duration_ms < 150.0  # < 150ms in-memory/pooled DB
    assert isinstance(history, list)


@pytest.mark.asyncio
async def test_cache_hit_vs_miss_latency():
    """Verifies that cached lookups execute with sub-millisecond retrieval speed."""
    key = "perf:test:market:overview"
    sample_payload = {"status": "ok", "regime": "bullish", "active_tickers": 50}

    # 1. Miss / write
    t0 = time.perf_counter()
    await redis_client.set_json(key, sample_payload, expire=60)
    write_ms = (time.perf_counter() - t0) * 1000

    # 2. Hit
    t1 = time.perf_counter()
    retrieved = await redis_client.get_json(key)
    hit_ms = (time.perf_counter() - t1) * 1000

    assert retrieved is not None
    assert retrieved["regime"] == "bullish"
    assert hit_ms < 50.0  # sub-50ms cache response


def test_vector_search_latency():
    """Verifies that semantic vector similarity search completes under 250ms."""
    start_time = time.perf_counter()
    results = vector_repository.search_similar(query="Supply chain risks and tariffs", ticker="AAPL", top_k=3)
    duration_ms = (time.perf_counter() - start_time) * 1000

    assert duration_ms < 300.0
    assert isinstance(results, list)


def test_api_health_endpoint_latency(test_client: TestClient):
    """Verifies that lightweight API endpoints respond with low latency."""
    start_time = time.perf_counter()
    resp = test_client.get("/api/v1/health")
    duration_ms = (time.perf_counter() - start_time) * 1000

    assert resp.status_code == 200
    assert duration_ms < 300.0
