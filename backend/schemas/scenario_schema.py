"""
Scenario Simulator & Stress Testing Pydantic Schemas.
"""
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field


class MonteCarloRequest(BaseModel):
    ticker: str = Field(default="AAPL", description="Target stock ticker")
    current_price: Optional[float] = Field(default=None, description="Optional custom initial price")
    drift_annualized: float = Field(default=0.08, description="Annualized expected drift (mu)")
    volatility_annualized: float = Field(default=0.25, description="Annualized volatility (sigma)")
    days: int = Field(default=90, ge=5, le=365, description="Simulation horizon in calendar/trading days")
    iterations: int = Field(default=5000, ge=100, le=20000, description="Number of Monte Carlo paths")
    jump_intensity: float = Field(default=0.05, ge=0.0, le=1.0, description="Poisson jump frequency")


class FanChartPoint(BaseModel):
    day: int
    p10: float
    p25: float
    p50: float
    p75: float
    p90: float


class DistributionBin(BaseModel):
    range_label: str
    midpoint: float
    frequency: int


class MonteCarloResponse(BaseModel):
    ticker: str
    initial_price: float
    days: int
    iterations: int
    annualized_drift_pct: float
    annualized_volatility_pct: float
    expected_terminal_price_p50: float
    terminal_p10_price: float
    terminal_p90_price: float
    value_at_risk_95_pct: float
    value_at_risk_99_pct: float
    cvar_expected_shortfall_95_pct: float
    cvar_expected_shortfall_99_pct: float
    probability_of_profit_pct: float
    prob_loss_exceeding_10pct: float
    prob_gain_exceeding_20pct: float
    fan_chart: List[FanChartPoint]
    distribution_histogram: List[DistributionBin]
    sample_paths: List[List[float]]
    disclaimer: str


class HistoricalStressRequest(BaseModel):
    ticker: str = Field(default="AAPL")
    current_price: Optional[float] = None
    sector: Optional[str] = "Information Technology"
    beta: Optional[float] = 1.10


class ScenarioCrisisResult(BaseModel):
    scenario_name: str
    period: str
    projected_drawdown_pct: float
    stressed_price: float
    estimated_loss_per_share: float
    description: str


class HistoricalStressResponse(BaseModel):
    ticker: str
    current_price: float
    sector: str
    beta: float
    scenario_results: Dict[str, ScenarioCrisisResult]
    disclaimer: str


class MacroShockRequest(BaseModel):
    ticker: str = Field(default="AAPL")
    current_price: Optional[float] = None
    sector: Optional[str] = "Information Technology"
    beta: Optional[float] = 1.10
    rate_shock_bps: float = Field(default=100.0, description="Yield shift in basis points (+/- 300bps)")
    inflation_shock_pct: float = Field(default=1.5, description="CPI Inflation change in %")
    oil_shock_pct: float = Field(default=20.0, description="Crude oil change in %")
    gdp_shock_pct: float = Field(default=-1.0, description="GDP real growth change in %")
    usd_shock_pct: float = Field(default=5.0, description="US Dollar index change in %")


class MacroFactorDecomposition(BaseModel):
    rates_effect_pct: float
    inflation_effect_pct: float
    oil_effect_pct: float
    gdp_effect_pct: float
    usd_effect_pct: float


class MacroShockResponse(BaseModel):
    ticker: str
    current_price: float
    projected_price: float
    total_projected_return_pct: float
    dollar_impact_per_share: float
    factor_decomposition: MacroFactorDecomposition
    parameters: Dict[str, Any]
    disclaimer: str
