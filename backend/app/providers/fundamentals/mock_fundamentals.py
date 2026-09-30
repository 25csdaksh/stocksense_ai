"""
MarketMind AI — Deterministic Mock Fundamentals Provider for Unit Testing.
Phase 6.6: Fast, deterministic offline provider for unit test suites and fallback scenarios.
"""
from typing import Optional, Dict, Any, List
from datetime import datetime
from app.providers.fundamentals.base import FundamentalsProvider
from app.providers.fundamentals.models import (
    CompanyProfileData,
    IncomeStatementData,
    BalanceSheetData,
    CashFlowData,
    FundamentalOverviewData,
    FinancialStatementsContainer,
    FinancialPeriodType,
    FundamentalDataSource,
    FundamentalDataStatus,
    ValuationRatios,
    ProfitabilityRatios,
    LeverageRatios,
    LiquidityRatios,
    EfficiencyRatios,
)
from app.providers.market_data.symbol_normalizer import normalize_symbol
from app.analytics.ratio_engine import ratio_engine


class MockFundamentalsProvider(FundamentalsProvider):
    """Deterministic Mock Fundamentals Provider for Unit & Integration Testing."""

    @property
    def provider_name(self) -> str:
        return "MOCK_FUNDAMENTALS"

    async def get_company_profile(self, symbol: str) -> Optional[CompanyProfileData]:
        norm = normalize_symbol(symbol)
        canonical = norm.canonical_symbol

        return CompanyProfileData(
            symbol=canonical,
            name=f"{norm.display_symbol or canonical} Corp",
            legal_name=f"{norm.display_symbol or canonical} Corporation",
            exchange=norm.exchange or "NSE",
            isin=f"INE{abs(hash(canonical)) % 1000000000:09d}",
            sector="Technology",
            industry="Software & AI Infrastructure",
            country="IN" if norm.exchange in ["NSE", "BSE"] else "US",
            currency="INR" if norm.exchange in ["NSE", "BSE"] else "USD",
            market_cap=500000000000.0,
            description="Mock company profile for deterministic testing.",
            website="https://www.example.com",
            employees=10000,
            data_source=FundamentalDataSource.DEMO,
            data_status=FundamentalDataStatus.DEMO,
            updated_at=datetime.utcnow().isoformat(),
        )

    async def get_financial_statements(
        self,
        symbol: str,
        statement_type: str = "income",
        period_type: str = "annual"
    ) -> FinancialStatementsContainer:
        norm = normalize_symbol(symbol)
        canonical = norm.canonical_symbol
        curr = "INR" if norm.exchange in ["NSE", "BSE"] else "USD"

        st_key = "income"
        if "balance" in statement_type.lower():
            st_key = "balance_sheet"
            periods = [
                {"period": "2024-FY", "period_type": "ANNUAL", "fiscal_year": 2024, "fiscal_quarter": "FY", "cash_and_equivalents": 38000000000.0, "total_assets": 365000000000.0, "current_liabilities": 140000000000.0, "total_liabilities": 140000000000.0, "total_equity": 225000000000.0},
                {"period": "2023-FY", "period_type": "ANNUAL", "fiscal_year": 2023, "fiscal_quarter": "FY", "cash_and_equivalents": 35000000000.0, "total_assets": 350000000000.0, "current_liabilities": 145000000000.0, "total_liabilities": 145000000000.0, "total_equity": 205000000000.0},
            ]
        elif "cash" in statement_type.lower():
            st_key = "cash_flow"
            periods = [
                {"period": "2024-FY", "period_type": "ANNUAL", "fiscal_year": 2024, "fiscal_quarter": "FY", "operating_cash_flow": 28000000000.0, "capital_expenditures": -8500000000.0, "free_cash_flow": 19500000000.0, "dividends_paid": -3800000000.0},
                {"period": "2023-FY", "period_type": "ANNUAL", "fiscal_year": 2023, "fiscal_quarter": "FY", "operating_cash_flow": 110000000000.0, "capital_expenditures": -32000000000.0, "free_cash_flow": 78000000000.0, "dividends_paid": -15000000000.0},
            ]
        else:
            periods = [
                {"period": "2024-FY", "period_type": "ANNUAL", "fiscal_year": 2024, "fiscal_quarter": "FY", "revenue": 94800000000.0, "cost_of_revenue": 29900000000.0, "gross_profit": 64900000000.0, "operating_income": 32400000000.0, "ebitda": 38000000000.0, "ebit": 32400000000.0, "interest_expense": 1200000000.0, "tax_expense": 5800000000.0, "net_income": 25400000000.0, "eps": 1.64},
                {"period": "2023-FY", "period_type": "ANNUAL", "fiscal_year": 2023, "fiscal_quarter": "FY", "revenue": 383000000000.0, "cost_of_revenue": 123000000000.0, "gross_profit": 260000000000.0, "operating_income": 128000000000.0, "ebitda": 145000000000.0, "ebit": 128000000000.0, "interest_expense": 4500000000.0, "tax_expense": 26500000000.0, "net_income": 97000000000.0, "eps": 6.13},
            ]

        return FinancialStatementsContainer(
            symbol=canonical,
            statement_type=st_key,
            period_type=FinancialPeriodType(period_type.upper()) if period_type.upper() in ["ANNUAL", "QUARTERLY", "TTM"] else FinancialPeriodType.ANNUAL,
            currency=curr,
            periods=periods,
            data_source=FundamentalDataSource.DEMO,
            data_status=FundamentalDataStatus.DEMO,
            updated_at=datetime.utcnow().isoformat(),
        )

    async def get_fundamentals(self, symbol: str) -> Optional[FundamentalOverviewData]:
        norm = normalize_symbol(symbol)
        canonical = norm.canonical_symbol
        curr = "INR" if norm.exchange in ["NSE", "BSE"] else "USD"

        return FundamentalOverviewData(
            symbol=canonical,
            name=f"{norm.display_symbol or canonical} Corp",
            sector="Information Technology",
            exchange=norm.exchange or "NSE",
            currency=curr,
            valuation=ValuationRatios(
                pe_ratio=28.5,
                forward_pe=25.1,
                ps_ratio=5.2,
                pb_ratio=6.4,
                ev_ebitda=22.4,
                peg_ratio=1.45,
                fcf_yield_pct=3.8,
            ),
            profitability=ProfitabilityRatios(
                gross_margin_pct=68.5,
                operating_margin_pct=34.2,
                ebitda_margin_pct=40.1,
                net_margin_pct=26.8,
                roe_pct=38.4,
                roa_pct=16.2,
                roic_pct=24.5,
            ),
            financial_health=LeverageRatios(
                debt_to_equity=0.62,
                debt_to_assets=0.38,
                interest_coverage=18.5,
                altman_z_score=4.85,
                health_score="EXCELLENT",
            ),
            liquidity=LiquidityRatios(
                current_ratio=1.45,
                quick_ratio=1.20,
                cash_ratio=0.85,
            ),
            efficiency=EfficiencyRatios(
                asset_turnover=0.65,
                inventory_turnover=12.4,
                receivables_turnover=8.2,
            ),
            data_source=FundamentalDataSource.DEMO,
            data_status=FundamentalDataStatus.DEMO,
            updated_at=datetime.utcnow().isoformat(),
        )
