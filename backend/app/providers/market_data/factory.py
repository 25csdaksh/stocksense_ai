"""
Market Data Provider Factory with Multi-Market Routing (US Demo + Indian NSE/BSE).
"""
from typing import Optional
from app.core.config import settings
from app.providers.market_data.base import MarketDataProvider
from app.providers.market_data.yfinance_provider import YFinanceProvider
from app.providers.market_data.mock_provider import MockMarketProvider
from app.providers.market_data.indian_market_provider import IndianMarketDataProvider, indian_market_provider


def get_market_data_provider(ticker: Optional[str] = None) -> MarketDataProvider:
    """
    Returns the appropriate market data provider adapter.
    If ticker has Indian market suffixes (.NS, .BO, NIFTY, SENSEX), routes to Indian provider.
    """
    if ticker:
        sym = ticker.strip().upper()
        if sym.endswith(".NS") or sym.endswith(".BO") or "NIFTY" in sym or "SENSEX" in sym:
            return indian_market_provider

    provider_name = settings.DEFAULT_MARKET_PROVIDER.lower()
    if provider_name in ["indian", "nse", "bse"]:
        return indian_market_provider
    elif provider_name == "mock":
        return MockMarketProvider()
    return YFinanceProvider()
