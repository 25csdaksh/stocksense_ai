"""
MarketMind AI — Indian Equities Fundamentals Provider.
Phase 6.6: Provides rich multi-period statements, company profiles,
and ratios for NSE/BSE instruments in INR.
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


INDIAN_PROFILES: Dict[str, Dict[str, Any]] = {
    "RELIANCE.NS": {
        "name": "Reliance Industries Limited",
        "legal_name": "Reliance Industries Limited",
        "exchange": "NSE",
        "isin": "INE002A01018",
        "sector": "Energy & Conglomerate",
        "industry": "Oil, Gas & Petrochemicals / Retail & Telecom",
        "country": "IN",
        "currency": "INR",
        "market_cap": 20150000000000.0,
        "description": "Reliance Industries Limited is an Indian multinational conglomerate headquartered in Mumbai. Its diverse businesses include energy, petrochemicals, natural gas, retail, telecommunications, mass media, and textiles.",
        "website": "https://www.ril.com",
        "employees": 389000,
    },
    "TCS.NS": {
        "name": "Tata Consultancy Services Limited",
        "legal_name": "Tata Consultancy Services Limited",
        "exchange": "NSE",
        "isin": "INE467B01029",
        "sector": "Information Technology",
        "industry": "IT Services & Consulting",
        "country": "IN",
        "currency": "INR",
        "market_cap": 14500000000000.0,
        "description": "Tata Consultancy Services is an Indian multinational information technology services and consulting company headquartered in Mumbai, operating across 150+ locations in 46 countries.",
        "website": "https://www.tcs.com",
        "employees": 615000,
    },
    "INFY.NS": {
        "name": "Infosys Limited",
        "legal_name": "Infosys Limited",
        "exchange": "NSE",
        "isin": "INE009A01021",
        "sector": "Information Technology",
        "industry": "IT Services, Cloud & Digital Transformation",
        "country": "IN",
        "currency": "INR",
        "market_cap": 7800000000000.0,
        "description": "Infosys is a global leader in next-generation digital services and consulting, enabling clients in more than 50 countries to navigate their digital transformation powered by the cloud and AI.",
        "website": "https://www.infosys.com",
        "employees": 317000,
    },
    "HDFCBANK.NS": {
        "name": "HDFC Bank Limited",
        "legal_name": "HDFC Bank Limited",
        "exchange": "NSE",
        "isin": "INE040A01034",
        "sector": "Financial Services",
        "industry": "Private Banking & Financial Services",
        "country": "IN",
        "currency": "INR",
        "market_cap": 12800000000000.0,
        "description": "HDFC Bank is an Indian banking and financial services company headquartered in Mumbai. It is India's largest private sector bank by assets and market capitalization.",
        "website": "https://www.hdfcbank.com",
        "employees": 208000,
    },
    "ICICIBANK.NS": {
        "name": "ICICI Bank Limited",
        "legal_name": "ICICI Bank Limited",
        "exchange": "NSE",
        "isin": "INE090A01021",
        "sector": "Financial Services",
        "industry": "Commercial & Retail Banking",
        "country": "IN",
        "currency": "INR",
        "market_cap": 8900000000000.0,
        "description": "ICICI Bank Limited is a leading Indian multinational bank and financial services company providing a diversified range of banking and financial services to corporate and retail customers.",
        "website": "https://www.icicibank.com",
        "employees": 130000,
    },
    "ITC.NS": {
        "name": "ITC Limited",
        "legal_name": "ITC Limited",
        "exchange": "NSE",
        "isin": "INE154A01025",
        "sector": "Consumer Goods & FMCG",
        "industry": "FMCG, Hotels, Paperboards & Packaging, Agri Business",
        "country": "IN",
        "currency": "INR",
        "market_cap": 6100000000000.0,
        "description": "ITC Limited is an Indian conglomerate company headquartered in Kolkata with businesses spanning FMCG, Hotels, Paperboards & Packaging, Agri Business and Information Technology.",
        "website": "https://www.itcportal.com",
        "employees": 36000,
    },
    "SBIN.NS": {
        "name": "State Bank of India",
        "legal_name": "State Bank of India",
        "exchange": "NSE",
        "isin": "INE062A01020",
        "sector": "Financial Services",
        "industry": "Public Sector Banking",
        "country": "IN",
        "currency": "INR",
        "market_cap": 7200000000000.0,
        "description": "State Bank of India is a Fortune 500 company and India's largest public sector bank with over 200 years of history, commanding a 25% market share in total loan and deposit assets in India.",
        "website": "https://www.sbi.co.in",
        "employees": 235000,
    },
    "TATAMOTORS.NS": {
        "name": "Tata Motors Limited",
        "legal_name": "Tata Motors Limited",
        "exchange": "NSE",
        "isin": "INE155A01022",
        "sector": "Automotive",
        "industry": "Commercial Vehicles, Passenger Cars & EVs (JLR)",
        "country": "IN",
        "currency": "INR",
        "market_cap": 3650000000000.0,
        "description": "Tata Motors Limited is a leading global automobile manufacturer of cars, utility vehicles, pick-ups, trucks, buses, and luxury vehicles under the Jaguar Land Rover marquee.",
        "website": "https://www.tatamotors.com",
        "employees": 82000,
    },
}


# Multi-Period Statements Data Repository (FY24, FY23, FY22, Q3-FY25, Q2-FY25)
INDIAN_FINANCIAL_STATEMENTS: Dict[str, Dict[str, Any]] = {
    "RELIANCE.NS": {
        "income": [
            {"period": "2024-FY", "period_type": "ANNUAL", "fiscal_year": 2024, "fiscal_quarter": "FY", "revenue": 8980200000000.0, "cost_of_revenue": 5890000000000.0, "gross_profit": 3090200000000.0, "operating_expenses": 1310000000000.0, "operating_income": 1780200000000.0, "ebitda": 1780200000000.0, "ebit": 1320000000000.0, "interest_expense": 220000000000.0, "tax_expense": 290000000000.0, "net_income": 790200000000.0, "eps": 116.8, "shares_outstanding": 6765000000},
            {"period": "2023-FY", "period_type": "ANNUAL", "fiscal_year": 2023, "fiscal_quarter": "FY", "revenue": 8794680000000.0, "cost_of_revenue": 5780000000000.0, "gross_profit": 3014680000000.0, "operating_expenses": 1475000000000.0, "operating_income": 1539680000000.0, "ebitda": 1539680000000.0, "ebit": 1140000000000.0, "interest_expense": 195000000000.0, "tax_expense": 280000000000.0, "net_income": 736700000000.0, "eps": 108.9, "shares_outstanding": 6765000000},
            {"period": "2024-Q3", "period_type": "QUARTERLY", "fiscal_year": 2025, "fiscal_quarter": "Q3", "revenue": 2354800000000.0, "cost_of_revenue": 1540000000000.0, "gross_profit": 814800000000.0, "operating_expenses": 350000000000.0, "operating_income": 464800000000.0, "ebitda": 464800000000.0, "ebit": 345000000000.0, "interest_expense": 58000000000.0, "tax_expense": 75000000000.0, "net_income": 205000000000.0, "eps": 30.3, "shares_outstanding": 6765000000},
            {"period": "2024-Q2", "period_type": "QUARTERLY", "fiscal_year": 2025, "fiscal_quarter": "Q2", "revenue": 2318800000000.0, "cost_of_revenue": 1520000000000.0, "gross_profit": 798800000000.0, "operating_expenses": 345000000000.0, "operating_income": 453800000000.0, "ebitda": 453800000000.0, "ebit": 338000000000.0, "interest_expense": 56000000000.0, "tax_expense": 74000000000.0, "net_income": 191000000000.0, "eps": 28.2, "shares_outstanding": 6765000000},
        ],
        "balance_sheet": [
            {"period": "2024-FY", "period_type": "ANNUAL", "fiscal_year": 2024, "fiscal_quarter": "FY", "cash_and_equivalents": 1820000000000.0, "receivables": 380000000000.0, "inventory": 1420000000000.0, "total_current_assets": 4200000000000.0, "total_assets": 17800000000000.0, "current_liabilities": 3600000000000.0, "short_term_debt": 980000000000.0, "long_term_debt": 2340000000000.0, "total_debt": 3320000000000.0, "total_liabilities": 9200000000000.0, "retained_earnings": 5100000000000.0, "total_equity": 8600000000000.0},
            {"period": "2023-FY", "period_type": "ANNUAL", "fiscal_year": 2023, "fiscal_quarter": "FY", "cash_and_equivalents": 1650000000000.0, "receivables": 350000000000.0, "inventory": 1380000000000.0, "total_current_assets": 3900000000000.0, "total_assets": 16400000000000.0, "current_liabilities": 3400000000000.0, "short_term_debt": 910000000000.0, "long_term_debt": 2230000000000.0, "total_debt": 3140000000000.0, "total_liabilities": 8600000000000.0, "retained_earnings": 4500000000000.0, "total_equity": 7800000000000.0},
        ],
        "cash_flow": [
            {"period": "2024-FY", "period_type": "ANNUAL", "fiscal_year": 2024, "fiscal_quarter": "FY", "operating_cash_flow": 1580000000000.0, "capital_expenditures": -1320000000000.0, "free_cash_flow": 260000000000.0, "investing_cash_flow": -1390000000000.0, "financing_cash_flow": -110000000000.0, "dividends_paid": -67650000000.0},
            {"period": "2023-FY", "period_type": "ANNUAL", "fiscal_year": 2023, "fiscal_quarter": "FY", "operating_cash_flow": 1420000000000.0, "capital_expenditures": -1250000000000.0, "free_cash_flow": 170000000000.0, "investing_cash_flow": -1310000000000.0, "financing_cash_flow": -95000000000.0, "dividends_paid": -60880000000.0},
        ]
    },
    "TCS.NS": {
        "income": [
            {"period": "2024-FY", "period_type": "ANNUAL", "fiscal_year": 2024, "fiscal_quarter": "FY", "revenue": 2408930000000.0, "cost_of_revenue": 1394500000000.0, "gross_profit": 1014430000000.0, "operating_expenses": 378000000000.0, "operating_income": 636430000000.0, "ebitda": 685000000000.0, "ebit": 636430000000.0, "interest_expense": 8500000000.0, "tax_expense": 169000000000.0, "net_income": 460990000000.0, "eps": 127.3, "shares_outstanding": 3618000000},
            {"period": "2023-FY", "period_type": "ANNUAL", "fiscal_year": 2023, "fiscal_quarter": "FY", "revenue": 2254580000000.0, "cost_of_revenue": 1308000000000.0, "gross_profit": 946580000000.0, "operating_expenses": 354000000000.0, "operating_income": 592580000000.0, "ebitda": 638000000000.0, "ebit": 592580000000.0, "interest_expense": 7800000000.0, "tax_expense": 156000000000.0, "net_income": 423030000000.0, "eps": 115.6, "shares_outstanding": 3659000000},
            {"period": "2024-Q3", "period_type": "QUARTERLY", "fiscal_year": 2025, "fiscal_quarter": "Q3", "revenue": 639800000000.0, "cost_of_revenue": 371000000000.0, "gross_profit": 268800000000.0, "operating_expenses": 101000000000.0, "operating_income": 167800000000.0, "ebitda": 181000000000.0, "ebit": 167800000000.0, "interest_expense": 2200000000.0, "tax_expense": 44500000000.0, "net_income": 121500000000.0, "eps": 33.6, "shares_outstanding": 3618000000},
        ],
        "balance_sheet": [
            {"period": "2024-FY", "period_type": "ANNUAL", "fiscal_year": 2024, "fiscal_quarter": "FY", "cash_and_equivalents": 425000000000.0, "short_term_investments": 310000000000.0, "receivables": 480000000000.0, "total_current_assets": 1280000000000.0, "total_assets": 1490000000000.0, "current_liabilities": 435000000000.0, "short_term_debt": 0.0, "long_term_debt": 0.0, "total_debt": 0.0, "total_liabilities": 475000000000.0, "retained_earnings": 985000000000.0, "total_equity": 1015000000000.0},
        ],
        "cash_flow": [
            {"period": "2024-FY", "period_type": "ANNUAL", "fiscal_year": 2024, "fiscal_quarter": "FY", "operating_cash_flow": 442000000000.0, "capital_expenditures": -31000000000.0, "free_cash_flow": 411000000000.0, "investing_cash_flow": -45000000000.0, "financing_cash_flow": -392000000000.0, "dividends_paid": -380000000000.0},
        ]
    },
    "INFY.NS": {
        "income": [
            {"period": "2024-FY", "period_type": "ANNUAL", "fiscal_year": 2024, "fiscal_quarter": "FY", "revenue": 1536700000000.0, "cost_of_revenue": 929000000000.0, "gross_profit": 607700000000.0, "operating_expenses": 268000000000.0, "operating_income": 339700000000.0, "ebitda": 386000000000.0, "ebit": 339700000000.0, "interest_expense": 5200000000.0, "tax_expense": 88000000000.0, "net_income": 262480000000.0, "eps": 63.4, "shares_outstanding": 4140000000},
            {"period": "2024-Q3", "period_type": "QUARTERLY", "fiscal_year": 2025, "fiscal_quarter": "Q3", "revenue": 409860000000.0, "cost_of_revenue": 248000000000.0, "gross_profit": 161860000000.0, "operating_expenses": 71000000000.0, "operating_income": 90860000000.0, "ebitda": 103000000000.0, "ebit": 90860000000.0, "interest_expense": 1400000000.0, "tax_expense": 24500000000.0, "net_income": 65060000000.0, "eps": 15.7, "shares_outstanding": 4140000000},
        ],
        "balance_sheet": [
            {"period": "2024-FY", "period_type": "ANNUAL", "fiscal_year": 2024, "fiscal_quarter": "FY", "cash_and_equivalents": 215000000000.0, "short_term_investments": 145000000000.0, "receivables": 310000000000.0, "total_current_assets": 765000000000.0, "total_assets": 1050000000000.0, "current_liabilities": 310000000000.0, "short_term_debt": 0.0, "long_term_debt": 0.0, "total_debt": 0.0, "total_liabilities": 345000000000.0, "retained_earnings": 680000000000.0, "total_equity": 705000000000.0},
        ],
        "cash_flow": [
            {"period": "2024-FY", "period_type": "ANNUAL", "fiscal_year": 2024, "fiscal_quarter": "FY", "operating_cash_flow": 286000000000.0, "capital_expenditures": -25000000000.0, "free_cash_flow": 261000000000.0, "investing_cash_flow": -38000000000.0, "financing_cash_flow": -235000000000.0, "dividends_paid": -190000000000.0},
        ]
    }
}


class IndianFundamentalsProvider(FundamentalsProvider):
    """Normalized Fundamentals Provider for Indian NSE/BSE Equities."""

    @property
    def provider_name(self) -> str:
        return "INDIAN_PROVIDER"

    async def get_company_profile(self, symbol: str) -> Optional[CompanyProfileData]:
        norm = normalize_symbol(symbol)
        canonical = norm.canonical_symbol

        raw = INDIAN_PROFILES.get(canonical)
        if not raw:
            # Check bare symbol without .NS
            bare = canonical.replace(".NS", "").replace(".BO", "")
            for k, v in INDIAN_PROFILES.items():
                if k.startswith(bare):
                    raw = v
                    canonical = k
                    break

        if not raw:
            # Generate fallback structured profile for arbitrary Indian equities
            bare_name = norm.display_symbol or canonical
            raw = {
                "name": f"{bare_name} Limited",
                "legal_name": f"{bare_name} India Limited",
                "exchange": norm.exchange or "NSE",
                "isin": f"INE{abs(hash(canonical)) % 1000000000:09d}",
                "sector": "Indian Equities",
                "industry": "Diversified Business",
                "country": "IN",
                "currency": "INR",
                "market_cap": 250000000000.0,
                "description": f"{bare_name} is an active listed corporate entity traded on the {norm.exchange or 'NSE'} stock exchange.",
                "website": f"https://www.{bare_name.lower().replace('.ns', '')}.com",
                "employees": 15000,
            }

        return CompanyProfileData(
            symbol=canonical,
            name=raw.get("name", canonical),
            legal_name=raw.get("legal_name"),
            exchange=raw.get("exchange", "NSE"),
            isin=raw.get("isin"),
            sector=raw.get("sector", "General"),
            industry=raw.get("industry"),
            country=raw.get("country", "IN"),
            currency=raw.get("currency", "INR"),
            market_cap=raw.get("market_cap"),
            description=raw.get("description"),
            website=raw.get("website"),
            employees=raw.get("employees"),
            data_source=FundamentalDataSource.INDIAN_PROVIDER,
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

        comp_data = INDIAN_FINANCIAL_STATEMENTS.get(canonical, {})
        raw_periods = comp_data.get(st_key, [])

        # Filter by period_type if requested
        p_type_filter = period_type.strip().upper()
        if p_type_filter in ["ANNUAL", "QUARTERLY"]:
            filtered = [p for p in raw_periods if p.get("period_type", "ANNUAL") == p_type_filter]
            if filtered:
                raw_periods = filtered

        if not raw_periods:
            # Construct standard realistic fallback periods for Indian stock
            if st_key == "income":
                raw_periods = [
                    {"period": "2024-FY", "period_type": "ANNUAL", "fiscal_year": 2024, "fiscal_quarter": "FY", "revenue": 185000000000.0, "cost_of_revenue": 115000000000.0, "gross_profit": 70000000000.0, "operating_expenses": 32000000000.0, "operating_income": 38000000000.0, "ebitda": 45000000000.0, "ebit": 38000000000.0, "interest_expense": 4200000000.0, "tax_expense": 8500000000.0, "net_income": 25300000000.0, "eps": 42.5, "shares_outstanding": 600000000},
                    {"period": "2023-FY", "period_type": "ANNUAL", "fiscal_year": 2023, "fiscal_quarter": "FY", "revenue": 162000000000.0, "cost_of_revenue": 102000000000.0, "gross_profit": 60000000000.0, "operating_expenses": 28000000000.0, "operating_income": 32000000000.0, "ebitda": 38000000000.0, "ebit": 32000000000.0, "interest_expense": 3800000000.0, "tax_expense": 7100000000.0, "net_income": 21100000000.0, "eps": 35.2, "shares_outstanding": 600000000},
                ]
            elif st_key == "balance_sheet":
                raw_periods = [
                    {"period": "2024-FY", "period_type": "ANNUAL", "fiscal_year": 2024, "fiscal_quarter": "FY", "cash_and_equivalents": 32000000000.0, "receivables": 24000000000.0, "inventory": 18000000000.0, "total_current_assets": 85000000000.0, "total_assets": 240000000000.0, "current_liabilities": 45000000000.0, "short_term_debt": 8000000000.0, "long_term_debt": 32000000000.0, "total_debt": 40000000000.0, "total_liabilities": 95000000000.0, "retained_earnings": 115000000000.0, "total_equity": 145000000000.0},
                ]
            else:
                raw_periods = [
                    {"period": "2024-FY", "period_type": "ANNUAL", "fiscal_year": 2024, "fiscal_quarter": "FY", "operating_cash_flow": 34000000000.0, "capital_expenditures": -14000000000.0, "free_cash_flow": 20000000000.0, "investing_cash_flow": -16000000000.0, "financing_cash_flow": -12000000000.0, "dividends_paid": -7500000000.0},
                ]

        return FinancialStatementsContainer(
            symbol=canonical,
            statement_type=st_key,
            period_type=FinancialPeriodType(period_type.upper()) if period_type.upper() in ["ANNUAL", "QUARTERLY", "TTM"] else FinancialPeriodType.ANNUAL,
            currency="INR",
            periods=raw_periods,
            data_source=FundamentalDataSource.INDIAN_PROVIDER,
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
                currency="INR",
                revenue=p.get("revenue", 100000000.0),
                gross_profit=p.get("gross_profit"),
                operating_income=p.get("operating_income"),
                ebitda=p.get("ebitda"),
                ebit=p.get("ebit"),
                interest_expense=p.get("interest_expense"),
                tax_expense=p.get("tax_expense"),
                net_income=p.get("net_income", 10000000.0),
                eps=p.get("eps"),
                data_source=FundamentalDataSource.INDIAN_PROVIDER,
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
                currency="INR",
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
                data_source=FundamentalDataSource.INDIAN_PROVIDER,
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
                currency="INR",
                operating_cash_flow=p.get("operating_cash_flow", 20000000.0),
                capital_expenditures=p.get("capital_expenditures"),
                free_cash_flow=p.get("free_cash_flow"),
                dividends_paid=p.get("dividends_paid"),
                data_source=FundamentalDataSource.INDIAN_PROVIDER,
                data_status=FundamentalDataStatus.DEMO,
            )

        mcap = profile.market_cap if profile else None
        ratios = ratio_engine.compute_all_ratios(
            symbol=canonical,
            income=latest_inc,
            balance=latest_bal,
            cashflow=latest_cf,
            market_cap=mcap,
            data_source=FundamentalDataSource.INDIAN_PROVIDER,
            data_status=FundamentalDataStatus.DEMO,
        )

        return FundamentalOverviewData(
            symbol=canonical,
            name=profile.name if profile else canonical,
            sector=profile.sector if profile else "Indian Equities",
            exchange=profile.exchange if profile else "NSE",
            currency="INR",
            profile=profile,
            valuation=ratios.valuation,
            profitability=ratios.profitability,
            financial_health=ratios.leverage,
            liquidity=ratios.liquidity,
            efficiency=ratios.efficiency,
            latest_income=latest_inc,
            latest_balance=latest_bal,
            latest_cashflow=latest_cf,
            data_source=FundamentalDataSource.INDIAN_PROVIDER,
            data_status=FundamentalDataStatus.DEMO,
            updated_at=datetime.utcnow().isoformat(),
        )
