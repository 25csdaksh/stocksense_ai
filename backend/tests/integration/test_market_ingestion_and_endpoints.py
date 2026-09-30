"""
Integration Tests for Market Data Ingestion and Multi-Market REST Endpoints.
Phase 6.1: Validates database ingestion into TimescaleDB models and backward compatibility of all market/stock endpoints.
"""
import pytest
from unittest.mock import patch, MagicMock
from datetime import datetime, timezone
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from fastapi.testclient import TestClient

from app.main import app
from app.db.models.stock import StockOHLCV, MarketIndex, Stock
from app.services.market_ingestion_service import market_ingestion_service
from app.providers.market_data.models import HistoricalCandle, MarketIndexQuote, DataStatus


@pytest.fixture(autouse=True)
def mock_external_yfinance():
    """Mocks yfinance network calls during integration tests for ultra-fast, deterministic testing."""
    with patch("app.providers.market_data.indian_market_provider.yf.Ticker") as mock_in_yf, \
         patch("app.providers.market_data.us_market_provider.yf.Ticker") as mock_us_yf:

        mock_ticker_instance = MagicMock()
        mock_fast_info = MagicMock()
        mock_fast_info.last_price = 150.0
        mock_fast_info.previous_close = 148.0
        mock_fast_info.open = 149.0
        mock_fast_info.day_high = 152.0
        mock_fast_info.day_low = 148.5
        mock_fast_info.last_volume = 20000000.0
        mock_fast_info.market_cap = 2e12
        mock_fast_info.year_high = 180.0
        mock_fast_info.year_low = 120.0
        mock_ticker_instance.fast_info = mock_fast_info

        mock_in_yf.return_value = mock_ticker_instance
        mock_us_yf.return_value = mock_ticker_instance
        yield


@pytest.mark.asyncio
async def test_timescaledb_ohlcv_ingestion(db_session: AsyncSession):
    now = datetime.now(timezone.utc)
    bars = [
        HistoricalCandle(
            timestamp=now,
            time="2026-09-30",
            open=2980.0,
            high=3010.0,
            low=2975.0,
            close=3005.0,
            volume=4500000.0,
            symbol="RELIANCE.NS",
            exchange="NSE",
            currency="INR",
            data_source="NSE_FEED",
            data_status=DataStatus.LIVE
        )
    ]

    inserted = await market_ingestion_service.ingest_ohlcv_bars(
        session=db_session,
        symbol="RELIANCE.NS",
        bars=bars,
        interval="1d"
    )
    assert inserted == 1

    # Verify database persistence
    stmt = select(StockOHLCV).where(StockOHLCV.ticker == "RELIANCE.NS")
    res = await db_session.execute(stmt)
    records = res.scalars().all()
    assert len(records) == 1
    assert records[0].close == 3005.0
    assert records[0].ticker == "RELIANCE.NS"


@pytest.mark.asyncio
async def test_market_indices_ingestion(db_session: AsyncSession):
    indices = [
        MarketIndexQuote(
            symbol="^NSEI",
            name="NIFTY 50",
            exchange="NSE",
            price=24850.0,
            change=120.0,
            change_pct=0.48,
            currency="INR",
            timestamp=datetime.now(timezone.utc).isoformat(),
            data_source="NSE_INDEX_FEED",
            data_status=DataStatus.LIVE
        )
    ]

    count = await market_ingestion_service.ingest_indices(session=db_session, indices=indices)
    assert count == 1

    stmt = select(MarketIndex).where(MarketIndex.symbol == "^NSEI")
    res = await db_session.execute(stmt)
    idx_record = res.scalar_one_or_none()
    assert idx_record is not None
    assert idx_record.price == 24850.0


def test_market_overview_endpoint(test_client: TestClient):
    # US Overview
    resp_us = test_client.get("/api/v1/market/overview?market=US")
    assert resp_us.status_code == 200
    data_us = resp_us.json()
    assert "indices" in data_us
    assert "market_regime" in data_us

    # India Overview
    resp_in = test_client.get("/api/v1/market/overview?market=IN")
    assert resp_in.status_code == 200
    data_in = resp_in.json()
    assert "indices" in data_in


def test_market_session_status_endpoint(test_client: TestClient):
    resp = test_client.get("/api/v1/market/status/NSE")
    assert resp.status_code == 200
    data = resp.json()
    assert data["market"] == "IN"
    assert data["exchange"] == "NSE"
    assert "is_open" in data
    assert "session_state" in data
    assert data["timezone"] == "Asia/Kolkata"


def test_market_providers_health_endpoint(test_client: TestClient):
    resp = test_client.get("/api/v1/market/providers/health")
    assert resp.status_code == 200
    data = resp.json()
    assert isinstance(data, list)
    assert len(data) >= 4
    provider_names = [p["provider_name"] for p in data]
    assert "IndianMarketProvider" in provider_names
    assert "USMarketProvider" in provider_names
    assert "ZerodhaMarketProvider" in provider_names


def test_stock_quotes_us_and_indian(test_client: TestClient):
    # US Stock
    resp_aapl = test_client.get("/api/v1/stocks/AAPL")
    assert resp_aapl.status_code == 200
    data_aapl = resp_aapl.json()
    assert data_aapl["ticker"] == "AAPL"
    assert data_aapl["price"] > 0
    assert "data_source" in data_aapl

    # Indian Stock
    resp_rel = test_client.get("/api/v1/stocks/RELIANCE.NS")
    assert resp_rel.status_code == 200
    data_rel = resp_rel.json()
    assert data_rel["ticker"] == "RELIANCE.NS"
    assert data_rel["price"] > 0
    assert data_rel["currency"] == "INR"


def test_stock_history_us_and_indian(test_client: TestClient):
    # US History
    resp_hist_us = test_client.get("/api/v1/stocks/AAPL/history?timeframe=1m&interval=1d")
    assert resp_hist_us.status_code == 200
    data_us = resp_hist_us.json()
    assert data_us["ticker"] == "AAPL"
    assert len(data_us["bars"]) > 0

    # Indian History
    resp_hist_in = test_client.get("/api/v1/stocks/RELIANCE.NS/history?timeframe=1m&interval=1d")
    assert resp_hist_in.status_code == 200
    data_in = resp_hist_in.json()
    assert data_in["ticker"] == "RELIANCE.NS"
    assert len(data_in["bars"]) > 0


def test_stock_fundamentals_and_profile(test_client: TestClient):
    resp_fund = test_client.get("/api/v1/stocks/TCS.NS/fundamentals")
    assert resp_fund.status_code == 200
    data_fund = resp_fund.json()
    assert data_fund["symbol"] == "TCS.NS"
    assert "pe_ratio" in data_fund

    resp_prof = test_client.get("/api/v1/stocks/TCS.NS/profile")
    assert resp_prof.status_code == 200
    data_prof = resp_prof.json()
    assert data_prof["symbol"] == "TCS.NS"
    assert "sector" in data_prof
