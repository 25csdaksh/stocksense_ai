"""
Unit Tests for Phase 6.8: OHLCV Gap Detector & Edge-Case Calibration.
Tests weekend calendar invariance, intraday gap detection thresholds,
divide-by-zero protection, invalid OHLC geometries, and error taxonomy mapping.
"""
import pytest
from datetime import datetime, timezone, timedelta
from app.observability.gap_detector import ohlcv_gap_detector, OHLCVGapDetector
from app.observability.models import ErrorCategory, AlertSeverity, QualityStatus
from app.observability.quality_engine import quality_engine
from app.observability.freshness_service import freshness_service
from app.observability.failure_log import failure_logger
from app.providers.market_data.models import HistoricalCandle


def test_gap_detector_weekend_invariance():
    """Verifies that Friday to Monday transitions (3-4 day difference) are not falsely flagged as missing data."""
    # Friday 2026-03-06 to Monday 2026-03-09
    friday_to_monday_candles = [
        HistoricalCandle(timestamp="2026-03-05T09:15:00Z", open=100.0, high=105.0, low=99.0, close=102.0, volume=1000),
        HistoricalCandle(timestamp="2026-03-06T09:15:00Z", open=102.0, high=108.0, low=101.0, close=106.0, volume=1200), # Friday
        HistoricalCandle(timestamp="2026-03-09T09:15:00Z", open=106.0, high=110.0, low=105.0, close=109.0, volume=1500), # Monday (3 days later)
    ]
    res = ohlcv_gap_detector.analyze_candles(friday_to_monday_candles, interval="1d")
    assert len(res["gaps_detected"]) == 0
    assert res["continuity_score"] == 100.0


def test_gap_detector_weekday_missing_trading_days():
    """Verifies that multi-day missing trading days during active week are flagged."""
    # Monday to Friday with Tuesday-Thursday missing (4+ days gap without weekend transition)
    missing_weekdays_candles = [
        HistoricalCandle(timestamp="2026-03-02T09:15:00Z", open=100.0, high=105.0, low=99.0, close=102.0, volume=1000), # Monday
        HistoricalCandle(timestamp="2026-03-10T09:15:00Z", open=102.0, high=108.0, low=101.0, close=106.0, volume=1200), # Next Tuesday (8 days later)
    ]
    res = ohlcv_gap_detector.analyze_candles(missing_weekdays_candles, interval="1d")
    assert len(res["gaps_detected"]) >= 1
    assert res["continuity_score"] < 100.0


def test_gap_detector_intraday_gaps():
    """Verifies intraday bar gaps (> 3x expected interval within same day)."""
    intraday_candles = [
        HistoricalCandle(timestamp="2026-03-02T09:15:00Z", open=100.0, high=105.0, low=99.0, close=102.0, volume=100),
        HistoricalCandle(timestamp="2026-03-02T09:20:00Z", open=102.0, high=103.0, low=101.0, close=102.5, volume=100),
        HistoricalCandle(timestamp="2026-03-02T10:30:00Z", open=102.5, high=104.0, low=102.0, close=103.5, volume=150), # 70 min gap for 5m interval
    ]
    res = ohlcv_gap_detector.analyze_candles(intraday_candles, interval="5m")
    assert len(res["gaps_detected"]) >= 1
    assert res["gaps_detected"][0]["gap_duration_minutes"] >= 60.0


def test_gap_detector_empty_candles():
    """Verifies handling of empty or None candle lists without division by zero."""
    res = ohlcv_gap_detector.analyze_candles([], interval="1d")
    assert res["total_candles"] == 0
    assert res["validity_score"] == 100.0
    assert res["continuity_score"] == 100.0


def test_error_taxonomy_categorization():
    """Verifies standard ErrorCategory classifications and AlertSeverity values."""
    assert ErrorCategory.VALIDATION_ERROR == "VALIDATION_ERROR"
    assert ErrorCategory.PROVIDER_ERROR == "PROVIDER_ERROR"
    assert ErrorCategory.AUTHENTICATION_ERROR == "AUTHENTICATION_ERROR"
    assert ErrorCategory.RATE_LIMIT_ERROR == "RATE_LIMIT_ERROR"
    assert ErrorCategory.TIMEOUT_ERROR == "TIMEOUT_ERROR"
    assert ErrorCategory.NETWORK_ERROR == "NETWORK_ERROR"
    assert ErrorCategory.DATABASE_ERROR == "DATABASE_ERROR"
    assert ErrorCategory.CACHE_ERROR == "CACHE_ERROR"
    assert ErrorCategory.VECTOR_DB_ERROR == "VECTOR_DB_ERROR"
    assert ErrorCategory.AI_PROVIDER_ERROR == "AI_PROVIDER_ERROR"
    assert ErrorCategory.STALE_DATA == "STALE_DATA"
    assert ErrorCategory.DATA_GAP == "DATA_GAP"
    assert ErrorCategory.DUPLICATE_DATA == "DUPLICATE_DATA"
    assert ErrorCategory.UNKNOWN_ERROR == "UNKNOWN_ERROR"

    assert AlertSeverity.INFO == "INFO"
    assert AlertSeverity.WARNING == "WARNING"
    assert AlertSeverity.CRITICAL == "CRITICAL"


def test_freshness_daily_candle_weekend_tolerance():
    """Verifies daily candles SLA accounts for weekend gaps."""
    now = datetime.now(timezone.utc)
    # 2 days old (typical weekend)
    weekend_ts = (now - timedelta(days=2)).isoformat()
    is_stale, age, score = freshness_service.evaluate_freshness("ohlcv", weekend_ts, "DEMO", interval="1d")
    assert not is_stale
    assert score == 100.0

    # 15 days old
    old_ts = (now - timedelta(days=15)).isoformat()
    is_stale_old, age_old, score_old = freshness_service.evaluate_freshness("ohlcv", old_ts, "DEMO", interval="1d")
    assert is_stale_old
    assert score_old < 50.0
