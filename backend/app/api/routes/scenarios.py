"""
Scenario Analysis, Monte Carlo Simulation & Macro Stress API Routes with Database Logging.
"""
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.schemas.scenario import (
    MonteCarloRequest,
    MonteCarloResponse,
    HistoricalStressRequest,
    HistoricalStressResponse,
    MacroShockRequest,
    MacroShockResponse
)
from app.services.scenario_service import scenario_service
from app.db.session import get_db_session
from app.db.repositories.scenario_repository import ScenarioRepository

router = APIRouter(prefix="/scenarios", tags=["Scenario Simulation & Stress Testing"])


@router.post("/monte-carlo", response_model=MonteCarloResponse)
@router.post("/analyze", response_model=MonteCarloResponse)
async def run_monte_carlo_simulation(
    req: MonteCarloRequest,
    db: AsyncSession = Depends(get_db_session)
):
    """Executes stochastic Merton Jump Diffusion Monte Carlo simulation with VaR/CVaR and fan charts."""
    res = await scenario_service.run_monte_carlo(
        ticker=req.ticker,
        drift_annualized=req.drift_annualized,
        volatility_annualized=req.volatility_annualized,
        days=req.days,
        iterations=req.iterations,
        jump_intensity=req.jump_intensity
    )
    try:
        repo = ScenarioRepository(db)
        await repo.save_report(
            ticker=req.ticker,
            scenario_type="MONTE_CARLO",
            parameters=req.model_dump(),
            results={
                "expected_terminal_price_p50": res.get("expected_terminal_price_p50"),
                "value_at_risk_95_pct": res.get("value_at_risk_95_pct"),
                "cvar_expected_shortfall_99_pct": res.get("cvar_expected_shortfall_99_pct")
            }
        )
    except Exception:
        pass
    return res


@router.post("/historical-stress", response_model=HistoricalStressResponse)
async def run_historical_stress_test(
    req: HistoricalStressRequest,
    db: AsyncSession = Depends(get_db_session)
):
    """Simulates portfolio and asset drawdown during historical market crises (2008 GFC, 2020 COVID, etc.)."""
    res = await scenario_service.run_historical_stress(
        ticker=req.ticker,
        current_price=req.current_price,
        sector=req.sector,
        beta=req.beta
    )
    try:
        repo = ScenarioRepository(db)
        await repo.save_report(
            ticker=req.ticker,
            scenario_type="HISTORICAL_STRESS",
            parameters=req.model_dump(),
            results={"scenario_results": {k: v.get("projected_drawdown_pct") for k, v in res.get("scenario_results", {}).items()}}
        )
    except Exception:
        pass
    return res


@router.post("/macro-shock", response_model=MacroShockResponse)
async def run_macro_shock_simulation(
    req: MacroShockRequest,
    db: AsyncSession = Depends(get_db_session)
):
    """Simulates multi-variable macroeconomic elasticity shocks across rates, inflation, oil, and GDP."""
    res = await scenario_service.run_macro_shock(
        ticker=req.ticker,
        rate_shock_bps=req.rate_shock_bps,
        inflation_shock_pct=req.inflation_shock_pct,
        oil_shock_pct=req.oil_shock_pct,
        gdp_shock_pct=req.gdp_shock_pct
    )
    try:
        repo = ScenarioRepository(db)
        await repo.save_report(
            ticker=req.ticker,
            scenario_type="MACRO_SHOCK",
            parameters=req.model_dump(),
            results={
                "projected_price": res.get("projected_price"),
                "total_projected_return_pct": res.get("total_projected_return_pct")
            }
        )
    except Exception:
        pass
    return res
