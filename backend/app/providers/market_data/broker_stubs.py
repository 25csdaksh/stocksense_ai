"""
MarketMind AI — Indian Broker Market Data Provider Stubs.
Phase 6.1: Provider stubs for Zerodha Kite, Upstox, and Angel One SmartAPI.
Explicitly checks credentials from settings and reports CONFIGURATION_REQUIRED status without fabricating fake live data.
"""
from typing import Dict, Any, List, Optional
from datetime import datetime, timezone

from app.core.config import settings
from app.providers.market_data.base import MarketDataProvider
from app.providers.market_data.models import (
    NormalizedQuote,
    HistoricalDataResponse,
    MarketIndexQuote,
    CompanyFundamentals,
    CompanyProfile,
    MarketNewsItem,
    MarketSessionStatus,
    ProviderHealth,
    ProviderStatus
)
from app.providers.market_data.exceptions import ProviderNotConfigured
from app.providers.market_data.session import market_session_manager


class ZerodhaMarketProvider(MarketDataProvider):
    """Zerodha Kite Connect Market Data Provider Adapter."""

    def __init__(self):
        self.provider_name = "ZerodhaMarketProvider"
        self.market = "NSE"
        self.api_key = settings.ZERODHA_API_KEY
        self.api_secret = settings.ZERODHA_API_SECRET
        self.access_token = settings.ZERODHA_ACCESS_TOKEN

    @property
    def is_configured(self) -> bool:
        return bool(self.api_key and self.access_token)

    def _ensure_configured(self):
        if not self.is_configured:
            missing = []
            if not self.api_key:
                missing.append("ZERODHA_API_KEY")
            if not self.access_token:
                missing.append("ZERODHA_ACCESS_TOKEN")
            raise ProviderNotConfigured(self.provider_name, missing_keys=missing)

    async def get_quote(self, symbol: str) -> NormalizedQuote:
        self._ensure_configured()
        raise NotImplementedError("Zerodha live connectivity is scheduled for Phase 6.2.")

    async def get_quotes(self, symbols: List[str]) -> List[NormalizedQuote]:
        self._ensure_configured()
        raise NotImplementedError("Zerodha live connectivity is scheduled for Phase 6.2.")

    async def get_historical_data(self, symbol: str, start=None, end=None, interval="1d", timeframe="6m") -> HistoricalDataResponse:
        self._ensure_configured()
        raise NotImplementedError("Zerodha live connectivity is scheduled for Phase 6.2.")

    async def get_fundamentals(self, symbol: str) -> CompanyFundamentals:
        self._ensure_configured()
        raise NotImplementedError("Zerodha live connectivity is scheduled for Phase 6.2.")

    async def get_company_profile(self, symbol: str) -> CompanyProfile:
        self._ensure_configured()
        raise NotImplementedError("Zerodha live connectivity is scheduled for Phase 6.2.")

    async def get_market_indices(self) -> List[MarketIndexQuote]:
        self._ensure_configured()
        raise NotImplementedError("Zerodha live connectivity is scheduled for Phase 6.2.")

    async def get_news(self, symbol: Optional[str] = None, limit: int = 10) -> List[MarketNewsItem]:
        self._ensure_configured()
        raise NotImplementedError("Zerodha live connectivity is scheduled for Phase 6.2.")

    async def get_market_status(self) -> MarketSessionStatus:
        return market_session_manager.get_session_status("NSE")

    async def get_health(self) -> ProviderHealth:
        if self.is_configured:
            return ProviderHealth(
                provider_name=self.provider_name,
                market=self.market,
                status=ProviderStatus.LIVE,
                configuration_status="Zerodha Kite Connect credentials verified."
            )
        return ProviderHealth(
            provider_name=self.provider_name,
            market=self.market,
            status=ProviderStatus.CONFIGURATION_REQUIRED,
            configuration_status="Zerodha Kite Connect requires ZERODHA_API_KEY and ZERODHA_ACCESS_TOKEN in environment.",
            error_message="Credentials not provided. Provider inactive."
        )


class UpstoxMarketProvider(MarketDataProvider):
    """Upstox Market Data Provider Adapter."""

    def __init__(self):
        self.provider_name = "UpstoxMarketProvider"
        self.market = "NSE"
        self.api_key = settings.UPSTOX_API_KEY
        self.api_secret = settings.UPSTOX_API_SECRET
        self.access_token = settings.UPSTOX_ACCESS_TOKEN

    @property
    def is_configured(self) -> bool:
        return bool(self.api_key and self.access_token)

    def _ensure_configured(self):
        if not self.is_configured:
            missing = []
            if not self.api_key:
                missing.append("UPSTOX_API_KEY")
            if not self.access_token:
                missing.append("UPSTOX_ACCESS_TOKEN")
            raise ProviderNotConfigured(self.provider_name, missing_keys=missing)

    async def get_quote(self, symbol: str) -> NormalizedQuote:
        self._ensure_configured()
        raise NotImplementedError("Upstox live connectivity is scheduled for Phase 6.2.")

    async def get_quotes(self, symbols: List[str]) -> List[NormalizedQuote]:
        self._ensure_configured()
        raise NotImplementedError("Upstox live connectivity is scheduled for Phase 6.2.")

    async def get_historical_data(self, symbol: str, start=None, end=None, interval="1d", timeframe="6m") -> HistoricalDataResponse:
        self._ensure_configured()
        raise NotImplementedError("Upstox live connectivity is scheduled for Phase 6.2.")

    async def get_fundamentals(self, symbol: str) -> CompanyFundamentals:
        self._ensure_configured()
        raise NotImplementedError("Upstox live connectivity is scheduled for Phase 6.2.")

    async def get_company_profile(self, symbol: str) -> CompanyProfile:
        self._ensure_configured()
        raise NotImplementedError("Upstox live connectivity is scheduled for Phase 6.2.")

    async def get_market_indices(self) -> List[MarketIndexQuote]:
        self._ensure_configured()
        raise NotImplementedError("Upstox live connectivity is scheduled for Phase 6.2.")

    async def get_news(self, symbol: Optional[str] = None, limit: int = 10) -> List[MarketNewsItem]:
        self._ensure_configured()
        raise NotImplementedError("Upstox live connectivity is scheduled for Phase 6.2.")

    async def get_market_status(self) -> MarketSessionStatus:
        return market_session_manager.get_session_status("NSE")

    async def get_health(self) -> ProviderHealth:
        if self.is_configured:
            return ProviderHealth(
                provider_name=self.provider_name,
                market=self.market,
                status=ProviderStatus.LIVE,
                configuration_status="Upstox API credentials verified."
            )
        return ProviderHealth(
            provider_name=self.provider_name,
            market=self.market,
            status=ProviderStatus.CONFIGURATION_REQUIRED,
            configuration_status="Upstox requires UPSTOX_API_KEY and UPSTOX_ACCESS_TOKEN in environment.",
            error_message="Credentials not provided. Provider inactive."
        )


class AngelOneMarketProvider(MarketDataProvider):
    """Angel One SmartAPI Market Data Provider Adapter."""

    def __init__(self):
        self.provider_name = "AngelOneMarketProvider"
        self.market = "NSE"
        self.api_key = settings.ANGEL_API_KEY
        self.client_id = settings.ANGEL_CLIENT_ID
        self.password = settings.ANGEL_PASSWORD
        self.totp = settings.ANGEL_TOTP

    @property
    def is_configured(self) -> bool:
        return bool(self.api_key and self.client_id and self.password)

    def _ensure_configured(self):
        if not self.is_configured:
            missing = []
            if not self.api_key:
                missing.append("ANGEL_API_KEY")
            if not self.client_id:
                missing.append("ANGEL_CLIENT_ID")
            raise ProviderNotConfigured(self.provider_name, missing_keys=missing)

    async def get_quote(self, symbol: str) -> NormalizedQuote:
        self._ensure_configured()
        raise NotImplementedError("Angel One SmartAPI connectivity is scheduled for Phase 6.2.")

    async def get_quotes(self, symbols: List[str]) -> List[NormalizedQuote]:
        self._ensure_configured()
        raise NotImplementedError("Angel One SmartAPI connectivity is scheduled for Phase 6.2.")

    async def get_historical_data(self, symbol: str, start=None, end=None, interval="1d", timeframe="6m") -> HistoricalDataResponse:
        self._ensure_configured()
        raise NotImplementedError("Angel One SmartAPI connectivity is scheduled for Phase 6.2.")

    async def get_fundamentals(self, symbol: str) -> CompanyFundamentals:
        self._ensure_configured()
        raise NotImplementedError("Angel One SmartAPI connectivity is scheduled for Phase 6.2.")

    async def get_company_profile(self, symbol: str) -> CompanyProfile:
        self._ensure_configured()
        raise NotImplementedError("Angel One SmartAPI connectivity is scheduled for Phase 6.2.")

    async def get_market_indices(self) -> List[MarketIndexQuote]:
        self._ensure_configured()
        raise NotImplementedError("Angel One SmartAPI connectivity is scheduled for Phase 6.2.")

    async def get_news(self, symbol: Optional[str] = None, limit: int = 10) -> List[MarketNewsItem]:
        self._ensure_configured()
        raise NotImplementedError("Angel One SmartAPI connectivity is scheduled for Phase 6.2.")

    async def get_market_status(self) -> MarketSessionStatus:
        return market_session_manager.get_session_status("NSE")

    async def get_health(self) -> ProviderHealth:
        if self.is_configured:
            return ProviderHealth(
                provider_name=self.provider_name,
                market=self.market,
                status=ProviderStatus.LIVE,
                configuration_status="Angel One SmartAPI credentials verified."
            )
        return ProviderHealth(
            provider_name=self.provider_name,
            market=self.market,
            status=ProviderStatus.CONFIGURATION_REQUIRED,
            configuration_status="Angel One requires ANGEL_API_KEY and ANGEL_CLIENT_ID in environment.",
            error_message="Credentials not provided. Provider inactive."
        )
