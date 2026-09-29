"""
Scenario Simulator, Monte Carlo, Historical Stress & Macro Shock Schemas.
"""
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field


class MonteCarloRequest(BaseModel):
    ticker: str = Field(default="AAPL")
    drift_annualized: float = Field(default=0.08)
    volatility_annualized: float = Field(default=0.25)
    days: int = Field(default=90, ge=5, le=365)
    iterations: int = Field(default=5000, ge=100, le=20000)
    jump_intensity: float = Field(default=0.05, ge=0.0, le=1.0)


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
    cvar_expected_shortfall_99_pct: float
    probability_of_profit_pct: float
    prob_loss_exceeding_10pct: float
    prob_gain_exceeding_20pct: float
    fan_chart: List[FanChartPoint]
    distribution_histogram: List[DistributionBin]
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
    rate_shock_bps: float = Field(default=100.0)
    inflation_shock_pct: float = Field(default=1.5)
    oil_shock_pct: float = Field(default=20.0)
    gdp_shock_pct: float = Field(default=-1.0)


class MacroShockResponse(BaseModel):
    ticker: str
    current_price: float
    projected_price: float
    total_projected_return_pct: float
    dollar_impact_per_share: float
    factor_decomposition: Dict[str, float]
    disclaimer: str
