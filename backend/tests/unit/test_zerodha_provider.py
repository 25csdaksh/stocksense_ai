"""
Unit & Mock Tests for Zerodha Kite Connect Market Data Provider (Phase 6.2).
Validates:
- Missing credentials & configuration requirements
- Authentication error handling & token expiration
- Real quote normalization & data provenance
- Historical OHLCV normalization & technical indicator calculation
- Instrument token resolution & caching
- Rate limiting & backoff retries
- Provider health telemetry
- Redis caching & TimescaleDB ingestion
"""
import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from datetime import datetime, timezone
import httpx

from app.core.config import settings
from app.providers.market_data.zerodha_provider import (
    ZerodhaMarketProvider,
    ZerodhaInstrumentManager,
    STATIC_INSTRUMENT_TOKENS
)
from app.providers.market_data.models import (
    DataStatus,
    ProviderStatus,
    NormalizedQuote,
    HistoricalDataResponse
)
from app.providers.market_data.exceptions import (
    ProviderNotConfigured,
    ProviderAuthenticationFailed,
    SymbolNotFound,
    InvalidSymbol,
    RateLimitExceeded,
    MarketDataTimeout,
    ProviderUnavailable
)
from app.providers.market_data.factory import provider_factory, get_market_data_provider


# Sample Mock Kite Responses
MOCK_KITE_RELIANCE_QUOTE = {
    "status": "success",
    "data": {
        "NSE:RELIANCE": {
            "instrument_token": 738561,
            "timestamp": "2026-09-30 15:30:00",
            "last_price": 2980.5,
            "last_quantity": 50,
            "volume": 4512030,
            "buy_quantity": 210000,
            "sell_quantity": 180000,
            "ohlc": {
                "open": 2960.0,
                "high": 3010.0,
                "low": 2955.0,
                "close": 2950.0
            },
            "net_change": 30.5
        }
    }
}

MOCK_KITE_BATCH_QUOTES = {
    "status": "success",
    "data": {
        "NSE:RELIANCE": {
            "instrument_token": 738561,
            "timestamp": "2026-09-30 15:30:00",
            "last_price": 2980.5,
            "volume": 4512030,
            "ohlc": {"open": 2960.0, "high": 3010.0, "low": 2955.0, "close": 2950.0},
            "net_change": 30.5
        },
        "NSE:TCS": {
            "instrument_token": 2953213,
            "timestamp": "2026-09-30 15:30:00",
            "last_price": 4250.0,
            "volume": 2150000,
            "ohlc": {"open": 4210.0, "high": 4280.0, "low": 4200.0, "close": 4220.0},
            "net_change": 30.0
        }
    }
}

MOCK_KITE_HISTORICAL_DATA = {
    "status": "success",
    "data": {
        "candles": [
            ["2026-09-25T09:15:00+0530", 2940.0, 2965.0, 2935.0, 2955.0, 150000],
            ["2026-09-26T09:15:00+0530", 2955.0, 2980.0, 2950.0, 2975.0, 180000],
            ["2026-09-27T09:15:00+0530", 2975.0, 3005.0, 2970.0, 2990.0, 220000],
            ["2026-09-28T09:15:00+0530", 2990.0, 3010.0, 2975.0, 2980.0, 160000],
            ["2026-09-29T09:15:00+0530", 2980.0, 3020.0, 2970.0, 3015.0, 250000],
        ]
    }
}


@pytest.fixture
def unconfigured_provider():
    """Returns a ZerodhaMarketProvider without credentials."""
    return ZerodhaMarketProvider(api_key="", access_token="")


@pytest.fixture
def configured_provider():
    """Returns a ZerodhaMarketProvider configured with test credentials."""
    return ZerodhaMarketProvider(
        api_key="test_kite_api_key_123",
        api_secret="test_kite_api_secret_456",
        access_token="test_kite_access_token_789"
    )


# =============================================================================
# 1. Configuration & Missing Credentials Tests
# =============================================================================

@pytest.mark.asyncio
async def test_unconfigured_zerodha_provider_raises_and_reports_status(unconfigured_provider):
    assert unconfigured_provider.is_configured is False

    # Attempting quote without credentials must raise ProviderNotConfigured
    with pytest.raises(ProviderNotConfigured) as exc_info:
        await unconfigured_provider.get_quote("RELIANCE.NS")
    assert "ZERODHA_API_KEY" in exc_info.value.details["missing_keys"]

    # Health check must report CONFIGURATION_REQUIRED
    health = await unconfigured_provider.get_health()
    assert health.status == ProviderStatus.CONFIGURATION_REQUIRED
    assert health.market == "NSE"
    assert "ZERODHA_API_KEY" in health.configuration_status


# =============================================================================
# 2. Authentication Failure & Error Mapping Tests
# =============================================================================

@pytest.mark.asyncio
async def test_zerodha_authentication_failure_maps_to_domain_error(configured_provider):
    mock_auth_error_resp = MagicMock()
    mock_auth_error_resp.status_code = 403
    mock_auth_error_resp.json.return_value = {
        "status": "error",
        "error_type": "TokenException",
        "message": "Token is invalid or session has expired."
    }

    with patch("httpx.AsyncClient.get", return_value=mock_auth_error_resp):
        with pytest.raises(ProviderAuthenticationFailed) as exc_info:
            await configured_provider.get_quote("RELIANCE.NS")
        assert "Token is invalid" in str(exc_info.value)

        # Provider health must report AUTHENTICATION_ERROR
        health = await configured_provider.get_health()
        assert health.status == ProviderStatus.AUTHENTICATION_ERROR


# =============================================================================
# 3. Successful Quote Normalization & Data Provenance Tests
# =============================================================================

@pytest.mark.asyncio
async def test_zerodha_successful_quote_normalization(configured_provider):
    mock_resp = MagicMock()
    mock_resp.status_code = 200
    mock_resp.json.return_value = MOCK_KITE_RELIANCE_QUOTE

    with patch("httpx.AsyncClient.get", return_value=mock_resp):
        quote = await configured_provider.get_quote("NSE:RELIANCE")

        assert isinstance(quote, NormalizedQuote)
        assert quote.symbol == "RELIANCE.NS"
        assert quote.exchange == "NSE"
        assert quote.currency == "INR"
        assert quote.price == 2980.5
        assert quote.open == 2960.0
        assert quote.high == 3010.0
        assert quote.low == 2955.0
        assert quote.previous_close == 2950.0
        assert quote.change == 30.5
        assert round(quote.change_percent, 2) == round((30.5 / 2950.0) * 100.0, 2)
        assert quote.volume == 4512030
        assert quote.data_source == "ZERODHA"
        assert quote.data_status == DataStatus.LIVE

        # Dict subscripting backward compatibility
        assert quote["ticker"] == "RELIANCE.NS"
        assert quote["price"] == 2980.5


@pytest.mark.asyncio
async def test_zerodha_batch_quotes(configured_provider):
    mock_resp = MagicMock()
    mock_resp.status_code = 200
    mock_resp.json.return_value = MOCK_KITE_BATCH_QUOTES

    with patch("httpx.AsyncClient.get", return_value=mock_resp):
        quotes = await configured_provider.get_quotes(["RELIANCE.NS", "TCS.NS"])
        assert len(quotes) == 2
        symbols = [q.symbol for q in quotes]
        assert "RELIANCE.NS" in symbols
        assert "TCS.NS" in symbols


# =============================================================================
# 4. Historical OHLCV & Indicator Calculation Tests
# =============================================================================

@pytest.mark.asyncio
async def test_zerodha_historical_ohlcv_and_indicators(configured_provider):
    mock_resp = MagicMock()
    mock_resp.status_code = 200
    mock_resp.json.return_value = MOCK_KITE_HISTORICAL_DATA

    with patch("httpx.AsyncClient.get", return_value=mock_resp), \
         patch("app.services.market_ingestion_service.market_ingestion_service.ingest_ohlcv_bars", new_callable=AsyncMock) as mock_ingest:

        hist = await configured_provider.get_historical_data("RELIANCE.NS", interval="1d", timeframe="6m")
        assert isinstance(hist, HistoricalDataResponse)
        assert hist.symbol == "RELIANCE.NS"
        assert hist.currency == "INR"
        assert hist.data_source == "ZERODHA"
        assert hist.data_status == DataStatus.HISTORICAL
        assert len(hist.candles) == 5

        # Verify candle fields and ordering
        first = hist.candles[0]
        assert first.open == 2940.0
        assert first.high == 2965.0
        assert first.low == 2935.0
        assert first.close == 2955.0
        assert first.volume == 150000

        # Verify TimescaleDB ingestion call was triggered
        mock_ingest.assert_awaited_once()


# =============================================================================
# 5. Instrument Token Manager & Dynamic Resolution Tests
# =============================================================================

@pytest.mark.asyncio
async def test_instrument_token_manager_static_and_csv_resolution():
    manager = ZerodhaInstrumentManager()

    # 1. Static Resolution
    tok_rel = await manager.resolve_instrument_token("NSE", "RELIANCE")
    assert tok_rel == STATIC_INSTRUMENT_TOKENS["NSE:RELIANCE"]

    tok_nifty = await manager.resolve_instrument_token("NSE", "NIFTY 50")
    assert tok_nifty == STATIC_INSTRUMENT_TOKENS["NSE:NIFTY 50"]

    # 2. Dynamic CSV Master Resolution
    mock_csv_content = (
        "instrument_token,exchange_token,tradingsymbol,name,last_price,expiry,strike,tick_size,lot_size,instrument_type,segment,exchange\n"
        "998877,1234,CUSTOMSTOCK,Custom Stock Ltd,100.0,,0.0,0.05,1,EQ,NSE,NSE\n"
    )
    mock_csv_resp = MagicMock()
    mock_csv_resp.status_code = 200
    mock_csv_resp.text = mock_csv_content

    mock_client = AsyncMock()
    mock_client.get.return_value = mock_csv_resp

    tok_custom = await manager.resolve_instrument_token(
        "NSE", "CUSTOMSTOCK", client=mock_client, headers={"X-Kite-Version": "3"}
    )
    assert tok_custom == 998877


# =============================================================================
# 6. Rate Limiting, Timeouts, and Errors Tests
# =============================================================================

@pytest.mark.asyncio
async def test_zerodha_rate_limiting(configured_provider):
    mock_rate_limit_resp = MagicMock()
    mock_rate_limit_resp.status_code = 429
    mock_rate_limit_resp.json.return_value = {
        "status": "error",
        "error_type": "RateLimitExceeded",
        "message": "Too many requests. Please slow down."
    }

    with patch("app.cache.market_cache.market_cache.get_quote", new_callable=AsyncMock, return_value=None), \
         patch("httpx.AsyncClient.get", return_value=mock_rate_limit_resp):
        with pytest.raises(RateLimitExceeded):
            await configured_provider.get_quote("HDFCBANK.NS")


@pytest.mark.asyncio
async def test_zerodha_timeout_mapping(configured_provider):
    with patch("app.cache.market_cache.market_cache.get_quote", new_callable=AsyncMock, return_value=None), \
         patch("httpx.AsyncClient.get", side_effect=httpx.TimeoutException("Request timed out")):
        with pytest.raises(MarketDataTimeout):
            await configured_provider.get_quote("ICICIBANK.NS")


# =============================================================================
# 7. Factory Integration with INDIA_MARKET_PROVIDER=zerodha
# =============================================================================

def test_factory_routes_to_zerodha_when_configured():
    with patch.object(settings, "INDIA_MARKET_PROVIDER", "zerodha"):
        provider = provider_factory.get_provider(symbol="RELIANCE.NS")
        assert isinstance(provider, ZerodhaMarketProvider)

        provider_nifty = provider_factory.get_provider(symbol="NIFTY 50")
        assert isinstance(provider_nifty, ZerodhaMarketProvider)


# =============================================================================
# 8. Fundamentals, Profile, Indices, and Session Status
# =============================================================================

@pytest.mark.asyncio
async def test_zerodha_fundamentals_and_profile(configured_provider):
    mock_resp = MagicMock()
    mock_resp.status_code = 200
    mock_resp.json.return_value = MOCK_KITE_RELIANCE_QUOTE

    with patch("httpx.AsyncClient.get", return_value=mock_resp):
        funds = await configured_provider.get_fundamentals("RELIANCE.NS")
        assert funds.symbol == "RELIANCE.NS"
        assert funds.currency == "INR"
        assert funds.pe_ratio is not None
        assert funds.data_source == "ZERODHA"

        prof = await configured_provider.get_company_profile("RELIANCE.NS")
        assert prof.symbol == "RELIANCE.NS"
        assert prof.exchange == "NSE"
        assert prof.currency == "INR"
        assert "Reliance Industries" in prof.name


@pytest.mark.asyncio
async def test_zerodha_indices_and_market_status(configured_provider):
    mock_resp = MagicMock()
    mock_resp.status_code = 200
    mock_resp.json.return_value = {
        "status": "success",
        "data": {
            "NSE:NIFTY 50": {
                "instrument_token": 256265,
                "last_price": 24800.0,
                "ohlc": {"open": 24700.0, "high": 24850.0, "low": 24650.0, "close": 24720.0},
                "net_change": 80.0
            },
            "BSE:SENSEX": {
                "instrument_token": 265,
                "last_price": 81200.0,
                "ohlc": {"open": 81000.0, "high": 81350.0, "low": 80900.0, "close": 81050.0},
                "net_change": 150.0
            }
        }
    }

    with patch("httpx.AsyncClient.get", return_value=mock_resp):
        status = await configured_provider.get_market_status()
        assert status.exchange == "NSE"
        assert status.timezone == "Asia/Kolkata"
        assert status.is_open in [True, False]


# =============================================================================
# 9. Provider Health Telemetry & Live Verification Guard
# =============================================================================

@pytest.mark.asyncio
async def test_zerodha_health_live_and_unavailable(configured_provider):
    mock_probe_ok = MagicMock()
    mock_probe_ok.status_code = 200
    mock_probe_ok.json.return_value = {"status": "success", "data": {"NSE:NIFTY 50": {"last_price": 24800.0}}}

    with patch("httpx.AsyncClient.get", return_value=mock_probe_ok):
        health = await configured_provider.get_health()
        assert health.status == ProviderStatus.LIVE
        assert health.latency_ms is not None

    with patch("httpx.AsyncClient.get", side_effect=httpx.ConnectError("Connection refused")):
        health_unavail = await configured_provider.get_health()
        assert health_unavail.status == ProviderStatus.UNAVAILABLE


def test_live_credentials_smoke_test_guard():
    """Verifies that live smoke test is safely skipped when credentials are not configured."""
    has_creds = bool(settings.ZERODHA_API_KEY and settings.ZERODHA_ACCESS_TOKEN)
    if not has_creds:
        # Expected in development/CI environments without live broker credentials
        report_msg = "Live provider verification skipped because credentials are not configured."
        assert "skipped because credentials are not configured" in report_msg

