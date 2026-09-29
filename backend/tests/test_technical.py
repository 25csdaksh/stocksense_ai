"""
Technical Indicator Unit Tests.
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
def sample_ohlcv_df():
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


def test_sma_calculation(sample_ohlcv_df):
    sma20 = calculate_sma(sample_ohlcv_df["close"], window=20)
    assert len(sma20) == len(sample_ohlcv_df)
    assert not sma20.isna().any()
    assert np.isclose(sma20.iloc[19], sample_ohlcv_df["close"].iloc[:20].mean())


def test_ema_calculation(sample_ohlcv_df):
    ema20 = calculate_ema(sample_ohlcv_df["close"], window=20)
    assert len(ema20) == len(sample_ohlcv_df)
    assert not ema20.isna().any()


def test_rsi_bounds(sample_ohlcv_df):
    rsi = calculate_rsi(sample_ohlcv_df["close"], window=14)
    assert len(rsi) == len(sample_ohlcv_df)
    assert (rsi >= 0.0).all() and (rsi <= 100.0).all()


def test_macd_structure(sample_ohlcv_df):
    res = calculate_macd(sample_ohlcv_df["close"])
    assert "macd_line" in res
    assert "signal_line" in res
    assert "histogram" in res
    assert len(res["macd_line"]) == len(sample_ohlcv_df)


def test_bollinger_bands_ordering(sample_ohlcv_df):
    res = calculate_bollinger_bands(sample_ohlcv_df["close"], window=20)
    upper = res["upper"]
    middle = res["middle"]
    lower = res["lower"]
    assert (upper >= middle).all()
    assert (middle >= lower).all()


def test_compute_all_indicators(sample_ohlcv_df):
    df_ind = compute_all_technical_indicators(sample_ohlcv_df)
    expected_cols = [
        "sma_20", "sma_50", "ema_20", "rsi_14",
        "macd_line", "macd_signal", "macd_hist",
        "bb_upper", "bb_middle", "bb_lower",
        "atr_14", "vwap", "realized_vol_20d"
    ]
    for col in expected_cols:
        assert col in df_ind.columns
