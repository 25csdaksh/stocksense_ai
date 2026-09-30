"""
Unit & Integration Tests for Phase 6.8: Data Quality, Observability & Health Platform.
Tests scoring formulas, freshness SLAs, failure logger sanitization, provider latency tracking,
infrastructure probes, symbol quality reports, and API health endpoints.
"""
import pytest
from datetime import datetime, timezone, timedelta
from httpx import AsyncClient, ASGITransport

from app.main import app
from app.observability.models import (
    QualityStatus,
    ProviderHealthStatus,
    AlertSeverity,
    ErrorCategory,
    QualityScoreBreakdown,
    DataQualityReport,
    SymbolDataQualityReport,
    GlobalDataQualityReport,
)
from app.observability.quality_engine import quality_engine, DataQualityEngine
from app.observability.freshness_service import freshness_service, DataFreshnessService
from app.observability.gap_detector import ohlcv_gap_detector, OHLCVGapDetector
from app.observability.provider_monitor import provider_monitor, ProviderHealthMonitor
from app.observability.failure_log import failure_logger, OperationalFailureLogger
from app.observability.infra_monitor import infra_monitor
from app.observability.quality_coordinator import quality_coordinator
from app.providers.market_data.models import HistoricalCandle


# =============================================================================
# 1. Deterministic Quality Score Engine Tests
# =============================================================================

def test_data_quality_score_weights():
    """Verifies that the composite score matches the exact documented dimension weights."""
    # 25% Freshness, 20% Completeness, 20% Validity, 15% Availability, 10% Consistency, 10% Continuity
    breakdown = quality_engine.calculate_score(
        freshness_score=100.0,
        completeness_score=100.0,
        validity_score=100.0,
        availability_score=100.0,
        consistency_score=100.0,
        continuity_score=100.0
    )
    assert breakdown.overall_score == 100.0

    partial = quality_engine.calculate_score(
        freshness_score=80.0,      # 80 * 0.25 = 20.0
        completeness_score=90.0,   # 90 * 0.20 = 18.0
        validity_score=100.0,      # 100 * 0.20 = 20.0
        availability_score=100.0,  # 100 * 0.15 = 15.0
        consistency_score=70.0,    # 70 * 0.10 = 7.0
        continuity_score=60.0      # 60 * 0.10 = 6.0
    )
    expected_sum = 20.0 + 18.0 + 20.0 + 15.0 + 7.0 + 6.0
    assert abs(partial.overall_score - expected_sum) < 0.01
    assert partial.overall_score == 86.0


def test_quality_status_derivation():
    """Verifies status categorization from score and anomaly flags."""
    assert quality_engine.derive_status_from_score(95.0) == QualityStatus.HEALTHY
    assert quality_engine.derive_status_from_score(75.0) == QualityStatus.DEGRADED
    assert quality_engine.derive_status_from_score(45.0) == QualityStatus.ERROR
    assert quality_engine.derive_status_from_score(95.0, is_stale=True) == QualityStatus.STALE
    assert quality_engine.derive_status_from_score(95.0, is_invalid=True) == QualityStatus.INVALID
    assert quality_engine.derive_status_from_score(95.0, is_unavailable=True) == QualityStatus.UNAVAILABLE


# =============================================================================
# 2. Freshness SLA Evaluator Tests
# =============================================================================

def test_freshness_evaluation():
    """Tests domain-specific SLA evaluation for quotes, fundamentals, and news."""
    now = datetime.now(timezone.utc)
    recent_ts = (now - timedelta(seconds=30)).isoformat()
    old_quote_ts = (now - timedelta(minutes=20)).isoformat()

    # Recent quote
    is_stale, age, score = freshness_service.evaluate_freshness("quotes", recent_ts, "LIVE")
    assert not is_stale
    assert age is not None and age <= 35.0
    assert score == 100.0

    # Old quote past SLA
    is_stale_old, age_old, score_old = freshness_service.evaluate_freshness("quotes", old_quote_ts, "LIVE")
    assert is_stale_old
    assert score_old < 60.0

    # Missing timestamp
    is_stale_none, _, score_none = freshness_service.evaluate_freshness("quotes", None)
    assert is_stale_none
    assert score_none == 30.0


# =============================================================================
# 3. OHLCV Gap & Mathematical Invariant Tests
# =============================================================================

def test_ohlcv_gap_and_bounds_detection():
    """Tests detection of inverted high/low bounds, negative volume, and timestamp ordering."""
    valid_candles = [
        HistoricalCandle(timestamp="2026-03-01T09:15:00Z", open=100.0, high=105.0, low=99.0, close=102.0, volume=1000),
        HistoricalCandle(timestamp="2026-03-02T09:15:00Z", open=102.0, high=108.0, low=101.0, close=106.0, volume=1200),
        HistoricalCandle(timestamp="2026-03-03T09:15:00Z", open=106.0, high=110.0, low=105.0, close=109.0, volume=1500),
    ]
    res = ohlcv_gap_detector.analyze_candles(valid_candles, interval="1d")
    assert res["validity_score"] == 100.0
    assert res["continuity_score"] == 100.0
    assert len(res["invalid_candles"]) == 0
    assert res["duplicates_count"] == 0

    # Candle with high < max(open, close) and negative volume
    invalid_candles = [
        HistoricalCandle(timestamp="2026-03-01T09:15:00Z", open=100.0, high=95.0, low=90.0, close=98.0, volume=-50),
        HistoricalCandle(timestamp="2026-03-01T09:15:00Z", open=100.0, high=105.0, low=99.0, close=102.0, volume=1000), # Duplicate ts
    ]
    res_inv = ohlcv_gap_detector.analyze_candles(invalid_candles, interval="1d")
    assert len(res_inv["invalid_candles"]) >= 1
    assert res_inv["duplicates_count"] == 1
    assert res_inv["validity_score"] < 100.0


# =============================================================================
# 4. Provider Latency & Health Tracking Tests
# =============================================================================

def test_provider_latency_percentiles():
    """Tests in-memory latency percentile calculations (p50, p95, p99, max) and error rates."""
    mon = ProviderHealthMonitor()
    for lat in [10.0, 20.0, 30.0, 40.0, 50.0, 60.0, 70.0, 80.0, 90.0, 100.0]:
        mon.record_request("TestProvider", success=True, latency_ms=lat)

    mon.record_request("TestProvider", success=False, latency_ms=250.0, is_rate_limited=True)

    rep = mon.get_provider_report("TestProvider")
    assert rep is not None
    assert rep.request_count == 11
    assert rep.success_count == 10
    assert rep.failure_count == 1
    assert rep.rate_limit_hits == 1
    assert rep.latency.p50_ms >= 50.0
    assert rep.latency.max_ms == 250.0
    assert rep.status == ProviderHealthStatus.RATE_LIMITED


# =============================================================================
# 5. Operational Failure Logger & Secret Sanitization Tests
# =============================================================================

def test_failure_logger_redaction():
    """Verifies that API keys, passwords, bearer tokens, and connection strings are redacted."""
    failure_logger.clear()
    leak_msg = "Failed to connect with api_key='sk-secret12345' and password='super_secret_pw' and bearer eyJhbGciOiJIUzI1NiJ9.test"
    rec = failure_logger.log_failure(
        component="MarketCollector",
        provider="ZerodhaKite",
        symbol="RELIANCE.NS",
        error_type=ErrorCategory.AUTHENTICATION_ERROR,
        severity=AlertSeverity.CRITICAL,
        message=leak_msg
    )

    assert "sk-secret12345" not in rec.message
    assert "super_secret_pw" not in rec.message
    assert "eyJhbGciOiJIUzI1NiJ9.test" not in rec.message
    assert "[REDACTED]" in rec.message

    recent = failure_logger.get_recent_failures(symbol="RELIANCE.NS")
    assert len(recent) == 1
    assert recent[0].component == "MarketCollector"


# =============================================================================
# 6. Infrastructure Monitor Tests
# =============================================================================

@pytest.mark.asyncio
async def test_infra_monitor_system_health():
    """Verifies asynchronous system health telemetry across DB, Redis, Qdrant, WS, and EventBus."""
    report = await infra_monitor.get_system_health()
    assert report.service == "MarketMind AI"
    assert "postgresql" in report.components
    assert "redis" in report.components
    assert "qdrant" in report.components
    assert "websocket" in report.components
    assert "event_bus" in report.components
    assert "ai_rag" in report.components
    assert len(report.providers) >= 4


# =============================================================================
# 7. Symbol & Global Quality Coordinator Tests
# =============================================================================

@pytest.mark.asyncio
async def test_symbol_quality_assessment():
    """Verifies 3-pillar data quality assessment for Indian and US tickers."""
    sym_rep = await quality_coordinator.assess_symbol_quality("RELIANCE.NS")
    assert sym_rep.symbol == "RELIANCE.NS"
    assert sym_rep.market_data.dataset == "market_data"
    assert sym_rep.fundamentals.dataset == "fundamentals"
    assert sym_rep.news.dataset == "news"
    assert 0.0 <= sym_rep.overall_score <= 100.0
    assert isinstance(sym_rep.market_data.data_source, str) and len(sym_rep.market_data.data_source) > 0


@pytest.mark.asyncio
async def test_global_quality_report():
    """Verifies top-level platform data quality overview."""
    glob_rep = await quality_coordinator.get_global_quality_report()
    assert 0.0 <= glob_rep.overall_score <= 100.0
    assert "INDIA" in glob_rep.markets
    assert "US" in glob_rep.markets
    assert "market_data" in glob_rep.dataset_scores
    assert "ZerodhaKite" in glob_rep.providers_summary


# =============================================================================
# 8. Observability & Health API Endpoints
# =============================================================================

@pytest.mark.asyncio
async def test_health_and_readiness_api_endpoints():
    """Tests GET /health, GET /ready, and GET /api/v1/system/health."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        # Public health check
        res_health = await ac.get("/health")
        assert res_health.status_code == 200
        data_h = res_health.json()
        assert data_h["status"] == "healthy"
        assert "components" in data_h

        # Readiness probe
        res_ready = await ac.get("/ready")
        assert res_ready.status_code == 200
        data_r = res_ready.json()
        assert "ready" in data_r
        assert data_r["ready"] is True

        # Detailed system health
        res_sys = await ac.get("/api/v1/system/health")
        assert res_sys.status_code == 200
        data_s = res_sys.json()
        assert "components" in data_s
        assert "providers" in data_s


@pytest.mark.asyncio
async def test_data_quality_api_endpoints():
    """Tests GET /api/v1/data-quality and GET /api/v1/data-quality/{symbol}."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        # Global overview
        res_global = await ac.get("/api/v1/data-quality")
        assert res_global.status_code == 200
        data_g = res_global.json()
        assert "overall_score" in data_g
        assert "markets" in data_g
        assert "dataset_scores" in data_g

        # Symbol quality
        res_sym = await ac.get("/api/v1/data-quality/TCS.NS")
        assert res_sym.status_code == 200
        data_sym = res_sym.json()
        assert data_sym["symbol"] == "TCS.NS"
        assert "market_data" in data_sym
        assert "fundamentals" in data_sym
        assert "news" in data_sym


@pytest.mark.asyncio
async def test_providers_and_observability_metrics_endpoints():
    """Tests GET /api/v1/providers/health and GET /api/v1/observability/metrics."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        # Providers health
        res_prov = await ac.get("/api/v1/providers/health")
        assert res_prov.status_code == 200
        prov_list = res_prov.json()
        assert isinstance(prov_list, list)
        assert len(prov_list) >= 4

        # Observability metrics
        res_met = await ac.get("/api/v1/observability/metrics")
        assert res_met.status_code == 200
        met_data = res_met.json()
        assert "metrics" in met_data
        assert "market_quote_latency_ms" in met_data["metrics"]
        assert "websocket_connections_active" in met_data["metrics"]
