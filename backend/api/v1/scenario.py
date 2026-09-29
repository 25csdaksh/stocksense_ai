"""
Scenario Simulator, Monte Carlo & Stress Testing Endpoints.
"""
from fastapi import APIRouter
from schemas.scenario_schema import (
    MonteCarloRequest,
    MonteCarloResponse,
    HistoricalStressRequest,
    HistoricalStressResponse,
    MacroShockRequest,
    MacroShockResponse
)
from services.market_data_service import market_data_service, SUPPORTED_UNIVERSE
from core.guardrails import FINANCIAL_DISCLAIMER_MD

import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", "ml-engine")))
from engine import ml_engine

router = APIRouter(prefix="/scenario", tags=["Scenario Simulator"])


@router.post("/monte-carlo", response_model=MonteCarloResponse)
async def run_monte_carlo_simulation(req: MonteCarloRequest):
    """Executes Merton Jump Diffusion Monte Carlo simulation (1,000–20,000 paths)."""
    ticker = req.ticker.upper()
    quote = market_data_service.get_quote(ticker)
    price = req.current_price if req.current_price is not None else quote["price"]

    sim_res = ml_engine.run_monte_carlo(
        current_price=price,
        mu=req.drift_annualized,
        sigma=req.volatility_annualized,
        days=req.days,
        iterations=req.iterations,
        jump_intensity=req.jump_intensity
    )

    sim_res["ticker"] = ticker
    sim_res["disclaimer"] = FINANCIAL_DISCLAIMER_MD.strip()
    return sim_res


@router.post("/historical-stress", response_model=HistoricalStressResponse)
async def run_historical_stress(req: HistoricalStressRequest):
    """Replays portfolio drawdowns across 2008 GFC, 2020 COVID, 2022 Fed Rate Shock, and 2000 Dot-com."""
    ticker = req.ticker.upper()
    quote = market_data_service.get_quote(ticker)
    price = req.current_price if req.current_price is not None else quote["price"]
    meta = SUPPORTED_UNIVERSE.get(ticker, {})

    sector = req.sector or meta.get("sector", "Information Technology")
    beta = req.beta or meta.get("beta", 1.10)

    stress_res = ml_engine.run_historical_stress(
        ticker=ticker,
        current_price=price,
        sector=sector,
        beta=beta
    )
    stress_res["disclaimer"] = FINANCIAL_DISCLAIMER_MD.strip()
    return stress_res


@router.post("/macro-shock", response_model=MacroShockResponse)
async def run_macro_shock(req: MacroShockRequest):
    """Simulates customized multi-variable macroeconomic shock scenarios."""
    ticker = req.ticker.upper()
    quote = market_data_service.get_quote(ticker)
    price = req.current_price if req.current_price is not None else quote["price"]
    meta = SUPPORTED_UNIVERSE.get(ticker, {})

    sector = req.sector or meta.get("sector", "Information Technology")
    beta = req.beta or meta.get("beta", 1.10)

    shock_res = ml_engine.run_macro_shock(
        ticker=ticker,
        current_price=price,
        sector=sector,
        beta=beta,
        rate_shock_bps=req.rate_shock_bps,
        inflation_shock_pct=req.inflation_shock_pct,
        oil_shock_pct=req.oil_shock_pct,
        gdp_shock_pct=req.gdp_shock_pct,
        usd_shock_pct=req.usd_shock_pct
    )
    shock_res["disclaimer"] = FINANCIAL_DISCLAIMER_MD.strip()
    return shock_res
