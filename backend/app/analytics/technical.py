"""
Technical Indicators & Quantitative Time-Series Calculations.
Pure mathematical implementations using Pandas and NumPy.
"""
from typing import Dict, Any, Optional
import numpy as np
import pandas as pd


def calculate_sma(series: pd.Series, window: int = 20) -> pd.Series:
    """Calculates Simple Moving Average (SMA)."""
    return series.rolling(window=window, min_periods=1).mean()


def calculate_ema(series: pd.Series, window: int = 20) -> pd.Series:
    """Calculates Exponential Moving Average (EMA)."""
    return series.ewm(span=window, adjust=False).mean()


def calculate_rsi(series: pd.Series, window: int = 14) -> pd.Series:
    """Calculates Relative Strength Index (RSI)."""
    delta = series.diff()
    gain = (delta.where(delta > 0, 0.0)).rolling(window=window, min_periods=1).mean()
    loss = (-delta.where(delta < 0, 0.0)).rolling(window=window, min_periods=1).mean()
    rs = gain / loss.replace(0, 1e-6)
    rsi = 100.0 - (100.0 / (1.0 + rs))
    return rsi.fillna(50.0)


def calculate_macd(
    series: pd.Series,
    fast: int = 12,
    slow: int = 26,
    signal: int = 9
) -> Dict[str, pd.Series]:
    """Calculates Moving Average Convergence Divergence (MACD)."""
    ema_fast = calculate_ema(series, fast)
    ema_slow = calculate_ema(series, slow)
    macd_line = ema_fast - ema_slow
    signal_line = macd_line.ewm(span=signal, adjust=False).mean()
    histogram = macd_line - signal_line
    return {
        "macd_line": macd_line,
        "signal_line": signal_line,
        "histogram": histogram
    }


def calculate_bollinger_bands(
    series: pd.Series,
    window: int = 20,
    num_std: float = 2.0
) -> Dict[str, pd.Series]:
    """Calculates Bollinger Bands (Upper, Middle, Lower)."""
    middle = series.rolling(window=window, min_periods=1).mean()
    std = series.rolling(window=window, min_periods=1).std().fillna(0)
    upper = middle + (std * num_std)
    lower = middle - (std * num_std)
    bandwidth = ((upper - lower) / middle.replace(0, 1e-6)) * 100.0
    return {
        "middle": middle,
        "upper": upper,
        "lower": lower,
        "bandwidth": bandwidth
    }


def calculate_atr(
    high: pd.Series,
    low: pd.Series,
    close: pd.Series,
    window: int = 14
) -> pd.Series:
    """Calculates Average True Range (ATR)."""
    prev_close = close.shift(1)
    tr1 = high - low
    tr2 = (high - prev_close).abs()
    tr3 = (low - prev_close).abs()
    true_range = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
    return true_range.rolling(window=window, min_periods=1).mean()


def calculate_vwap(
    high: pd.Series,
    low: pd.Series,
    close: pd.Series,
    volume: pd.Series
) -> pd.Series:
    """Calculates Volume Weighted Average Price (VWAP)."""
    typical_price = (high + low + close) / 3.0
    cum_vol_price = (typical_price * volume).cumsum()
    cum_vol = volume.cumsum().replace(0, 1)
    return cum_vol_price / cum_vol


def calculate_realized_volatility(close: pd.Series, window: int = 20) -> pd.Series:
    """Calculates Annualized Realized Volatility (in %)."""
    log_returns = np.log(close / close.shift(1)).fillna(0)
    rolling_std = log_returns.rolling(window=window, min_periods=2).std().fillna(0)
    return rolling_std * np.sqrt(252) * 100.0


def compute_all_technical_indicators(df: pd.DataFrame) -> pd.DataFrame:
    """
    Takes an OHLCV dataframe and attaches standard technical indicators.
    Expected columns: ['open', 'high', 'low', 'close', 'volume']
    """
    out = df.copy()
    c = out["close"].astype(float)
    h = out["high"].astype(float)
    l = out["low"].astype(float)
    v = out["volume"].astype(float)

    out["sma_20"] = calculate_sma(c, 20).round(2)
    out["sma_50"] = calculate_sma(c, 50).round(2)
    out["ema_20"] = calculate_ema(c, 20).round(2)
    out["rsi_14"] = calculate_rsi(c, 14).round(2)
    
    macd_res = calculate_macd(c)
    out["macd_line"] = macd_res["macd_line"].round(2)
    out["macd_signal"] = macd_res["signal_line"].round(2)
    out["macd_hist"] = macd_res["histogram"].round(2)

    bb_res = calculate_bollinger_bands(c)
    out["bb_upper"] = bb_res["upper"].round(2)
    out["bb_middle"] = bb_res["middle"].round(2)
    out["bb_lower"] = bb_res["lower"].round(2)

    out["atr_14"] = calculate_atr(h, l, c, 14).round(2)
    out["vwap"] = calculate_vwap(h, l, c, v).round(2)
    out["realized_vol_20d"] = calculate_realized_volatility(c, 20).round(2)

    return out
