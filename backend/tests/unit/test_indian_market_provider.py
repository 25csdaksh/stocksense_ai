"""
Unit Tests for Indian Market Data Provider (NSE, BSE, NIFTY 50, SENSEX).
"""
import pytest
from app.providers.market_data.indian_market_provider import (
    indian_market_provider,
    INDIAN_EQUITIES_UNIVERSE,
    INDIAN_INDICES
)
from app.providers.market_data.factory import get_market_data_provider


@pytest.mark.asyncio
async def test_indian_equity_quotes():
    # Test Reliance Industries
    quote_rel = await indian_market_provider.get_quote("RELIANCE.NS")
    assert quote_rel["ticker"] == "RELIANCE.NS"
    assert quote_rel["exchange"] == "NSE"
    assert quote_rel["currency"] == "INR"
    assert quote_rel["price"] > 1000.0
    assert "market_cap" in quote_rel

    # Test TCS
    quote_tcs = await indian_market_provider.get_quote("TCS.NS")
    assert quote_tcs["ticker"] == "TCS.NS"
    assert quote_tcs["price"] > 1000.0


@pytest.mark.asyncio
async def test_indian_indices():
    # Test NIFTY 50
    quote_nifty = await indian_market_provider.get_quote("NIFTY 50")
    assert quote_nifty["ticker"] == "NIFTY 50"
    assert quote_nifty["price"] > 20000.0
    assert quote_nifty["currency"] == "INR"

    # Test SENSEX
    quote_sensex = await indian_market_provider.get_quote("SENSEX")
    assert quote_sensex["ticker"] == "SENSEX"
    assert quote_sensex["price"] > 70000.0

    # Test get_indices list
    indices = await indian_market_provider.get_indices()
    assert len(indices) >= 3
    symbols = [idx["symbol"] for idx in indices]
    assert "^NSEI" in symbols or "^BSESN" in symbols


@pytest.mark.asyncio
async def test_indian_market_history():
    hist = await indian_market_provider.get_history("INFY.NS", timeframe="3m")
    assert hist["ticker"] == "INFY.NS"
    assert hist["currency"] == "INR"
    assert "bars" in hist
    assert len(hist["bars"]) > 0
    first_bar = hist["bars"][0]
    assert "close" in first_bar
    assert "sma_20" in first_bar
    assert "rsi_14" in first_bar


def test_market_provider_factory_routing():
    # Indian ticker route
    provider_ind = get_market_data_provider("RELIANCE.NS")
    assert provider_ind is indian_market_provider

    # Indian index route
    provider_nifty = get_market_data_provider("NIFTY 50")
    assert provider_nifty is indian_market_provider
