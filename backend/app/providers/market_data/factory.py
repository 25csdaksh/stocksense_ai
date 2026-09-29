"""
Market Data Provider Factory.
"""
from app.core.config import settings
from app.providers.market_data.base import MarketDataProvider
from app.providers.market_data.yfinance_provider import YFinanceProvider
from app.providers.market_data.mock_provider import MockMarketProvider


def get_market_data_provider() -> MarketDataProvider:
    provider_name = settings.DEFAULT_MARKET_PROVIDER.lower()
    if provider_name == "mock":
        return MockMarketProvider()
    return YFinanceProvider()
