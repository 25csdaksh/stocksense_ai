import numpy as np
import pandas as pd
import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "ml-engine")))
from engine import ml_engine


def test_monte_carlo_simulation():
    """Validates Monte Carlo jump diffusion quantiles, VaR, and fan chart integrity."""
    result = ml_engine.run_monte_carlo(
        current_price=200.0,
        mu=0.08,
        sigma=0.25,
        days=30,
        iterations=1000
    )

    assert result["initial_price"] == 200.0
    assert result["days"] == 30
    assert result["iterations"] == 1000
    assert "expected_terminal_price_p50" in result
    assert result["value_at_risk_95_pct"] < 0.0  # VaR return is negative
    assert result["cvar_expected_shortfall_99_pct"] <= result["value_at_risk_95_pct"]
    assert len(result["fan_chart"]) == 31  # Day 0 to 30
    assert len(result["distribution_histogram"]) > 0


def test_stock_dna_profiler():
    """Validates 5-factor scoring normalization and radar data generation."""
    dna = ml_engine.calculate_stock_dna(
        ticker="AAPL",
        fundamentals={"pe_ratio": 30.0, "roe": 0.35, "debt_to_equity": 0.5},
        price_metrics={"beta": 1.1, "annualized_volatility": 24.0, "return_3m_pct": 10.0, "return_1y_pct": 25.0}
    )

    assert dna["ticker"] == "AAPL"
    assert len(dna["radar_data"]) == 5
    scores = dna["factor_scores"]
    for factor in ["value", "growth", "quality", "momentum", "low_volatility"]:
        assert 0.0 <= scores[factor] <= 100.0
    assert isinstance(dna["dominant_persona"], str)


def test_anomaly_detection():
    """Validates Isolation Forest and GARCH on synthetic time series."""
    np.random.seed(42)
    dates = pd.date_range("2024-01-01", periods=60, freq="B")
    closes = [100.0]
    for _ in range(59):
        closes.append(closes[-1] * np.exp(np.random.normal(0, 0.015)))
    
    # Inject an acute volume & price anomaly
    volumes = np.random.normal(10_000_000, 1_000_000, size=60)
    volumes[45] = 65_000_000
    closes[45] = closes[44] * 1.08

    df = pd.DataFrame({
        "open": closes,
        "high": [c * 1.01 for c in closes],
        "low": [c * 0.99 for c in closes],
        "close": closes,
        "volume": volumes
    }, index=dates)

    pipeline_res = ml_engine.run_anomaly_pipeline(df, "TEST")
    assert pipeline_res["ticker"] == "TEST"
    assert "detected_anomalies" in pipeline_res
    assert "garch_volatility" in pipeline_res
    assert pipeline_res["garch_volatility"]["current_annualized_volatility_pct"] > 0


def test_historical_stress_testing():
    """Validates crisis drawdowns for an equity."""
    stress_res = ml_engine.run_historical_stress(
        ticker="NVDA",
        current_price=120.0,
        sector="Information Technology",
        beta=1.65
    )

    assert stress_res["ticker"] == "NVDA"
    assert "GFC_2008" in stress_res["scenario_results"]
    assert "COVID_2020" in stress_res["scenario_results"]
    assert stress_res["scenario_results"]["GFC_2008"]["projected_drawdown_pct"] < 0
    assert stress_res["scenario_results"]["GFC_2008"]["stressed_price"] < 120.0


def test_macro_shock_simulation():
    """Validates macro sensitivity calculation."""
    shock_res = ml_engine.run_macro_shock(
        ticker="AAPL",
        current_price=220.0,
        rate_shock_bps=150.0,
        inflation_shock_pct=2.0
    )

    assert shock_res["ticker"] == "AAPL"
    assert "projected_price" in shock_res
    assert "factor_decomposition" in shock_res
    assert "rates_effect_pct" in shock_res["factor_decomposition"]


if __name__ == "__main__":
    test_monte_carlo_simulation()
    test_stock_dna_profiler()
    test_anomaly_detection()
    test_historical_stress_testing()
    test_macro_shock_simulation()
    print("All quantitative & ML unit tests passed successfully!")
