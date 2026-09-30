"""
Unit Tests for Market Data Provider Interface, Models, and Provenance.
Phase 6.1: Verifies Pydantic response models, normalized quote contracts, and data provenance.
"""
import pytest
from datetime import datetime, timezone
from app.providers.market_data.models import (
    NormalizedQuote,
    HistoricalCandle,
    HistoricalDataResponse,
    MarketIndexQuote,
    CompanyFundamentals,
    CompanyProfile,
    MarketSessionStatus,
    ProviderHealth,
    DataStatus,
    ProviderStatus,
    MarketSessionState
)


def test_normalized_quote_creation_and_provenance():
    now_iso = datetime.now(timezone.utc).isoformat()
    quote = NormalizedQuote(
        symbol="RELIANCE.NS",
        ticker="RELIANCE.NS",
        name="Reliance Industries Limited",
        exchange="NSE",
        currency="INR",
        price=2980.50,
        open=2970.0,
        high=2995.0,
        low=2965.0,
        previous_close=2960.0,
        change=20.50,
        change_percent=0.69,
        change_pct=0.69,
        volume=4500000.0,
        market_cap=20150000000000.0,
        pe_ratio=26.5,
        week_52_high=3200.0,
        week_52_low=2400.0,
        market_status="REGULAR",
        data_source="NSE_REALTIME",
        data_status=DataStatus.LIVE,
        is_synthetic=False,
        timestamp=now_iso
    )

    assert quote.symbol == "RELIANCE.NS"
    assert quote.price == 2980.50
    assert quote.currency == "INR"
    assert quote.data_status == DataStatus.LIVE
    assert quote.is_synthetic is False
    assert quote.change_pct == 0.69


def test_historical_candle_and_technical_indicators():
    now = datetime.now(timezone.utc)
    candle = HistoricalCandle(
        timestamp=now,
        time="2026-09-30",
        open=150.0,
        high=155.0,
        low=149.0,
        close=154.5,
        volume=1000000.0,
        adjusted_close=154.5,
        symbol="AAPL",
        exchange="NASDAQ",
        currency="USD",
        data_source="EXCHANGE_FEED",
        data_status=DataStatus.LIVE,
        sma_20=152.0,
        sma_50=148.0,
        ema_20=152.5,
        rsi_14=58.2,
        vwap=153.1
    )

    assert candle.close == 154.5
    assert candle.high >= max(candle.open, candle.close)
    assert candle.low <= min(candle.open, candle.close)
    assert candle.rsi_14 == 58.2


def test_provider_health_model():
    health = ProviderHealth(
        provider_name="IndianMarketProvider",
        market="NSE",
        status=ProviderStatus.CONFIGURATION_REQUIRED,
        configuration_status="Missing API keys for live licensed broker.",
        error_message="Credentials not provided.",
        requests_remaining=60,
        rate_limit_status="NORMAL"
    )

    assert health.status == ProviderStatus.CONFIGURATION_REQUIRED
    assert health.provider_name == "IndianMarketProvider"
    assert health.requests_remaining == 60
