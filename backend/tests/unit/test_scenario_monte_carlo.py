"""
Unit Tests: Merton Jump Diffusion Monte Carlo & Macro Stress Models.
"""
import pytest
from app.analytics.scenario import (
    MonteCarloSimulator,
    HistoricalStressTester,
    MacroScenarioSimulator
)


def test_monte_carlo_merton_simulation():
    mc = MonteCarloSimulator(random_seed=42)
    res = mc.simulate(
        current_price=150.0,
        drift_annualized=0.08,
        volatility_annualized=0.25,
        days=60,
        iterations=2000,
        jump_intensity=0.05
    )

    assert res["initial_price"] == 150.0
    assert res["days"] == 60
    assert "expected_terminal_price_p50" in res
    assert "value_at_risk_95_pct" in res
    assert len(res["fan_chart"]) == 61


def test_historical_stress_tester():
    tester = HistoricalStressTester()
    res = tester.stress_test(ticker="AAPL", current_price=200.0, sector="Information Technology", beta=1.15)

    assert res["ticker"] == "AAPL"
    assert "GFC_2008" in res["scenario_results"]
    assert "COVID_2020" in res["scenario_results"]


def test_macro_scenario_simulator():
    macro = MacroScenarioSimulator()
    res = macro.simulate(
        ticker="AAPL",
        current_price=200.0,
        rate_shock_bps=100.0,
        inflation_shock_pct=1.5
    )

    assert res["ticker"] == "AAPL"
    assert "projected_price" in res
    assert "factor_decomposition" in res
