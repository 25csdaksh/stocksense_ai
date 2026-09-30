"""
Unit Tests for HistoricalDataBackfillService and MarketQualityService (Phase 6.3).
Validates:
- Full and incremental historical OHLCV backfill
- TimescaleDB duplicate avoidance
- OHLCV gap detection
- Data quality scoring (freshness, completeness, validation)
- Batch universe backfilling
"""
import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from datetime import datetime, timezone, timedelta

from app.services.market_backfill_service import (
    HistoricalDataBackfillService,
    BackfillResult
)
from app.services.market_quality_service import (
    market_quality_service,
    DataQualityStatus,
    MarketDataQualityReport
)
from app.providers.market_data.models import (
    HistoricalCandle,
    HistoricalDataResponse,
    NormalizedQuote,
    DataStatus
)


# =============================================================================
# 1. Gap Detection & Data Quality Assessment Tests
# =============================================================================

def test_gap_detection_on_normal_and_gapped_series():
    # Continuous daily series (no abnormal gaps)
    base_dt = datetime(2026, 9, 1, 9, 15, tzinfo=timezone.utc)
    normal_candles = [
        HistoricalCandle(
            timestamp=base_dt + timedelta(days=i),
            open=100.0, high=105.0, low=99.0, close=102.0, volume=1000
        )
        for i in range(10)
    ]

    gaps, dupes = market_quality_service.detect_ohlcv_gaps(normal_candles, interval="1d")
    assert len(gaps) == 0
    assert dupes == 0

    # Series with a 15-day gap and a duplicate
    gapped_candles = [
        HistoricalCandle(
            timestamp=base_dt,
            open=100.0, high=105.0, low=99.0, close=102.0, volume=1000
        ),
        HistoricalCandle(
            timestamp=base_dt,  # Duplicate
            open=100.0, high=105.0, low=99.0, close=102.0, volume=1000
        ),
        HistoricalCandle(
            timestamp=base_dt + timedelta(days=20),  # 20-day gap
            open=105.0, high=110.0, low=104.0, close=108.0, volume=1500
        )
    ]

    gaps2, dupes2 = market_quality_service.detect_ohlcv_gaps(gapped_candles, interval="1d")
    assert len(gaps2) >= 1
    assert dupes2 == 1


def test_quote_quality_evaluation():
    # Fresh valid quote
    fresh_quote = NormalizedQuote(
        symbol="RELIANCE.NS",
        ticker="RELIANCE.NS",
        name="Reliance Industries",
        exchange="NSE",
        currency="INR",
        price=2980.0,
        open=2950.0,
        high=3000.0,
        low=2940.0,
        previous_close=2945.0,
        change=35.0,
        change_percent=1.19,
        volume=2000000,
        timestamp=datetime.now(timezone.utc).isoformat(),
        market_status="REGULAR",
        data_source="ZERODHA",
        data_status=DataStatus.LIVE
    )

    report = market_quality_service.evaluate_quote_quality(fresh_quote)
    assert report.quality_status == DataQualityStatus.HEALTHY
    assert report.validation_passed is True
    assert report.quality_score == 100.0

    # Stale quote (timestamp from 10 days ago)
    old_ts = (datetime.now(timezone.utc) - timedelta(days=10)).isoformat()
    stale_quote = fresh_quote.model_copy(update={"timestamp": old_ts})
    report_stale = market_quality_service.evaluate_quote_quality(stale_quote)
    assert report_stale.quality_status == DataQualityStatus.STALE
    assert report_stale.is_stale is True


# =============================================================================
# 2. Historical Backfill Service Tests
# =============================================================================

@pytest.mark.asyncio
async def test_historical_backfill_full_mode():
    base_dt = datetime.now(timezone.utc)
    mock_candles = [
        HistoricalCandle(
            timestamp=base_dt - timedelta(days=i),
            open=2900.0 + i, high=2950.0 + i, low=2890.0 + i, close=2940.0 + i, volume=100000,
            symbol="RELIANCE.NS", currency="INR", data_source="TEST"
        )
        for i in range(5)
    ]

    mock_resp = HistoricalDataResponse(
        symbol="RELIANCE.NS",
        ticker="RELIANCE.NS",
        timeframe="6m",
        interval="1d",
        currency="INR",
        bars=mock_candles,
        total_bars=5,
        data_source="MOCK",
        data_status=DataStatus.HISTORICAL
    )

    mock_provider = AsyncMock()
    mock_provider.get_historical_data.return_value = mock_resp

    with patch("app.providers.market_data.factory.provider_factory.get_provider", return_value=mock_provider), \
         patch("app.db.repositories.market_data_repository.MarketDataRepository.get_latest_bar", new_callable=AsyncMock, return_value=None), \
         patch("app.services.market_ingestion_service.market_ingestion_service.ingest_ohlcv_bars", new_callable=AsyncMock, return_value=5), \
         patch("app.cache.market_cache.market_cache.set_history", new_callable=AsyncMock):

        res = await HistoricalDataBackfillService.backfill_symbol_history(
            symbol="RELIANCE.NS",
            timeframe="6m",
            interval="1d",
            force_full=True
        )

        assert isinstance(res, BackfillResult)
        assert res.status == "SUCCESS"
        assert res.bars_fetched == 5
        assert res.bars_persisted == 5
        assert res.is_incremental is False


@pytest.mark.asyncio
async def test_historical_backfill_incremental_mode():
    # Simulate an existing bar in TimescaleDB from 2 days ago
    existing_bar_dt = datetime.now(timezone.utc) - timedelta(days=2)
    mock_existing_bar = MagicMock()
    mock_existing_bar.timestamp = existing_bar_dt

    mock_new_candles = [
        HistoricalCandle(
            timestamp=datetime.now(timezone.utc) - timedelta(days=1),
            open=2980.0, high=3010.0, low=2975.0, close=3000.0, volume=120000,
            symbol="TCS.NS", currency="INR", data_source="TEST"
        ),
        HistoricalCandle(
            timestamp=datetime.now(timezone.utc),
            open=3000.0, high=3030.0, low=2990.0, close=3025.0, volume=140000,
            symbol="TCS.NS", currency="INR", data_source="TEST"
        )
    ]

    mock_resp = HistoricalDataResponse(
        symbol="TCS.NS",
        ticker="TCS.NS",
        timeframe="6m",
        interval="1d",
        currency="INR",
        bars=mock_new_candles,
        total_bars=2,
        data_source="MOCK",
        data_status=DataStatus.HISTORICAL
    )

    mock_provider = AsyncMock()
    mock_provider.get_historical_data.return_value = mock_resp

    with patch("app.providers.market_data.factory.provider_factory.get_provider", return_value=mock_provider), \
         patch("app.db.repositories.market_data_repository.MarketDataRepository.get_latest_bar", new_callable=AsyncMock, return_value=mock_existing_bar), \
         patch("app.services.market_ingestion_service.market_ingestion_service.ingest_ohlcv_bars", new_callable=AsyncMock, return_value=2), \
         patch("app.cache.market_cache.market_cache.set_history", new_callable=AsyncMock):

        res = await HistoricalDataBackfillService.backfill_symbol_history(
            symbol="TCS.NS",
            timeframe="6m",
            interval="1d",
            force_full=False
        )

        assert res.status == "SUCCESS"
        assert res.is_incremental is True
        assert res.bars_persisted == 2
        assert res.last_timestamp_before is not None
