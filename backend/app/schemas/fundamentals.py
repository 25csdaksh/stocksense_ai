"""
Fundamentals, Valuation & Financial Statement Schemas.
Phase 6.6: Extended schemas with strict provenance, multi-period statements,
ratios, company profiles, and backward-compatible fields.
"""
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field
from app.providers.fundamentals.models import (
    FundamentalDataStatus,
    FundamentalDataSource,
    FinancialPeriodType,
    CompanyProfileData,
    IncomeStatementData,
    BalanceSheetData,
    CashFlowData,
    FinancialRatiosData,
    ValuationRatios,
    ProfitabilityRatios,
    LeverageRatios,
    LiquidityRatios,
    EfficiencyRatios,
)


class ValuationMultiples(BaseModel):
    pe_ratio: Optional[float] = None
    forward_pe: Optional[float] = None
    ps_ratio: Optional[float] = None
    pb_ratio: Optional[float] = None
    ev_ebitda: Optional[float] = None
    peg_ratio: Optional[float] = None
    fcf_yield_pct: Optional[float] = None
    dividend_yield_pct: Optional[float] = None


class ProfitabilityMetrics(BaseModel):
    gross_margin_pct: Optional[float] = None
    operating_margin_pct: Optional[float] = None
    ebitda_margin_pct: Optional[float] = None
    net_margin_pct: Optional[float] = None
    roe_pct: Optional[float] = None
    roa_pct: Optional[float] = None
    roic_pct: Optional[float] = None


class FinancialHealthMetrics(BaseModel):
    current_ratio: Optional[float] = None
    quick_ratio: Optional[float] = None
    debt_to_equity: Optional[float] = None
    debt_to_assets: Optional[float] = None
    interest_coverage_ratio: Optional[float] = None
    altman_z_score: Optional[float] = None
    health_score: str = "HEALTHY"


class FundamentalOverviewResponse(BaseModel):
    ticker: str
    symbol: Optional[str] = None
    name: str
    sector: str
    exchange: Optional[str] = None
    currency: Optional[str] = "INR"
    valuation: ValuationMultiples
    profitability: ProfitabilityMetrics
    financial_health: FinancialHealthMetrics
    liquidity: Optional[LiquidityRatios] = None
    efficiency: Optional[EfficiencyRatios] = None
    data_source: Optional[str] = "DEMO"
    data_status: Optional[str] = "DEMO"
    updated_at: Optional[str] = None


class FinancialStatementsResponse(BaseModel):
    ticker: str
    symbol: Optional[str] = None
    statement_type: str
    period_type: Optional[str] = "ANNUAL"
    currency: Optional[str] = "INR"
    periods: List[Dict[str, Any]]
    data_source: Optional[str] = "DEMO"
    data_status: Optional[str] = "DEMO"
    updated_at: Optional[str] = None


class CompanyProfileResponse(BaseModel):
    ticker: str
    symbol: Optional[str] = None
    name: str
    legal_name: Optional[str] = None
    exchange: str = "NSE"
    isin: Optional[str] = None
    sector: str = "General"
    industry: Optional[str] = None
    country: str = "IN"
    currency: str = "INR"
    market_cap: Optional[float] = None
    description: Optional[str] = None
    website: Optional[str] = None
    employees: Optional[int] = None
    cik: Optional[str] = None
    data_source: str = "DEMO"
    data_status: str = "DEMO"
    updated_at: str


class FundamentalsHealthResponse(BaseModel):
    status: str = "HEALTHY"
    provider_status: Dict[str, str] = Field(default_factory=dict)
    records_processed: int = 0
    records_failed: int = 0
    duplicates_prevented: int = 0
    missing_fields_detected: int = 0
    last_successful_run: Optional[str] = None
    freshness_seconds: Optional[int] = None
    active_providers: List[str] = Field(default_factory=list)
