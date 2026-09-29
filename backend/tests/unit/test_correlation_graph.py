"""
Unit Tests: Rolling Correlation, CAPM Beta & Contagion Graph.
"""
import pytest
import numpy as np
import pandas as pd
from app.analytics.correlation import (
    RollingCorrelationEngine,
    MarketRelationshipGraph
)


@pytest.fixture
def returns_data():
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


def test_correlation_matrix(returns_data):
    res = RollingCorrelationEngine.compute_matrix(returns_data, method="pearson")
    assert "assets" in res
    assert len(res["assets"]) == 4
    assert len(res["top_pairs"]) > 0


def test_capm_beta(returns_data):
    res = RollingCorrelationEngine.compute_beta(returns_data["NVDA"], returns_data["SPY"])
    assert "beta" in res
    assert res["beta"] > 1.2


def test_contagion_graph(returns_data):
    meta = {
        "SPY": {"name": "S&P 500 ETF", "sector": "Index ETF"},
        "AAPL": {"name": "Apple Inc.", "sector": "Information Technology"},
        "MSFT": {"name": "Microsoft Corp.", "sector": "Information Technology"},
        "NVDA": {"name": "NVIDIA Corp.", "sector": "Information Technology"}
    }
    builder = MarketRelationshipGraph(threshold=0.40)
    res = builder.build_graph(returns_data, meta)

    assert "nodes" in res
    assert "edges" in res
    assert len(res["nodes"]) == 4
