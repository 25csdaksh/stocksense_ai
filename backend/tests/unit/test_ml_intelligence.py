"""
Unit Tests for Machine Learning & Quantitative Intelligence Modules.
Verifies Isolation Forest Anomaly Detection, GARCH(1,1) Volatility Forecasting, NetworkX Relationship Graph, and Stock DNA Radar.
"""
import pytest
import numpy as np
import pandas as pd
from app.analytics.anomaly import MarketAnomalyDetector, GARCHVolatilityModel
from app.analytics.correlation import MarketRelationshipGraph
from app.analytics.stock_dna import StockDNAProfiler
from app.analytics.scenario import MonteCarloSimulator, MacroScenarioSimulator, HistoricalStressTester


def test_isolation_forest_anomaly_detection():
    detector = MarketAnomalyDetector(contamination=0.08)
    
    # Generate synthetic price/volume time-series with artificial outlier spikes
    np.random.seed(42)
    n = 100
    dates = pd.date_range("2026-01-01", periods=n)
    prices = 100.0 + np.cumsum(np.random.normal(0.1, 1.5, n))
    volumes = np.random.uniform(1_000_000, 5_000_000, n)

    # Inject anomaly at day 50: sudden 15% price crash with 10x volume spike
    prices[50] = prices[49] * 0.85
    volumes[50] = 50_000_000

    bars = [
        {
            "time": dates[i].strftime("%Y-%m-%d"),
            "open": prices[i] * 0.99,
            "high": prices[i] * 1.01,
            "low": prices[i] * 0.98,
            "close": prices[i],
            "volume": volumes[i]
        }
        for i in range(n)
    ]

    res = detector.analyze_ticker("TEST_ASSET", bars)
    assert "anomalies_detected" in res
    assert "active_anomalies" in res
    assert "volatility_regime" in res
    assert "stress_score" in res


def test_garch_volatility_forecasting():
    model = GARCHVolatilityModel()
    np.random.seed(123)
    returns = pd.Series(np.random.normal(0.0005, 0.02, 150))

    model.fit(returns)
    assert model.omega > 0
    assert model.alpha > 0
    assert model.beta > 0

    forecast = model.forecast(returns, horizon=10)
    assert "forecast_next_days" in forecast
    assert len(forecast["forecast_next_days"]) == 10
    assert "regime" in forecast


def test_market_relationship_graph():
    graph_builder = MarketRelationshipGraph(threshold=0.30)
    
    # Generate 5 correlated asset return series
    np.random.seed(99)
    assets = ["AAPL", "MSFT", "NVDA", "GOOGL", "AMZN"]
    returns_matrix = pd.DataFrame(
        np.random.multivariate_normal(
            mean=[0.001]*5,
            cov=np.full((5, 5), 0.0004) + np.eye(5) * 0.0002,
            size=100
        ),
        columns=assets
    )
    metadata = {a: {"name": a, "sector": "Tech"} for a in assets}

    graph_res = graph_builder.build_graph(returns_matrix, metadata)
    assert "nodes" in graph_res
    assert "edges" in graph_res
    assert "network_metrics" in graph_res
    assert len(graph_res["nodes"]) == 5
    assert graph_res["network_metrics"]["total_nodes"] == 5


def test_stock_dna_5_factor_radar():
    profiler = StockDNAProfiler()
    fundamentals = {"pe_ratio": 24.5, "pb_ratio": 8.2, "roe_pct": 32.0, "net_margin_pct": 26.0}
    price_metrics = {"beta": 1.15, "annualized_volatility": 24.0, "return_3m_pct": 12.0, "return_1y_pct": 35.0}

    dna = profiler.calculate("NVDA", fundamentals, price_metrics)
    assert "factor_scores" in dna
    assert "radar_data" in dna
    assert "dominant_persona" in dna
    assert len(dna["radar_data"]) == 5
    factors = {item["factor"] for item in dna["radar_data"]}
    assert {"Value", "Growth", "Quality", "Momentum", "Low Volatility"}.issubset(factors)


def test_scenario_monte_carlo_merton_jump():
    sim = MonteCarloSimulator()
    res = sim.simulate(current_price=150.0, drift=0.08, volatility=0.25, days=90, iterations=1000, jump_intensity=0.05)

    assert res["initial_price"] == 150.0
    assert "expected_terminal_price_p50" in res
    assert "value_at_risk_95_pct" in res
    assert "cvar_expected_shortfall_99_pct" in res
    assert len(res["fan_chart"]) > 0
    assert len(res["distribution_histogram"]) > 0
