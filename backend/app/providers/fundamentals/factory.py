"""
MarketMind AI — Fundamentals Provider Factory.
Phase 6.6: Selects the appropriate market fundamentals provider (Indian, US, or Mock)
based on canonical symbol normalization and exchange routing.
"""
from typing import Optional, Dict, Any
from app.providers.fundamentals.base import FundamentalsProvider
from app.providers.fundamentals.indian_provider import IndianFundamentalsProvider
from app.providers.fundamentals.us_provider import USFundamentalsProvider
from app.providers.fundamentals.mock_fundamentals import MockFundamentalsProvider
from app.providers.fundamentals.models import (
    CompanyProfileData,
    FundamentalOverviewData,
    FinancialStatementsContainer,
)
from app.providers.market_data.symbol_normalizer import normalize_symbol
from app.core.config import settings


_indian_provider = IndianFundamentalsProvider()
_us_provider = USFundamentalsProvider()
_mock_provider = MockFundamentalsProvider()


class RoutingFundamentalsProvider(FundamentalsProvider):
    """Dynamic router provider that dispatches to Indian or US provider based on target symbol."""

    @property
    def provider_name(self) -> str:
        return "ROUTING_PROVIDER"

    def _get_target_provider(self, symbol: str) -> FundamentalsProvider:
        if getattr(settings, "USE_MOCK_DATA", False):
            return _mock_provider
        norm = normalize_symbol(symbol)
        if norm.exchange in ["NSE", "BSE"] or norm.canonical_symbol.endswith(".NS") or norm.canonical_symbol.endswith(".BO"):
            return _indian_provider
        elif norm.exchange in ["NASDAQ", "NYSE", "AMEX", "BATS"]:
            return _us_provider
        return _indian_provider

    async def get_company_profile(self, symbol: str) -> Optional[CompanyProfileData]:
        return await self._get_target_provider(symbol).get_company_profile(symbol)

    async def get_financial_statements(
        self,
        symbol: str,
        statement_type: str = "income",
        period_type: str = "annual"
    ) -> FinancialStatementsContainer:
        return await self._get_target_provider(symbol).get_financial_statements(
            symbol, statement_type=statement_type, period_type=period_type
        )

    async def get_fundamentals(self, symbol: str) -> Optional[FundamentalOverviewData]:
        return await self._get_target_provider(symbol).get_fundamentals(symbol)

    async def get_overview(self, ticker: str) -> Dict[str, Any]:
        return await self._get_target_provider(ticker).get_overview(ticker)


_routing_provider = RoutingFundamentalsProvider()


def get_fundamentals_provider(symbol: Optional[str] = None) -> FundamentalsProvider:
    """
    Returns the appropriate FundamentalsProvider implementation for the given symbol.
    If no symbol is passed, returns the dynamic RoutingFundamentalsProvider.
    """
    if getattr(settings, "USE_MOCK_DATA", False):
        return _mock_provider

    if not symbol:
        return _routing_provider

    norm = normalize_symbol(symbol)
    if norm.exchange in ["NSE", "BSE"] or norm.canonical_symbol.endswith(".NS") or norm.canonical_symbol.endswith(".BO"):
        return _indian_provider
    elif norm.exchange in ["NASDAQ", "NYSE", "AMEX", "BATS"]:
        return _us_provider
    else:
        return _indian_provider
