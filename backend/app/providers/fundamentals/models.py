"""
MarketMind AI — Strongly Typed Normalized Fundamentals & Financial Statement Models.
Phase 6.6: Multi-Market Company Profiles, Income Statements, Balance Sheets,
Cash Flows, and Deterministic Financial Ratios with strict data provenance.
"""
from typing import Optional, List, Dict, Any, Union
from enum import Enum
from datetime import datetime
from pydantic import BaseModel, Field, ConfigDict


class FundamentalDataStatus(str, Enum):
    LIVE = "LIVE"
    DEMO = "DEMO"
    STALE = "STALE"
    UNAVAILABLE = "UNAVAILABLE"


class FundamentalDataSource(str, Enum):
    ZERODHA = "ZERODHA"
    YFINANCE = "YFINANCE"
    INDIAN_PROVIDER = "INDIAN_PROVIDER"
    SEC_EDGAR = "SEC_EDGAR"
    DEMO = "DEMO"
    SYSTEM = "SYSTEM"
    OTHER = "OTHER"


class FinancialPeriodType(str, Enum):
    ANNUAL = "ANNUAL"
    QUARTERLY = "QUARTERLY"
    TTM = "TTM"


# =========================================================================
# Company Profile Model
# =========================================================================

class CompanyProfileData(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    symbol: str = Field(..., description="Normalized ticker symbol (e.g., RELIANCE.NS, AAPL)")
    name: str = Field(..., description="Common company name")
    legal_name: Optional[str] = Field(None, description="Full legal corporate name")
    exchange: str = Field("NSE", description="Exchange code (NSE, BSE, NASDAQ, NYSE)")
    isin: Optional[str] = Field(None, description="International Securities Identification Number")
    sector: str = Field("General", description="Macro industry sector")
    industry: Optional[str] = Field(None, description="Specific industry classification")
    country: str = Field("IN", description="Country of primary incorporation")
    currency: str = Field("INR", description="Reporting currency (INR, USD, etc.)")
    market_cap: Optional[float] = Field(None, description="Total market capitalization")
    description: Optional[str] = Field(None, description="Business description and summary")
    website: Optional[str] = Field(None, description="Official company website")
    employees: Optional[int] = Field(None, description="Total full-time employees")
    cik: Optional[str] = Field(None, description="SEC Central Index Key if applicable")
    data_source: FundamentalDataSource = Field(FundamentalDataSource.DEMO, description="Source provider")
    data_status: FundamentalDataStatus = Field(FundamentalDataStatus.DEMO, description="Provenance status")
    updated_at: str = Field(default_factory=lambda: datetime.utcnow().isoformat())


# =========================================================================
# Financial Statement Line Item Models
# =========================================================================

class IncomeStatementData(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    symbol: str
    period_type: FinancialPeriodType = FinancialPeriodType.ANNUAL
    period_start: Optional[str] = None
    period_end: str
    fiscal_year: int
    fiscal_quarter: Optional[str] = None  # Q1, Q2, Q3, Q4 or FY
    reported_at: Optional[str] = None
    currency: str = "INR"
    data_source: FundamentalDataSource = FundamentalDataSource.DEMO
    data_status: FundamentalDataStatus = FundamentalDataStatus.DEMO

    # Income Statement Line Items (in reporting currency)
    revenue: float = Field(..., description="Total gross/operating revenue")
    cost_of_revenue: Optional[float] = Field(None, description="Cost of goods/services sold")
    gross_profit: Optional[float] = Field(None, description="Gross profit")
    operating_expenses: Optional[float] = Field(None, description="Selling, general and admin + R&D")
    operating_income: Optional[float] = Field(None, description="Operating income (EBIT)")
    ebitda: Optional[float] = Field(None, description="Earnings before interest, taxes, depr & amort")
    ebit: Optional[float] = Field(None, description="Earnings before interest and taxes")
    interest_expense: Optional[float] = Field(None, description="Interest and finance charges")
    tax_expense: Optional[float] = Field(None, description="Income tax provision")
    net_income: float = Field(..., description="Net income after tax (can be negative)")
    eps: Optional[float] = Field(None, description="Basic earnings per share")
    diluted_eps: Optional[float] = Field(None, description="Diluted earnings per share")
    shares_outstanding: Optional[float] = Field(None, description="Weighted average shares")


class BalanceSheetData(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    symbol: str
    period_type: FinancialPeriodType = FinancialPeriodType.ANNUAL
    period_start: Optional[str] = None
    period_end: str
    fiscal_year: int
    fiscal_quarter: Optional[str] = None
    reported_at: Optional[str] = None
    currency: str = "INR"
    data_source: FundamentalDataSource = FundamentalDataSource.DEMO
    data_status: FundamentalDataStatus = FundamentalDataStatus.DEMO

    # Assets
    cash_and_equivalents: Optional[float] = None
    short_term_investments: Optional[float] = None
    receivables: Optional[float] = None
    inventory: Optional[float] = None
    total_current_assets: Optional[float] = None
    property_plant_equipment: Optional[float] = None
    goodwill_and_intangibles: Optional[float] = None
    total_assets: float = Field(..., description="Total corporate assets")

    # Liabilities
    current_liabilities: Optional[float] = None
    short_term_debt: Optional[float] = None
    accounts_payable: Optional[float] = None
    long_term_debt: Optional[float] = None
    total_debt: Optional[float] = None
    total_liabilities: float = Field(..., description="Total corporate liabilities")

    # Equity
    common_stock: Optional[float] = None
    retained_earnings: Optional[float] = None
    total_equity: float = Field(..., description="Total stockholders equity")


class CashFlowData(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    symbol: str
    period_type: FinancialPeriodType = FinancialPeriodType.ANNUAL
    period_start: Optional[str] = None
    period_end: str
    fiscal_year: int
    fiscal_quarter: Optional[str] = None
    reported_at: Optional[str] = None
    currency: str = "INR"
    data_source: FundamentalDataSource = FundamentalDataSource.DEMO
    data_status: FundamentalDataStatus = FundamentalDataStatus.DEMO

    # Cash Flow Activities (can be negative)
    operating_cash_flow: float = Field(..., description="Net cash from operating activities")
    capital_expenditures: Optional[float] = Field(None, description="Capital expenditures (usually negative)")
    free_cash_flow: Optional[float] = Field(None, description="Operating cash flow - CapEx")
    investing_cash_flow: Optional[float] = Field(None, description="Net cash from investing activities")
    financing_cash_flow: Optional[float] = Field(None, description="Net cash from financing activities")
    dividends_paid: Optional[float] = Field(None, description="Total cash dividends paid")
    stock_based_compensation: Optional[float] = Field(None, description="Non-cash share-based comp")


# =========================================================================
# Computed Financial Ratios Model
# =========================================================================

class ValuationRatios(BaseModel):
    pe_ratio: Optional[float] = None
    forward_pe: Optional[float] = None
    ps_ratio: Optional[float] = None
    pb_ratio: Optional[float] = None
    ev_ebitda: Optional[float] = None
    peg_ratio: Optional[float] = None
    fcf_yield_pct: Optional[float] = None
    dividend_yield_pct: Optional[float] = None


class ProfitabilityRatios(BaseModel):
    gross_margin_pct: Optional[float] = None
    operating_margin_pct: Optional[float] = None
    ebitda_margin_pct: Optional[float] = None
    net_margin_pct: Optional[float] = None
    roe_pct: Optional[float] = None
    roa_pct: Optional[float] = None
    roic_pct: Optional[float] = None


class LeverageRatios(BaseModel):
    debt_to_equity: Optional[float] = None
    debt_to_assets: Optional[float] = None
    interest_coverage: Optional[float] = None
    altman_z_score: Optional[float] = None
    health_score: str = "HEALTHY"


class LiquidityRatios(BaseModel):
    current_ratio: Optional[float] = None
    quick_ratio: Optional[float] = None
    cash_ratio: Optional[float] = None


class EfficiencyRatios(BaseModel):
    asset_turnover: Optional[float] = None
    inventory_turnover: Optional[float] = None
    receivables_turnover: Optional[float] = None


class FinancialRatiosData(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    symbol: str
    valuation: ValuationRatios = Field(default_factory=ValuationRatios)
    profitability: ProfitabilityRatios = Field(default_factory=ProfitabilityRatios)
    leverage: LeverageRatios = Field(default_factory=LeverageRatios)
    liquidity: LiquidityRatios = Field(default_factory=LiquidityRatios)
    efficiency: EfficiencyRatios = Field(default_factory=EfficiencyRatios)
    data_source: FundamentalDataSource = FundamentalDataSource.DEMO
    data_status: FundamentalDataStatus = FundamentalDataStatus.DEMO
    calculated_at: str = Field(default_factory=lambda: datetime.utcnow().isoformat())


# =========================================================================
# Unified Fundamental Overview Model
# =========================================================================

class FundamentalOverviewData(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    symbol: str
    ticker: Optional[str] = None
    name: str
    sector: str
    exchange: Optional[str] = "NSE"
    currency: Optional[str] = "INR"
    pe_ratio: Optional[float] = None
    pb_ratio: Optional[float] = None
    profile: Optional[CompanyProfileData] = None
    valuation: ValuationRatios = Field(default_factory=ValuationRatios)
    profitability: ProfitabilityRatios = Field(default_factory=ProfitabilityRatios)
    financial_health: LeverageRatios = Field(default_factory=LeverageRatios)
    liquidity: Optional[LiquidityRatios] = None
    efficiency: Optional[EfficiencyRatios] = None
    latest_income: Optional[IncomeStatementData] = None
    latest_balance: Optional[BalanceSheetData] = None
    latest_cashflow: Optional[CashFlowData] = None
    data_source: FundamentalDataSource = FundamentalDataSource.DEMO
    data_status: FundamentalDataStatus = FundamentalDataStatus.DEMO
    updated_at: str = Field(default_factory=lambda: datetime.utcnow().isoformat())

    def model_post_init(self, __context: Any) -> None:
        if not self.ticker:
            self.ticker = self.symbol
        if self.pe_ratio is None and self.valuation and self.valuation.pe_ratio is not None:
            self.pe_ratio = self.valuation.pe_ratio
        if self.pb_ratio is None and self.valuation and self.valuation.pb_ratio is not None:
            self.pb_ratio = self.valuation.pb_ratio

    def __contains__(self, item: Any) -> bool:
        return hasattr(self, item) or item in self.__dict__

    def __iter__(self):
        return iter(self.model_dump())

    def keys(self):
        return self.model_dump().keys()

    def values(self):
        return self.model_dump().values()

    def items(self):
        return self.model_dump().items()

    def __getitem__(self, item: str) -> Any:
        if hasattr(self, item):
            val = getattr(self, item)
            # If it's a pydantic model, convert to dict when accessed via subscript if needed
            if hasattr(val, "model_dump"):
                return val.model_dump()
            return val
        data = self.model_dump()
        if item in data:
            return data[item]
        raise KeyError(item)

    def get(self, item: str, default: Any = None) -> Any:
        try:
            return self[item]
        except KeyError:
            return default


# =========================================================================
# Multi-Period Statements Container
# =========================================================================

class FinancialStatementsContainer(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    symbol: str
    ticker: Optional[str] = None
    statement_type: str = "income"  # income, balance_sheet, cash_flow
    period_type: FinancialPeriodType = FinancialPeriodType.ANNUAL
    currency: str = "INR"
    periods: List[Dict[str, Any]] = Field(default_factory=list)
    data_source: FundamentalDataSource = FundamentalDataSource.DEMO
    data_status: FundamentalDataStatus = FundamentalDataStatus.DEMO
    updated_at: str = Field(default_factory=lambda: datetime.utcnow().isoformat())

    def model_post_init(self, __context: Any) -> None:
        if not self.ticker:
            self.ticker = self.symbol

    def __contains__(self, item: Any) -> bool:
        return hasattr(self, item) or item in self.__dict__

    def __iter__(self):
        return iter(self.model_dump())

    def keys(self):
        return self.model_dump().keys()

    def values(self):
        return self.model_dump().values()

    def items(self):
        return self.model_dump().items()

    def __getitem__(self, item: str) -> Any:
        if hasattr(self, item):
            return getattr(self, item)
        data = self.model_dump()
        if item in data:
            return data[item]
        raise KeyError(item)

    def get(self, item: str, default: Any = None) -> Any:
        try:
            return self[item]
        except KeyError:
            return default


