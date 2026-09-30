"""
MarketMind AI — US Equities Fundamentals Provider.
Phase 6.6: Provides rich multi-period statements, company profiles,
and ratios for NASDAQ/NYSE instruments in USD.
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
)
from app.providers.market_data.symbol_normalizer import normalize_symbol
from app.analytics.ratio_engine import ratio_engine
from app.core.logging import logger


US_PROFILES: Dict[str, Dict[str, Any]] = {
    "AAPL": {
        "name": "Apple Inc.",
        "legal_name": "Apple Inc.",
        "exchange": "NASDAQ",
        "isin": "US0378331005",
        "sector": "Information Technology",
        "industry": "Consumer Electronics & Services",
        "country": "US",
        "currency": "USD",
        "market_cap": 3450000000000.0,
        "description": "Apple Inc. designs, manufactures, and markets smartphones, personal computers, tablets, wearables, and accessories, and sells a variety of related services.",
        "website": "https://www.apple.com",
        "employees": 161000,
        "cik": "0000320193",
    },
    "MSFT": {
        "name": "Microsoft Corporation",
        "legal_name": "Microsoft Corporation",
        "exchange": "NASDAQ",
        "isin": "US5949181045",
        "sector": "Information Technology",
        "industry": "Systems Software & Cloud Infrastructure (Azure)",
        "country": "US",
        "currency": "USD",
        "market_cap": 3150000000000.0,
        "description": "Microsoft Corporation develops and supports software, services, devices and solutions worldwide including Microsoft Cloud, Windows, Office 365, and gaming.",
        "website": "https://www.microsoft.com",
        "employees": 221000,
        "cik": "0000789019",
    },
    "NVDA": {
        "name": "NVIDIA Corporation",
        "legal_name": "NVIDIA Corporation",
        "exchange": "NASDAQ",
        "isin": "US67066G1040",
        "sector": "Information Technology",
        "industry": "Semiconductors & Accelerated AI Computing",
        "country": "US",
        "currency": "USD",
        "market_cap": 3100000000000.0,
        "description": "NVIDIA Corporation focuses on personal computer graphics, accelerated computing, and artificial intelligence architectures powering the global AI revolution.",
        "website": "https://www.nvidia.com",
        "employees": 29600,
        "cik": "0001045810",
    },
    "AMZN": {
        "name": "Amazon.com, Inc.",
        "legal_name": "Amazon.com, Inc.",
        "exchange": "NASDAQ",
        "isin": "US0231351067",
        "sector": "Consumer Discretionary",
        "industry": "E-Commerce & Cloud Infrastructure (AWS)",
        "country": "US",
        "currency": "USD",
        "market_cap": 2050000000000.0,
        "description": "Amazon.com, Inc. focuses on retail sale of consumer products and subscriptions through online and physical stores, cloud infrastructure services (AWS), and advertising.",
        "website": "https://www.amazon.com",
        "employees": 1525000,
        "cik": "0001018724",
    },
    "GOOGL": {
        "name": "Alphabet Inc.",
        "legal_name": "Alphabet Inc.",
        "exchange": "NASDAQ",
        "isin": "US02079K3059",
        "sector": "Communication Services",
        "industry": "Interactive Media & Search Services",
        "country": "US",
        "currency": "USD",
        "market_cap": 2180000000000.0,
        "description": "Alphabet Inc. offers various products and platforms in the US, Europe, Middle East, Africa, Asia-Pacific, Canada, and Latin America through Google Services and Google Cloud.",
        "website": "https://abc.xyz",
        "employees": 182000,
        "cik": "0001652044",
    },
}

US_FINANCIAL_STATEMENTS: Dict[str, Dict[str, Any]] = {
    "AAPL": {
        "income": [
            {"period": "2024-FY", "period_type": "ANNUAL", "fiscal_year": 2024, "fiscal_quarter": "FY", "revenue": 391035000000.0, "cost_of_revenue": 210352000000.0, "gross_profit": 180683000000.0, "operating_expenses": 57400000000.0, "operating_income": 123216000000.0, "ebitda": 134700000000.0, "ebit": 123216000000.0, "interest_expense": 3900000000.0, "tax_expense": 24000000000.0, "net_income": 93736000000.0, "eps": 6.11, "shares_outstanding": 15300000000},
            {"period": "2023-FY", "period_type": "ANNUAL", "fiscal_year": 2023, "fiscal_quarter": "FY", "revenue": 383285000000.0, "cost_of_revenue": 214137000000.0, "gross_profit": 169148000000.0, "operating_expenses": 54847000000.0, "operating_income": 114301000000.0, "ebitda": 125820000000.0, "ebit": 114301000000.0, "interest_expense": 3933000000.0, "tax_expense": 16741000000.0, "net_income": 96995000000.0, "eps": 6.13, "shares_outstanding": 15800000000},
            {"period": "2024-Q4", "period_type": "QUARTERLY", "fiscal_year": 2024, "fiscal_quarter": "Q4", "revenue": 94930000000.0, "cost_of_revenue": 51100000000.0, "gross_profit": 43830000000.0, "operating_expenses": 14200000000.0, "operating_income": 29630000000.0, "ebitda": 32500000000.0, "ebit": 29630000000.0, "interest_expense": 950000000.0, "tax_expense": 13900000000.0, "net_income": 14736000000.0, "eps": 0.97, "shares_outstanding": 15300000000},
        ],
        "balance_sheet": [
            {"period": "2024-FY", "period_type": "ANNUAL", "fiscal_year": 2024, "fiscal_quarter": "FY", "cash_and_equivalents": 29943000000.0, "short_term_investments": 35200000000.0, "receivables": 32000000000.0, "inventory": 6500000000.0, "total_current_assets": 143566000000.0, "total_assets": 364980000000.0, "current_liabilities": 145308000000.0, "short_term_debt": 10500000000.0, "long_term_debt": 91800000000.0, "total_debt": 102300000000.0, "total_liabilities": 298000000000.0, "retained_earnings": -15000000000.0, "total_equity": 66980000000.0},
        ],
        "cash_flow": [
            {"period": "2024-FY", "period_type": "ANNUAL", "fiscal_year": 2024, "fiscal_quarter": "FY", "operating_cash_flow": 118264000000.0, "capital_expenditures": -9450000000.0, "free_cash_flow": 108814000000.0, "investing_cash_flow": 2580000000.0, "financing_cash_flow": -115700000000.0, "dividends_paid": -15025000000.0},
        ]
    }
}


class USFundamentalsProvider(FundamentalsProvider):
    """Normalized Fundamentals Provider for US NASDAQ/NYSE Equities."""

    @property
    def provider_name(self) -> str:
        return "US_PROVIDER"

    async def get_company_profile(self, symbol: str) -> Optional[CompanyProfileData]:
        norm = normalize_symbol(symbol)
        canonical = norm.canonical_symbol

        raw = US_PROFILES.get(canonical)
        if not raw:
            bare_name = norm.display_symbol or canonical
            raw = {
                "name": f"{bare_name} Inc.",
                "legal_name": f"{bare_name} Inc.",
                "exchange": norm.exchange or "NASDAQ",
                "isin": f"US{abs(hash(canonical)) % 1000000000:09d}1",
                "sector": "US Equities",
                "industry": "Global Enterprise",
                "country": "US",
                "currency": "USD",
                "market_cap": 50000000000.0,
                "description": f"{bare_name} Inc. is an established publicly traded US enterprise.",
                "website": f"https://www.{bare_name.lower()}.com",
                "employees": 25000,
                "cik": "0000000000",
            }

        return CompanyProfileData(
            symbol=canonical,
            name=raw.get("name", canonical),
            legal_name=raw.get("legal_name"),
            exchange=raw.get("exchange", "NASDAQ"),
            isin=raw.get("isin"),
            sector=raw.get("sector", "Technology"),
            industry=raw.get("industry"),
            country=raw.get("country", "US"),
            currency=raw.get("currency", "USD"),
            market_cap=raw.get("market_cap"),
            description=raw.get("description"),
            website=raw.get("website"),
            employees=raw.get("employees"),
            cik=raw.get("cik"),
            data_source=FundamentalDataSource.YFINANCE,
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

        st_key = "income"
        if "balance" in statement_type.lower():
            st_key = "balance_sheet"
        elif "cash" in statement_type.lower():
            st_key = "cash_flow"

        comp_data = US_FINANCIAL_STATEMENTS.get(canonical, {})
        raw_periods = comp_data.get(st_key, [])

        p_type_filter = period_type.strip().upper()
        if p_type_filter in ["ANNUAL", "QUARTERLY"]:
            filtered = [p for p in raw_periods if p.get("period_type", "ANNUAL") == p_type_filter]
            if filtered:
                raw_periods = filtered

        if not raw_periods:
            if st_key == "income":
                raw_periods = [
                    {"period": "2024-FY", "period_type": "ANNUAL", "fiscal_year": 2024, "fiscal_quarter": "FY", "revenue": 85000000000.0, "cost_of_revenue": 45000000000.0, "gross_profit": 40000000000.0, "operating_expenses": 18000000000.0, "operating_income": 22000000000.0, "ebitda": 26000000000.0, "ebit": 22000000000.0, "interest_expense": 800000000.0, "tax_expense": 3500000000.0, "net_income": 17700000000.0, "eps": 4.85, "shares_outstanding": 3650000000},
                    {"period": "2023-FY", "period_type": "ANNUAL", "fiscal_year": 2023, "fiscal_quarter": "FY", "revenue": 76000000000.0, "cost_of_revenue": 41000000000.0, "gross_profit": 35000000000.0, "operating_expenses": 16000000000.0, "operating_income": 19000000000.0, "ebitda": 22500000000.0, "ebit": 19000000000.0, "interest_expense": 750000000.0, "tax_expense": 3000000000.0, "net_income": 15250000000.0, "eps": 4.15, "shares_outstanding": 3680000000},
                ]
            elif st_key == "balance_sheet":
                raw_periods = [
                    {"period": "2024-FY", "period_type": "ANNUAL", "fiscal_year": 2024, "fiscal_quarter": "FY", "cash_and_equivalents": 18500000000.0, "receivables": 14000000000.0, "inventory": 5200000000.0, "total_current_assets": 45000000000.0, "total_assets": 125000000000.0, "current_liabilities": 28000000000.0, "short_term_debt": 4000000000.0, "long_term_debt": 25000000000.0, "total_debt": 29000000000.0, "total_liabilities": 65000000000.0, "retained_earnings": 42000000000.0, "total_equity": 60000000000.0},
                ]
            else:
                raw_periods = [
                    {"period": "2024-FY", "period_type": "ANNUAL", "fiscal_year": 2024, "fiscal_quarter": "FY", "operating_cash_flow": 24000000000.0, "capital_expenditures": -5500000000.0, "free_cash_flow": 18500000000.0, "investing_cash_flow": -7000000000.0, "financing_cash_flow": -14000000000.0, "dividends_paid": -4500000000.0},
                ]

        return FinancialStatementsContainer(
            symbol=canonical,
            statement_type=st_key,
            period_type=FinancialPeriodType(period_type.upper()) if period_type.upper() in ["ANNUAL", "QUARTERLY", "TTM"] else FinancialPeriodType.ANNUAL,
            currency="USD",
            periods=raw_periods,
            data_source=FundamentalDataSource.YFINANCE,
            data_status=FundamentalDataStatus.DEMO,
            updated_at=datetime.utcnow().isoformat(),
        )

    async def get_fundamentals(self, symbol: str) -> Optional[FundamentalOverviewData]:
        norm = normalize_symbol(symbol)
        canonical = norm.canonical_symbol

        profile = await self.get_company_profile(canonical)
        inc_res = await self.get_financial_statements(canonical, "income", "annual")
        bal_res = await self.get_financial_statements(canonical, "balance_sheet", "annual")
        cf_res = await self.get_financial_statements(canonical, "cash_flow", "annual")

        latest_inc = None
        if inc_res.periods:
            p = inc_res.periods[0]
            latest_inc = IncomeStatementData(
                symbol=canonical,
                period_type=FinancialPeriodType.ANNUAL,
                period_end=p.get("period", "2024-FY"),
                fiscal_year=p.get("fiscal_year", 2024),
                currency="USD",
                revenue=p.get("revenue", 100000000.0),
                gross_profit=p.get("gross_profit"),
                operating_income=p.get("operating_income"),
                ebitda=p.get("ebitda"),
                ebit=p.get("ebit"),
                interest_expense=p.get("interest_expense"),
                tax_expense=p.get("tax_expense"),
                net_income=p.get("net_income", 10000000.0),
                eps=p.get("eps"),
                data_source=FundamentalDataSource.YFINANCE,
                data_status=FundamentalDataStatus.DEMO,
            )

        latest_bal = None
        if bal_res.periods:
            p = bal_res.periods[0]
            latest_bal = BalanceSheetData(
                symbol=canonical,
                period_type=FinancialPeriodType.ANNUAL,
                period_end=p.get("period", "2024-FY"),
                fiscal_year=p.get("fiscal_year", 2024),
                currency="USD",
                cash_and_equivalents=p.get("cash_and_equivalents"),
                receivables=p.get("receivables"),
                inventory=p.get("inventory"),
                total_current_assets=p.get("total_current_assets"),
                total_assets=p.get("total_assets", 200000000.0),
                current_liabilities=p.get("current_liabilities"),
                total_debt=p.get("total_debt"),
                total_liabilities=p.get("total_liabilities", 100000000.0),
                retained_earnings=p.get("retained_earnings"),
                total_equity=p.get("total_equity", 100000000.0),
                data_source=FundamentalDataSource.YFINANCE,
                data_status=FundamentalDataStatus.DEMO,
            )

        latest_cf = None
        if cf_res.periods:
            p = cf_res.periods[0]
            latest_cf = CashFlowData(
                symbol=canonical,
                period_type=FinancialPeriodType.ANNUAL,
                period_end=p.get("period", "2024-FY"),
                fiscal_year=p.get("fiscal_year", 2024),
                currency="USD",
                operating_cash_flow=p.get("operating_cash_flow", 20000000.0),
                capital_expenditures=p.get("capital_expenditures"),
                free_cash_flow=p.get("free_cash_flow"),
                dividends_paid=p.get("dividends_paid"),
                data_source=FundamentalDataSource.YFINANCE,
                data_status=FundamentalDataStatus.DEMO,
            )

        mcap = profile.market_cap if profile else None
        ratios = ratio_engine.compute_all_ratios(
            symbol=canonical,
            income=latest_inc,
            balance=latest_bal,
            cashflow=latest_cf,
            market_cap=mcap,
            data_source=FundamentalDataSource.YFINANCE,
            data_status=FundamentalDataStatus.DEMO,
        )

        return FundamentalOverviewData(
            symbol=canonical,
            name=profile.name if profile else canonical,
            sector=profile.sector if profile else "US Equities",
            exchange=profile.exchange if profile else "NASDAQ",
            currency="USD",
            profile=profile,
            valuation=ratios.valuation,
            profitability=ratios.profitability,
            financial_health=ratios.leverage,
            liquidity=ratios.liquidity,
            efficiency=ratios.efficiency,
            latest_income=latest_inc,
            latest_balance=latest_bal,
            latest_cashflow=latest_cf,
            data_source=FundamentalDataSource.YFINANCE,
            data_status=FundamentalDataStatus.DEMO,
            updated_at=datetime.utcnow().isoformat(),
        )
