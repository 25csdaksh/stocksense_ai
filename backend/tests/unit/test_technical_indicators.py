"""
Unit Tests: Technical Indicators & Quantitative Time-Series Formulas.
"""
import pytest
import numpy as np
import pandas as pd
from app.analytics.technical import (
    calculate_sma,
    calculate_ema,
    calculate_rsi,
    calculate_macd,
    calculate_bollinger_bands,
    calculate_atr,
    calculate_vwap,
    calculate_realized_volatility,
    compute_all_technical_indicators
)


@pytest.fixture
def sample_ohlcv():
    np.random.seed(42)
    n = 100
    prices = 150.0 + np.cumsum(np.random.normal(0.2, 2.0, n))
    highs = prices + np.random.uniform(0.5, 3.0, n)
    lows = prices - np.random.uniform(0.5, 3.0, n)
    opens = prices + np.random.uniform(-1.0, 1.0, n)
    volumes = np.random.uniform(1000000, 5000000, n)

    return pd.DataFrame({
        "time": [f"2024-01-{i+1:02d}" for i in range(n)],
        "open": opens,
        "high": highs,
        "low": lows,
        "close": prices,
        "volume": volumes
    })


def test_sma_calculation(sample_ohlcv):
    sma20 = calculate_sma(sample_ohlcv["close"], window=20)
    assert len(sma20) == len(sample_ohlcv)
    assert not sma20.isna().any()
    assert np.isclose(sma20.iloc[19], sample_ohlcv["close"].iloc[:20].mean())


def test_ema_calculation(sample_ohlcv):
    ema20 = calculate_ema(sample_ohlcv["close"], window=20)
    assert len(ema20) == len(sample_ohlcv)
    assert not ema20.isna().any()


def test_rsi_bounds(sample_ohlcv):
    rsi = calculate_rsi(sample_ohlcv["close"], window=14)
    assert len(rsi) == len(sample_ohlcv)
    assert (rsi >= 0.0).all() and (rsi <= 100.0).all()


def test_macd_structure(sample_ohlcv):
    res = calculate_macd(sample_ohlcv["close"])
    assert "macd_line" in res
    assert "signal_line" in res
    assert "histogram" in res
    assert len(res["macd_line"]) == len(sample_ohlcv)


def test_bollinger_bands_ordering(sample_ohlcv):
    res = calculate_bollinger_bands(sample_ohlcv["close"], window=20)
    assert (res["upper"] >= res["middle"]).all()
    assert (res["middle"] >= res["lower"]).all()


def test_compute_all_indicators(sample_ohlcv):
    df_ind = compute_all_technical_indicators(sample_ohlcv)
    for col in ["sma_20", "sma_50", "ema_20", "rsi_14", "macd_line", "bb_upper", "atr_14", "vwap", "realized_vol_20d"]:
        assert col in df_ind.columns
