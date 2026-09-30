"""
Unit Tests for Provider Factory, Multi-Market Routing, and Broker Health Stubs.
Phase 6.1: Validates intelligent symbol routing to Indian/US providers and CONFIGURATION_REQUIRED status on broker stubs.
"""
import pytest
from app.providers.market_data.factory import provider_factory, get_market_data_provider
from app.providers.market_data.indian_market_provider import IndianMarketDataProvider
from app.providers.market_data.us_market_provider import USMarketProvider
from app.providers.market_data.demo_provider import DemoMarketProvider
from app.providers.market_data.broker_stubs import (
    ZerodhaMarketProvider,
    UpstoxMarketProvider,
    AngelOneMarketProvider
)
from app.providers.market_data.exceptions import ProviderNotConfigured
from app.providers.market_data.models import ProviderStatus


def test_provider_factory_routing_by_symbol():
    # Indian Symbols -> IndianMarketProvider
    p_rel = provider_factory.get_provider(symbol="RELIANCE.NS")
    assert isinstance(p_rel, IndianMarketDataProvider)

    p_tcs = provider_factory.get_provider(symbol="TCS")
    assert isinstance(p_tcs, IndianMarketDataProvider)

    p_nifty = provider_factory.get_provider(symbol="NIFTY 50")
    assert isinstance(p_nifty, IndianMarketDataProvider)

    p_sensex = provider_factory.get_provider(symbol="SENSEX")
    assert isinstance(p_sensex, IndianMarketDataProvider)

    # US Symbols -> USMarketProvider
    p_aapl = provider_factory.get_provider(symbol="AAPL")
    assert isinstance(p_aapl, USMarketProvider)

    p_msft = provider_factory.get_provider(symbol="MSFT")
    assert isinstance(p_msft, USMarketProvider)

    p_sp500 = provider_factory.get_provider(symbol="S&P 500")
    assert isinstance(p_sp500, USMarketProvider)


def test_provider_factory_routing_by_market_or_exchange():
    p_in = provider_factory.get_provider(market="IN")
    assert isinstance(p_in, IndianMarketDataProvider)

    p_nse = provider_factory.get_provider(exchange="NSE")
    assert isinstance(p_nse, IndianMarketDataProvider)

    p_bse = provider_factory.get_provider(exchange="BSE")
    assert isinstance(p_bse, IndianMarketDataProvider)

    p_us = provider_factory.get_provider(market="US")
    assert isinstance(p_us, USMarketProvider)


def test_broker_stubs_health_and_configuration_status():
    zerodha = ZerodhaMarketProvider()
    assert zerodha.is_configured is False

    upstox = UpstoxMarketProvider()
    assert upstox.is_configured is False

    angel = AngelOneMarketProvider()
    assert angel.is_configured is False


@pytest.mark.asyncio
async def test_unconfigured_broker_raises_provider_not_configured():
    zerodha = ZerodhaMarketProvider()
    with pytest.raises(ProviderNotConfigured):
        await zerodha.get_quote("RELIANCE.NS")

    health = await zerodha.get_health()
    assert health.status == ProviderStatus.CONFIGURATION_REQUIRED
    assert "ZERODHA_API_KEY" in health.configuration_status


@pytest.mark.asyncio
async def test_get_all_providers_health():
    health_list = await provider_factory.get_all_providers_health()
    assert len(health_list) >= 4

    provider_names = [h.provider_name for h in health_list]
    assert "IndianMarketProvider" in provider_names
    assert "USMarketProvider" in provider_names
    assert "ZerodhaMarketProvider" in provider_names
    assert "UpstoxMarketProvider" in provider_names
