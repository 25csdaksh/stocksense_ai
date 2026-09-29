"""
Correlation Dynamics, CAPM Beta & Contagion Network Graph Unit Tests.
"""
import pytest
import numpy as np
import pandas as pd
from app.analytics.correlation import (
    RollingCorrelationEngine,
    GrangerCausalityAnalyzer,
    MarketRelationshipGraph
)


@pytest.fixture
def returns_df():
    np.random.seed(42)
    n = 100
    market = np.random.normal(0.0005, 0.012, n)
    aapl = 1.15 * market + np.random.normal(0, 0.005, n)
    msft = 1.05 * market + np.random.normal(0, 0.004, n)
    nvda = 1.80 * market + np.random.normal(0, 0.008, n)

    return pd.DataFrame({
        "SPY": market,
        "AAPL": aapl,
        "MSFT": msft,
        "NVDA": nvda
    })


def test_correlation_matrix_computation(returns_df):
    res = RollingCorrelationEngine.compute_matrix(returns_df, method="pearson")
    assert "assets" in res
    assert len(res["assets"]) == 4
    assert "matrix" in res
    assert len(res["top_pairs"]) > 0
    # AAPL and MSFT should have high correlation
    pair = next((p for p in res["top_pairs"] if (p["asset_a"] == "AAPL" and p["asset_b"] == "MSFT") or (p["asset_a"] == "MSFT" and p["asset_b"] == "AAPL")), None)
    assert pair is not None
    assert pair["correlation"] > 0.5


def test_compute_capm_beta(returns_df):
    res = RollingCorrelationEngine.compute_beta(returns_df["NVDA"], returns_df["SPY"])
    assert "beta" in res
    assert "alpha" in res
    assert "r_squared" in res
    assert res["beta"] > 1.2  # NVDA beta simulated at ~1.8


def test_market_relationship_graph(returns_df):
    meta = {
        "SPY": {"name": "S&P 500 ETF", "sector": "Index ETF"},
        "AAPL": {"name": "Apple Inc.", "sector": "Information Technology"},
        "MSFT": {"name": "Microsoft Corp.", "sector": "Information Technology"},
        "NVDA": {"name": "NVIDIA Corp.", "sector": "Information Technology"}
    }
    graph_builder = MarketRelationshipGraph(threshold=0.40)
    res = graph_builder.build_graph(returns_df, meta)

    assert "nodes" in res
    assert "edges" in res
    assert len(res["nodes"]) == 4
    assert len(res["edges"]) > 0
    assert "network_metrics" in res
    assert res["network_metrics"]["total_nodes"] == 4
