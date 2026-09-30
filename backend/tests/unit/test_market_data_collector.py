"""
Unit Tests for MarketDataCollector Service (Phase 6.3).
Validates:
- Configurable symbol universe management
- Real-time quote collection with failure isolation
- Benchmark index collection
- Event streaming dispatch (QUOTE_TICK, INDEX_TICK)
- Data validation rejection handling
- Collector telemetry and cycle results
"""
import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from datetime import datetime, timezone

from app.services.market_data_collector import (
    MarketDataCollector,
    CollectionMode,
    CollectorCycleResult
)
from app.providers.market_data.models import (
    NormalizedQuote,
    MarketIndexQuote,
    DataStatus
)
from app.providers.market_data.streaming_events import (
    MarketDataEvent,
    MarketEventType,
    event_bus
)


@pytest.fixture
def collector():
    """Creates an isolated MarketDataCollector instance for testing."""
    c = MarketDataCollector()
    c.reset_default_universe()
    return c


# =============================================================================
# 1. Universe Management Tests
# =============================================================================

def test_collector_universe_management(collector):
    univ = collector.get_monitored_universe()
    assert "equities" in univ
    assert "indices" in univ
    assert "RELIANCE.NS" in univ["equities"]
    assert "NIFTY 50" in univ["indices"]

    # Add custom equity
    collector.add_symbol_to_universe("SBIN.NS")
    collector.add_symbol_to_universe("CUSTOM.NS")
    updated = collector.get_monitored_universe()
    assert "CUSTOM.NS" in updated["equities"]

    # Remove symbol
    assert collector.remove_symbol_from_universe("CUSTOM.NS") is True
    assert "CUSTOM.NS" not in collector.get_monitored_universe()["equities"]

    # Reset
    collector.reset_default_universe()
    assert len(collector.get_monitored_universe()["equities"]) >= 8


# =============================================================================
# 2. Quote Collection & Failure Isolation Tests
# =============================================================================

@pytest.mark.asyncio
async def test_collector_quote_collection_with_isolation(collector):
    valid_quote = NormalizedQuote(
        symbol="RELIANCE.NS",
        ticker="RELIANCE.NS",
        name="Reliance Industries",
        exchange="NSE",
        currency="INR",
        price=2980.5,
        open=2960.0,
        high=3010.0,
        low=2955.0,
        previous_close=2950.0,
        change=30.5,
        change_percent=1.03,
        volume=4500000,
        timestamp=datetime.now(timezone.utc).isoformat(),
        market_status="REGULAR",
        data_source="MOCK",
        data_status=DataStatus.LIVE
    )

    mock_provider = AsyncMock()
    # RELIANCE succeeds, INFY fails
    async def side_effect(symbol):
        if "RELIANCE" in symbol:
            return valid_quote
        raise TimeoutError("Network timeout during provider request")

    mock_provider.get_quote.side_effect = side_effect

    with patch("app.providers.market_data.factory.provider_factory.get_provider", return_value=mock_provider), \
         patch("app.cache.market_cache.market_cache.set_quote", new_callable=AsyncMock):

        res = await collector.collect_quotes(
            symbols=["RELIANCE.NS", "INFY.NS"],
            mode=CollectionMode.MANUAL
        )

        assert isinstance(res, CollectorCycleResult)
        assert res.records_requested == 2
        assert res.records_received == 1
        assert res.records_valid == 1
        assert len(res.quotes) == 1
        assert res.quotes[0].symbol == "RELIANCE.NS"

        # Failure isolation verified
        assert "INFY.NS" in res.failed_symbols


# =============================================================================
# 3. Data Validation Rejection in Collection Cycle
# =============================================================================

@pytest.mark.asyncio
async def test_collector_rejects_invalid_financial_quote(collector):
    # Construct invalid quote (price is negative)
    invalid_quote = NormalizedQuote(
        symbol="BADSTOCK.NS",
        ticker="BADSTOCK.NS",
        name="Bad Stock",
        exchange="NSE",
        currency="INR",
        price=-150.0,  # Negative price violates invariant
        open=100.0,
        high=110.0,
        low=90.0,
        previous_close=100.0,
        change=-50.0,
        change_percent=-50.0,
        volume=1000,
        timestamp=datetime.now(timezone.utc).isoformat(),
        market_status="REGULAR",
        data_source="MOCK",
        data_status=DataStatus.LIVE
    )

    mock_provider = AsyncMock()
    mock_provider.get_quote.return_value = invalid_quote

    with patch("app.providers.market_data.factory.provider_factory.get_provider", return_value=mock_provider):
        res = await collector.collect_quotes(symbols=["BADSTOCK.NS"], mode=CollectionMode.ON_DEMAND)
        assert res.records_received == 1
        assert res.records_rejected == 1
        assert res.records_valid == 0
        assert len(res.quotes) == 0


# =============================================================================
# 4. Streaming Event Bus Integration
# =============================================================================

@pytest.mark.asyncio
async def test_collector_publishes_streaming_events(collector):
    captured_events = []

    async def test_subscriber(event: MarketDataEvent):
        captured_events.append(event)

    event_bus.subscribe(test_subscriber)

    valid_quote = NormalizedQuote(
        symbol="TCS.NS",
        ticker="TCS.NS",
        name="Tata Consultancy Services",
        exchange="NSE",
        currency="INR",
        price=4250.0,
        open=4200.0,
        high=4280.0,
        low=4190.0,
        previous_close=4210.0,
        change=40.0,
        change_percent=0.95,
        volume=2100000,
        timestamp=datetime.now(timezone.utc).isoformat(),
        market_status="REGULAR",
        data_source="MOCK",
        data_status=DataStatus.LIVE
    )

    mock_provider = AsyncMock()
    mock_provider.get_quote.return_value = valid_quote

    with patch("app.providers.market_data.factory.provider_factory.get_provider", return_value=mock_provider), \
         patch("app.cache.market_cache.market_cache.set_quote", new_callable=AsyncMock):

        await collector.collect_quotes(symbols=["TCS.NS"], mode=CollectionMode.STREAMING_READY)

        assert len(captured_events) >= 1
        last_event = captured_events[-1]
        assert last_event.event_type == MarketEventType.QUOTE_TICK
        assert last_event.symbol == "TCS.NS"
        assert last_event.price == 4250.0

    event_bus.unsubscribe(test_subscriber)


# =============================================================================
# 5. Index Collection & Telemetry Tests
# =============================================================================

@pytest.mark.asyncio
async def test_collector_index_collection(collector):
    mock_indices = [
        MarketIndexQuote(
            symbol="^NSEI",
            name="NIFTY 50",
            exchange="NSE",
            price=24800.0,
            change=80.0,
            change_pct=0.32,
            currency="INR",
            timestamp=datetime.now(timezone.utc).isoformat(),
            data_source="MOCK",
            data_status=DataStatus.LIVE
        )
    ]

    mock_ind_provider = AsyncMock()
    mock_ind_provider.get_market_indices.return_value = mock_indices

    with patch("app.providers.market_data.factory.provider_factory.get_indian_provider", return_value=mock_ind_provider), \
         patch("app.cache.market_cache.market_cache.set_indices", new_callable=AsyncMock), \
         patch("app.services.market_ingestion_service.market_ingestion_service.ingest_indices", new_callable=AsyncMock, return_value=1):

        res = await collector.collect_indices(mode=CollectionMode.MANUAL)
        assert res.records_valid >= 1
        assert len(res.indices) >= 1
        assert res.indices[0].name == "NIFTY 50"


def test_collector_status_reporting(collector):
    status = collector.get_collector_status()
    assert status["status"] == "RUNNING"
    assert "monitored_universe" in status
    assert "total_symbols" in status["monitored_universe"]
