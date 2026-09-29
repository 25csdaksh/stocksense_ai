"""
Scenario Analysis, Monte Carlo Simulation & Macro Stress API Routes.
"""
from fastapi import APIRouter
from app.schemas.scenario import (
    MonteCarloRequest,
    MonteCarloResponse,
    HistoricalStressRequest,
    HistoricalStressResponse,
    MacroShockRequest,
    MacroShockResponse
)
from app.services.scenario_service import scenario_service

router = APIRouter(prefix="/scenarios", tags=["Scenario Simulation & Stress Testing"])


@router.post("/monte-carlo", response_model=MonteCarloResponse)
@router.post("/analyze", response_model=MonteCarloResponse)
async def run_monte_carlo_simulation(req: MonteCarloRequest):
    """Executes stochastic Merton Jump Diffusion Monte Carlo simulation with VaR/CVaR and fan charts."""
    return await scenario_service.run_monte_carlo(
        ticker=req.ticker,
        drift_annualized=req.drift_annualized,
        volatility_annualized=req.volatility_annualized,
        days=req.days,
        iterations=req.iterations,
        jump_intensity=req.jump_intensity
    )


@router.post("/historical-stress", response_model=HistoricalStressResponse)
async def run_historical_stress_test(req: HistoricalStressRequest):
    """Simulates portfolio and asset drawdown during historical market crises (2008 GFC, 2020 COVID, etc.)."""
    return await scenario_service.run_historical_stress(
        ticker=req.ticker,
        current_price=req.current_price,
        sector=req.sector,
        beta=req.beta
    )


@router.post("/macro-shock", response_model=MacroShockResponse)
async def run_macro_shock_simulation(req: MacroShockRequest):
    """Simulates multi-variable macroeconomic elasticity shocks across rates, inflation, oil, and GDP."""
    return await scenario_service.run_macro_shock(
        ticker=req.ticker,
        rate_shock_bps=req.rate_shock_bps,
        inflation_shock_pct=req.inflation_shock_pct,
        oil_shock_pct=req.oil_shock_pct,
        gdp_shock_pct=req.gdp_shock_pct
    )
