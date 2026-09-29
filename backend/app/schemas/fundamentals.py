"""
Fundamentals & Valuation Schemas.
"""
from typing import List, Dict, Any, Optional
from pydantic import BaseModel


class ValuationMultiples(BaseModel):
    pe_ratio: Optional[float] = None
    forward_pe: Optional[float] = None
    pb_ratio: Optional[float] = None
    ev_ebitda: Optional[float] = None
    fcf_yield_pct: Optional[float] = None


class ProfitabilityMetrics(BaseModel):
    gross_margin_pct: Optional[float] = None
    operating_margin_pct: Optional[float] = None
    net_margin_pct: Optional[float] = None
    roe_pct: Optional[float] = None
    roa_pct: Optional[float] = None


class FinancialHealthMetrics(BaseModel):
    current_ratio: Optional[float] = None
    debt_to_equity: Optional[float] = None
    interest_coverage_ratio: Optional[float] = None
    altman_z_score: Optional[float] = None
    health_score: str


class FundamentalOverviewResponse(BaseModel):
    ticker: str
    name: str
    sector: str
    valuation: ValuationMultiples
    profitability: ProfitabilityMetrics
    financial_health: FinancialHealthMetrics


class FinancialStatementsResponse(BaseModel):
    ticker: str
    statement_type: str
    periods: List[Dict[str, Any]]
