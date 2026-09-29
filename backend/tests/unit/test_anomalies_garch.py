"""
Unit Tests: Isolation Forest Anomaly Detection, GARCH Volatility & Volume Spikes.
"""
import pytest
import numpy as np
import pandas as pd
from app.analytics.anomaly import MarketAnomalyDetector, GARCHVolatilityModel, VolumeSpikeDetector


@pytest.fixture
def anomaly_series():
    np.random.seed(42)
    n = 60
    closes = 100.0 + np.cumsum(np.random.normal(0.05, 1.5, n))
    highs = closes + np.random.uniform(0.5, 2.0, n)
    lows = closes - np.random.uniform(0.5, 2.0, n)
    volumes = np.random.uniform(1000000, 3000000, n)

    # Inject anomaly at index 45
    closes[45] += 15.0
    highs[45] += 16.0
    volumes[45] *= 8.0

    return pd.DataFrame({
        "time": [f"2024-02-{i+1:02d}" for i in range(n)],
        "open": closes - 0.2,
        "high": highs,
        "low": lows,
        "close": closes,
        "volume": volumes
    })


def test_isolation_forest_anomaly_detector(anomaly_series):
    detector = MarketAnomalyDetector(contamination=0.08)
    anomalies = detector.detect_anomalies(anomaly_series, ticker="NVDA")

    assert isinstance(anomalies, list)
    assert len(anomalies) > 0
    first = anomalies[0]
    assert first["ticker"] == "NVDA"
    assert "severity_score" in first
    assert "anomaly_type" in first


def test_garch_volatility_forecasting(anomaly_series):
    returns = anomaly_series["close"].pct_change().dropna().values
    garch = GARCHVolatilityModel()
    res = garch.forecast(returns, horizon=5)

    assert "current_annualized_volatility_pct" in res
    assert len(res["forecast_next_days"]) == 5
    assert res["current_annualized_volatility_pct"] > 0


def test_volume_spike_detector(anomaly_series):
    spike_det = VolumeSpikeDetector(window=20, z_threshold=2.0)
    res = spike_det.analyze(anomaly_series, ticker="NVDA")

    assert res["ticker"] == "NVDA"
    assert "volume_zscore" in res
    assert "is_spike" in res
