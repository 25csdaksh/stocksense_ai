"""
Scenario Simulation, Monte Carlo & Macro Elasticity Unit Tests.
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
    assert res["iterations"] == 2000
    assert "expected_terminal_price_p50" in res
    assert "value_at_risk_95_pct" in res
    assert "cvar_expected_shortfall_99_pct" in res
    assert len(res["fan_chart"]) == 61  # day 0 to 60
    assert len(res["distribution_histogram"]) == 25
    assert res["value_at_risk_99_pct"] <= res["value_at_risk_95_pct"]


def test_historical_stress_tester():
    stress_tester = HistoricalStressTester()
    res = stress_tester.stress_test(
        ticker="AAPL",
        current_price=200.0,
        sector="Information Technology",
        beta=1.15
    )

    assert res["ticker"] == "AAPL"
    assert res["current_price"] == 200.0
    assert "GFC_2008" in res["scenario_results"]
    assert "COVID_2020" in res["scenario_results"]
    assert "FED_TIGHTENING_2022" in res["scenario_results"]
    assert "DOT_COM_2000" in res["scenario_results"]

    gfc = res["scenario_results"]["GFC_2008"]
    assert gfc["stressed_price"] < 200.0
    assert gfc["projected_drawdown_pct"] < 0.0


def test_macro_scenario_simulator():
    macro_sim = MacroScenarioSimulator()
    res = macro_sim.simulate(
        ticker="AAPL",
        current_price=200.0,
        sector="Information Technology",
        beta=1.10,
        rate_shock_bps=100.0,
        inflation_shock_pct=1.5,
        oil_shock_pct=20.0,
        gdp_shock_pct=-1.0
    )

    assert res["ticker"] == "AAPL"
    assert "projected_price" in res
    assert "total_projected_return_pct" in res
    assert "factor_decomposition" in res
    decomp = res["factor_decomposition"]
    assert "rates_effect_pct" in decomp
    assert "inflation_effect_pct" in decomp
