"""
MarketMind AI — Market Data Provider Factory & Multi-Market Intelligent Router.
Phase 6.1: Routes queries dynamically based on symbol, exchange, market region, and active configuration.
"""
from typing import Optional, Dict, Any, List
from app.core.config import settings
from app.providers.market_data.base import MarketDataProvider
from app.providers.market_data.indian_market_provider import IndianMarketDataProvider, indian_market_provider
from app.providers.market_data.us_market_provider import USMarketProvider, us_market_provider
from app.providers.market_data.demo_provider import DemoMarketProvider, demo_market_provider
from app.providers.market_data.broker_stubs import (
    ZerodhaMarketProvider,
    UpstoxMarketProvider,
    AngelOneMarketProvider
)
from app.providers.market_data.symbol_normalizer import normalize_symbol
from app.providers.market_data.models import ProviderHealth
from app.core.logging import logger


class MarketDataProviderFactory:
    """
    Centralized factory and router for financial market data providers.
    """

    def __init__(self):
        self._indian_provider = indian_market_provider
        self._us_provider = us_market_provider
        self._demo_provider = demo_market_provider
        self._broker_registry: Dict[str, MarketDataProvider] = {
            "zerodha": ZerodhaMarketProvider(),
            "upstox": UpstoxMarketProvider(),
            "angelone": AngelOneMarketProvider(),
        }

    def get_provider(
        self,
        symbol: Optional[str] = None,
        market: Optional[str] = None,
        exchange: Optional[str] = None
    ) -> MarketDataProvider:
        """
        Determines and returns the appropriate MarketDataProvider instance.
        1. If explicit config override (e.g. DEFAULT_MARKET_PROVIDER='mock' or 'demo'), returns Demo provider.
        2. If symbol is provided, normalizes and routes to Indian vs US provider.
        3. If market or exchange specified ('IN', 'NSE', 'BSE' -> Indian provider; 'US', 'NASDAQ' -> US provider).
        4. Defaults to US Provider or configured default.
        """
        # Global override check
        global_override = (settings.MARKET_DATA_PROVIDER or settings.DEFAULT_MARKET_PROVIDER).lower()
        if global_override in ["mock", "demo", "synthetic"]:
            return self._demo_provider

        # Check configured India provider if requested
        india_provider_type = (settings.INDIA_MARKET_PROVIDER or "indian").lower()
        if india_provider_type in self._broker_registry:
            active_indian = self._broker_registry[india_provider_type]
        else:
            active_indian = self._indian_provider

        # Check configured US provider
        us_provider_type = (settings.US_MARKET_PROVIDER or "yfinance").lower()
        if us_provider_type in ["mock", "demo"]:
            active_us = self._demo_provider
        else:
            active_us = self._us_provider

        # 1. Route based on symbol
        if symbol:
            try:
                norm = normalize_symbol(symbol)
                if norm.market == "IN":
                    return active_indian
                elif norm.market == "US":
                    return active_us
            except Exception as exc:
                logger.debug(f"Symbol normalization during routing for '{symbol}': {exc}")

        # 2. Route based on explicit market or exchange parameter
        m_code = (market or exchange or "").strip().upper()
        if m_code in ["IN", "NSE", "BSE", "INDIA", "INDIAN"]:
            return active_indian
        elif m_code in ["US", "NASDAQ", "NYSE", "AMEX"]:
            return active_us

        # 3. Default based on DEFAULT_MARKET_PROVIDER
        if global_override in ["indian", "nse", "bse"]:
            return active_indian
        return active_us

    def get_indian_provider(self) -> MarketDataProvider:
        """Returns the active Indian market provider."""
        return self._indian_provider

    def get_us_provider(self) -> MarketDataProvider:
        """Returns the active US market provider."""
        return self._us_provider

    def get_demo_provider(self) -> MarketDataProvider:
        """Returns the synthetic demo provider."""
        return self._demo_provider

    def get_all_registered_providers(self) -> Dict[str, MarketDataProvider]:
        """Returns a map of all registered concrete providers and broker adapters."""
        return {
            "IndianMarketProvider": self._indian_provider,
            "USMarketProvider": self._us_provider,
            "DemoMarketProvider": self._demo_provider,
            "ZerodhaMarketProvider": self._broker_registry["zerodha"],
            "UpstoxMarketProvider": self._broker_registry["upstox"],
            "AngelOneMarketProvider": self._broker_registry["angelone"],
        }

    async def get_all_providers_health(self) -> List[ProviderHealth]:
        """Collects operational and configuration health from all registered providers."""
        health_reports: List[ProviderHealth] = []
        for _, provider in self.get_all_registered_providers().items():
            try:
                report = await provider.get_health()
                health_reports.append(report)
            except Exception as exc:
                health_reports.append(ProviderHealth(
                    provider_name=getattr(provider, "provider_name", "UnknownProvider"),
                    market=getattr(provider, "market", "UNKNOWN"),
                    status="UNAVAILABLE",
                    configuration_status="Failed to retrieve health status.",
                    error_message=str(exc)
                ))
        return health_reports


provider_factory = MarketDataProviderFactory()


def get_market_data_provider(ticker: Optional[str] = None, market: Optional[str] = None) -> MarketDataProvider:
    """
    Standard backward-compatible access function matching Phase 1-5 factory signature.
    """
    return provider_factory.get_provider(symbol=ticker, market=market)
