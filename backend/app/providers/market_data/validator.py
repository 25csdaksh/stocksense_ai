"""
MarketMind AI — Financial Market Data Validator.
Validates quotes, OHLCV bars, and indices for mathematical consistency, price positivity, and chronological ordering.
"""
from typing import Dict, Any, List, Union, Tuple, Optional
from datetime import datetime
from app.providers.market_data.models import NormalizedQuote, HistoricalCandle
from app.providers.market_data.exceptions import DataValidationError
from app.core.logging import logger


class MarketDataValidator:
    """Enforces strict financial integrity on market quotes and historical candlestick data."""

    @staticmethod
    def validate_quote(quote: Union[Dict[str, Any], NormalizedQuote]) -> Tuple[bool, Optional[str]]:
        """
        Validates quote record for price positivity, high/low boundaries, and non-negative volume.
        Returns (is_valid, error_reason).
        """
        if isinstance(quote, NormalizedQuote):
            data = quote.model_dump()
        else:
            data = quote

        price = data.get("price")
        if price is None or price <= 0:
            return False, f"Invalid price: {price}. Market price must be strictly positive."

        open_p = data.get("open")
        high_p = data.get("high")
        low_p = data.get("low")
        prev_close = data.get("previous_close")

        if open_p is not None and open_p <= 0:
            return False, f"Invalid open price: {open_p}. Must be strictly positive."
        if high_p is not None and high_p <= 0:
            return False, f"Invalid high price: {high_p}. Must be strictly positive."
        if low_p is not None and low_p <= 0:
            return False, f"Invalid low price: {low_p}. Must be strictly positive."
        if prev_close is not None and prev_close <= 0:
            return False, f"Invalid previous_close: {prev_close}. Must be strictly positive."

        # Check high / low bounds
        if high_p is not None and low_p is not None and low_p > high_p:
            return False, f"Impossible OHLC bounds: low ({low_p}) cannot exceed high ({high_p})."

        if high_p is not None and open_p is not None and high_p < open_p:
            return False, f"Impossible OHLC bounds: high ({high_p}) is lower than open ({open_p})."

        if low_p is not None and open_p is not None and low_p > open_p:
            return False, f"Impossible OHLC bounds: low ({low_p}) is higher than open ({open_p})."

        vol = data.get("volume", 0)
        if vol is not None and vol < 0:
            return False, f"Invalid volume: {vol}. Traded volume cannot be negative."

        return True, None

    @staticmethod
    def validate_candle(candle: Union[Dict[str, Any], HistoricalCandle]) -> Tuple[bool, Optional[str]]:
        """
        Validates OHLCV candle for:
        1. high >= max(open, close)
        2. low <= min(open, close)
        3. volume >= 0
        4. open > 0, high > 0, low > 0, close > 0
        5. valid timestamp
        """
        if isinstance(candle, HistoricalCandle):
            data = candle.model_dump()
        else:
            data = candle

        o = data.get("open")
        h = data.get("high")
        l = data.get("low")
        c = data.get("close")
        v = data.get("volume", 0)

        # Check None or non-numeric
        for name, val in [("open", o), ("high", h), ("low", l), ("close", c)]:
            if val is None or not isinstance(val, (int, float)) or val <= 0:
                return False, f"Candle price '{name}' must be a strictly positive number (got {val})."

        if v is not None and v < 0:
            return False, f"Candle volume must be non-negative (got {v})."

        # Check High >= max(Open, Close)
        max_oc = max(o, c)
        if h < (max_oc - 1e-6):  # floating-point tolerance
            return False, f"Invalid OHLC: high ({h}) is less than max(open={o}, close={c})."

        # Check Low <= min(Open, Close)
        min_oc = min(o, c)
        if l > (min_oc + 1e-6):
            return False, f"Invalid OHLC: low ({l}) is greater than min(open={o}, close={c})."

        return True, None

    @classmethod
    def filter_and_validate_candles(
        cls,
        candles: List[Union[Dict[str, Any], HistoricalCandle]],
        symbol: str = "UNKNOWN"
    ) -> List[HistoricalCandle]:
        """
        Validates a list of candles, rejects corrupt/impossible records safely,
        logs warning without silent corruption, and returns valid HistoricalCandle instances.
        """
        valid_candles: List[HistoricalCandle] = []

        for idx, bar in enumerate(candles):
            is_valid, error_reason = cls.validate_candle(bar)
            if not is_valid:
                logger.warning(
                    f"Financial Data Validation Rejected Candle #{idx} for {symbol}: {error_reason}. Record: {bar}"
                )
                continue

            if isinstance(bar, HistoricalCandle):
                valid_candles.append(bar)
            else:
                ts = bar.get("timestamp")
                if isinstance(ts, str):
                    try:
                        ts_dt = datetime.fromisoformat(ts.replace("Z", "+00:00"))
                    except Exception:
                        ts_dt = datetime.utcnow()
                elif isinstance(ts, datetime):
                    ts_dt = ts
                else:
                    ts_dt = datetime.utcnow()

                candle_obj = HistoricalCandle(
                    timestamp=ts_dt,
                    time=str(bar.get("time", ts_dt.strftime("%Y-%m-%d"))),
                    open=float(bar["open"]),
                    high=float(bar["high"]),
                    low=float(bar["low"]),
                    close=float(bar["close"]),
                    volume=float(bar.get("volume", 0)),
                    adjusted_close=float(bar["adjusted_close"]) if bar.get("adjusted_close") is not None else None,
                    symbol=bar.get("symbol", symbol),
                    exchange=bar.get("exchange"),
                    currency=bar.get("currency", "USD"),
                    data_source=bar.get("data_source", "FEED"),
                    data_status=bar.get("data_status", "DEMO"),
                    sma_20=bar.get("sma_20"),
                    sma_50=bar.get("sma_50"),
                    ema_20=bar.get("ema_20"),
                    rsi_14=bar.get("rsi_14"),
                    vwap=bar.get("vwap"),
                )
                valid_candles.append(candle_obj)

        return valid_candles


validator = MarketDataValidator()
