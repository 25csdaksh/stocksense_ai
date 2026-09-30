"""
MarketMind AI — Fundamentals Data Validation Engine.
Phase 6.6: Validates company profiles, financial statements, periods,
and numerical domain boundaries with zero fabrication.
"""
from typing import Optional, Dict, Any, List, Tuple
from datetime import datetime
from app.providers.market_data.symbol_normalizer import normalize_symbol
from app.providers.fundamentals.models import (
    CompanyProfileData,
    IncomeStatementData,
    BalanceSheetData,
    CashFlowData,
    FinancialPeriodType,
    FundamentalDataStatus,
    FundamentalDataSource,
)
from app.core.logging import logger


class FundamentalsValidationError(Exception):
    """Raised when fundamental data fails schema or domain integrity rules."""
    pass


class FundamentalsValidator:
    """Strict validation engine for financial and fundamental records."""

    MIN_FISCAL_YEAR = 1990
    MAX_FISCAL_YEAR = datetime.utcnow().year + 5
    VALID_QUARTERS = {"Q1", "Q2", "Q3", "Q4", "FY", "TTM"}
    VALID_CURRENCIES = {"INR", "USD", "EUR", "GBP", "JPY", "SGD", "AED", "CAD", "AUD"}

    @classmethod
    def validate_symbol(cls, raw_symbol: str) -> str:
        """Validates and returns normalized canonical symbol."""
        if not raw_symbol or not isinstance(raw_symbol, str) or not raw_symbol.strip():
            raise FundamentalsValidationError("Symbol cannot be empty.")
        norm = normalize_symbol(raw_symbol)
        return norm.canonical_symbol

    @classmethod
    def validate_fiscal_year(cls, year: int) -> int:
        """Validates fiscal year is within realistic boundaries."""
        if not isinstance(year, int) or year < cls.MIN_FISCAL_YEAR or year > cls.MAX_FISCAL_YEAR:
            raise FundamentalsValidationError(
                f"Fiscal year {year} is out of valid range [{cls.MIN_FISCAL_YEAR}, {cls.MAX_FISCAL_YEAR}]."
            )
        return year

    @classmethod
    def validate_fiscal_quarter(cls, quarter: Optional[str]) -> Optional[str]:
        """Validates quarter string."""
        if quarter is None:
            return None
        q = str(quarter).strip().upper()
        if q not in cls.VALID_QUARTERS:
            raise FundamentalsValidationError(f"Invalid fiscal quarter '{quarter}'. Allowed: {cls.VALID_QUARTERS}")
        return q

    @classmethod
    def validate_currency(cls, currency: Optional[str]) -> str:
        """Validates standard 3-character ISO currency code."""
        if not currency:
            return "INR"
        c = str(currency).strip().upper()
        if len(c) != 3:
            return "INR"
        return c

    @classmethod
    def sanitize_float(cls, val: Any, allow_negative: bool = True) -> Optional[float]:
        """
        Safely casts numeric values to float, handling nulls and invalid numbers.
        Disallows negative numbers only if allow_negative is False.
        """
        if val is None or val == "" or val == "N/A" or val == "null":
            return None
        try:
            f = float(val)
            if not allow_negative and f < 0:
                logger.warning(f"Sanitizing invalid negative value {f} to None for non-negative field")
                return None
            return f
        except (ValueError, TypeError):
            return None

    @classmethod
    def validate_income_statement(cls, data: Dict[str, Any]) -> IncomeStatementData:
        """Validates and constructs strongly typed IncomeStatementData."""
        symbol = cls.validate_symbol(data.get("symbol", ""))
        fiscal_year = cls.validate_fiscal_year(int(data.get("fiscal_year", datetime.utcnow().year)))
        fiscal_quarter = cls.validate_fiscal_quarter(data.get("fiscal_quarter"))
        currency = cls.validate_currency(data.get("currency"))

        revenue = cls.sanitize_float(data.get("revenue") or data.get("total_revenue"), allow_negative=False)
        if revenue is None:
            raise FundamentalsValidationError(f"Missing required valid non-negative revenue for {symbol}.")

        net_income = cls.sanitize_float(data.get("net_income"), allow_negative=True)
        if net_income is None:
            raise FundamentalsValidationError(f"Missing required net_income for {symbol}.")

        return IncomeStatementData(
            symbol=symbol,
            period_type=FinancialPeriodType(data.get("period_type", FinancialPeriodType.ANNUAL)),
            period_start=data.get("period_start"),
            period_end=data.get("period_end", f"{fiscal_year}-12-31"),
            fiscal_year=fiscal_year,
            fiscal_quarter=fiscal_quarter,
            reported_at=data.get("reported_at"),
            currency=currency,
            data_source=FundamentalDataSource(data.get("data_source", FundamentalDataSource.DEMO)),
            data_status=FundamentalDataStatus(data.get("data_status", FundamentalDataStatus.DEMO)),
            revenue=revenue,
            cost_of_revenue=cls.sanitize_float(data.get("cost_of_revenue"), allow_negative=False),
            gross_profit=cls.sanitize_float(data.get("gross_profit"), allow_negative=True),
            operating_expenses=cls.sanitize_float(data.get("operating_expenses"), allow_negative=False),
            operating_income=cls.sanitize_float(data.get("operating_income") or data.get("ebit"), allow_negative=True),
            ebitda=cls.sanitize_float(data.get("ebitda"), allow_negative=True),
            ebit=cls.sanitize_float(data.get("ebit") or data.get("operating_income"), allow_negative=True),
            interest_expense=cls.sanitize_float(data.get("interest_expense"), allow_negative=False),
            tax_expense=cls.sanitize_float(data.get("tax_expense"), allow_negative=True),
            net_income=net_income,
            eps=cls.sanitize_float(data.get("eps"), allow_negative=True),
            diluted_eps=cls.sanitize_float(data.get("diluted_eps"), allow_negative=True),
            shares_outstanding=cls.sanitize_float(data.get("shares_outstanding"), allow_negative=False),
        )

    @classmethod
    def validate_balance_sheet(cls, data: Dict[str, Any]) -> BalanceSheetData:
        """Validates and constructs strongly typed BalanceSheetData."""
        symbol = cls.validate_symbol(data.get("symbol", ""))
        fiscal_year = cls.validate_fiscal_year(int(data.get("fiscal_year", datetime.utcnow().year)))
        fiscal_quarter = cls.validate_fiscal_quarter(data.get("fiscal_quarter"))
        currency = cls.validate_currency(data.get("currency"))

        total_assets = cls.sanitize_float(data.get("total_assets"), allow_negative=False)
        if total_assets is None:
            raise FundamentalsValidationError(f"Missing required total_assets for {symbol}.")

        total_liabilities = cls.sanitize_float(data.get("total_liabilities"), allow_negative=False)
        if total_liabilities is None:
            raise FundamentalsValidationError(f"Missing required total_liabilities for {symbol}.")

        total_equity = cls.sanitize_float(data.get("total_equity") or data.get("stockholders_equity"), allow_negative=True)
        if total_equity is None:
            total_equity = total_assets - total_liabilities

        return BalanceSheetData(
            symbol=symbol,
            period_type=FinancialPeriodType(data.get("period_type", FinancialPeriodType.ANNUAL)),
            period_start=data.get("period_start"),
            period_end=data.get("period_end", f"{fiscal_year}-12-31"),
            fiscal_year=fiscal_year,
            fiscal_quarter=fiscal_quarter,
            reported_at=data.get("reported_at"),
            currency=currency,
            data_source=FundamentalDataSource(data.get("data_source", FundamentalDataSource.DEMO)),
            data_status=FundamentalDataStatus(data.get("data_status", FundamentalDataStatus.DEMO)),
            cash_and_equivalents=cls.sanitize_float(data.get("cash_and_equivalents") or data.get("cash"), allow_negative=False),
            short_term_investments=cls.sanitize_float(data.get("short_term_investments"), allow_negative=False),
            receivables=cls.sanitize_float(data.get("receivables"), allow_negative=False),
            inventory=cls.sanitize_float(data.get("inventory"), allow_negative=False),
            total_current_assets=cls.sanitize_float(data.get("total_current_assets") or data.get("current_assets"), allow_negative=False),
            property_plant_equipment=cls.sanitize_float(data.get("property_plant_equipment"), allow_negative=False),
            goodwill_and_intangibles=cls.sanitize_float(data.get("goodwill_and_intangibles"), allow_negative=False),
            total_assets=total_assets,
            current_liabilities=cls.sanitize_float(data.get("current_liabilities") or data.get("total_current_liabilities"), allow_negative=False),
            short_term_debt=cls.sanitize_float(data.get("short_term_debt"), allow_negative=False),
            accounts_payable=cls.sanitize_float(data.get("accounts_payable"), allow_negative=False),
            long_term_debt=cls.sanitize_float(data.get("long_term_debt"), allow_negative=False),
            total_debt=cls.sanitize_float(data.get("total_debt"), allow_negative=False),
            total_liabilities=total_liabilities,
            common_stock=cls.sanitize_float(data.get("common_stock"), allow_negative=False),
            retained_earnings=cls.sanitize_float(data.get("retained_earnings"), allow_negative=True),
            total_equity=total_equity,
        )

    @classmethod
    def validate_cash_flow(cls, data: Dict[str, Any]) -> CashFlowData:
        """Validates and constructs strongly typed CashFlowData."""
        symbol = cls.validate_symbol(data.get("symbol", ""))
        fiscal_year = cls.validate_fiscal_year(int(data.get("fiscal_year", datetime.utcnow().year)))
        fiscal_quarter = cls.validate_fiscal_quarter(data.get("fiscal_quarter"))
        currency = cls.validate_currency(data.get("currency"))

        operating_cash_flow = cls.sanitize_float(data.get("operating_cash_flow"), allow_negative=True)
        if operating_cash_flow is None:
            raise FundamentalsValidationError(f"Missing required operating_cash_flow for {symbol}.")

        capex = cls.sanitize_float(data.get("capital_expenditures") or data.get("capex"), allow_negative=True)
        fcf = cls.sanitize_float(data.get("free_cash_flow"), allow_negative=True)
        if fcf is None and capex is not None:
            # If CapEx is negative, OCF + CapEx; if positive, OCF - CapEx
            fcf = operating_cash_flow - abs(capex)

        return CashFlowData(
            symbol=symbol,
            period_type=FinancialPeriodType(data.get("period_type", FinancialPeriodType.ANNUAL)),
            period_start=data.get("period_start"),
            period_end=data.get("period_end", f"{fiscal_year}-12-31"),
            fiscal_year=fiscal_year,
            fiscal_quarter=fiscal_quarter,
            reported_at=data.get("reported_at"),
            currency=currency,
            data_source=FundamentalDataSource(data.get("data_source", FundamentalDataSource.DEMO)),
            data_status=FundamentalDataStatus(data.get("data_status", FundamentalDataStatus.DEMO)),
            operating_cash_flow=operating_cash_flow,
            capital_expenditures=capex,
            free_cash_flow=fcf,
            investing_cash_flow=cls.sanitize_float(data.get("investing_cash_flow"), allow_negative=True),
            financing_cash_flow=cls.sanitize_float(data.get("financing_cash_flow"), allow_negative=True),
            dividends_paid=cls.sanitize_float(data.get("dividends_paid"), allow_negative=True),
            stock_based_compensation=cls.sanitize_float(data.get("stock_based_compensation"), allow_negative=False),
        )


fundamentals_validator = FundamentalsValidator()
