"""
MarketMind AI — Fundamentals Provider Base Interface.
Phase 6.6: Multi-Market provider abstraction for company profiles,
financial statements, valuation multiples, and fundamental intelligence.
"""
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List
from app.providers.fundamentals.models import (
    CompanyProfileData,
    IncomeStatementData,
    BalanceSheetData,
    CashFlowData,
    FundamentalOverviewData,
    FinancialStatementsContainer,
    FinancialRatiosData,
)


class FundamentalsProvider(ABC):
    """Abstract interface defining operations required for all fundamentals providers."""

    @property
    @abstractmethod
    def provider_name(self) -> str:
        """Name of the provider implementation."""
        pass

    @abstractmethod
    async def get_company_profile(self, symbol: str) -> Optional[CompanyProfileData]:
        """Fetches normalized company legal profile, sector, exchange, and description."""
        pass

    @abstractmethod
    async def get_financial_statements(
        self,
        symbol: str,
        statement_type: str = "income",
        period_type: str = "annual"
    ) -> FinancialStatementsContainer:
        """Fetches normalized multi-period financial statement line items (Income, Balance, Cashflow)."""
        pass

    @abstractmethod
    async def get_fundamentals(self, symbol: str) -> Optional[FundamentalOverviewData]:
        """Fetches holistic fundamentals overview including valuation, margins, health, and latest statements."""
        pass

    # Backward compatible wrapper
    async def get_overview(self, ticker: str) -> Dict[str, Any]:
        """Legacy helper returning dictionary overview for backward compatibility."""
        res = await self.get_fundamentals(ticker)
        if res:
            return res.model_dump()
        return {}
