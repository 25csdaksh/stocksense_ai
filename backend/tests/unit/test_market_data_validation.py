"""
Unit Tests for Financial Market Data Validation.
Phase 6.1: Verifies OHLC bound enforcement, price positivity, non-negative volume, and invalid record filtering.
"""
import pytest
from app.providers.market_data.validator import validator, MarketDataValidator
from app.providers.market_data.models import NormalizedQuote, HistoricalCandle


def test_valid_quote_validation():
    valid_quote = {
        "price": 2500.0,
        "open": 2490.0,
        "high": 2520.0,
        "low": 2480.0,
        "previous_close": 2485.0,
        "volume": 1500000.0
    }
    is_valid, error = validator.validate_quote(valid_quote)
    assert is_valid is True
    assert error is None


def test_quote_rejection_on_negative_or_zero_price():
    # Negative price
    is_valid, error = validator.validate_quote({"price": -10.0})
    assert is_valid is False
    assert "strictly positive" in error

    # Zero price
    is_valid, error = validator.validate_quote({"price": 0.0})
    assert is_valid is False

    # Negative volume
    is_valid, error = validator.validate_quote({"price": 100.0, "volume": -500})
    assert is_valid is False
    assert "volume" in error


def test_candle_ohlc_boundary_enforcement():
    # Valid candle: High >= max(Open, Close) and Low <= min(Open, Close)
    valid_bar = {
        "open": 100.0,
        "high": 110.0,
        "low": 95.0,
        "close": 105.0,
        "volume": 1000.0
    }
    is_valid, error = validator.validate_candle(valid_bar)
    assert is_valid is True
    assert error is None

    # Invalid: High is lower than Open
    invalid_high = {
        "open": 100.0,
        "high": 98.0,
        "low": 90.0,
        "close": 95.0,
        "volume": 1000.0
    }
    is_valid, error = validator.validate_candle(invalid_high)
    assert is_valid is False
    assert "high" in error.lower()

    # Invalid: Low is higher than Close
    invalid_low = {
        "open": 100.0,
        "high": 105.0,
        "low": 98.0,
        "close": 92.0,
        "volume": 1000.0
    }
    is_valid, error = validator.validate_candle(invalid_low)
    assert is_valid is False
    assert "low" in error.lower()


def test_filter_and_validate_candles():
    mixed_candles = [
        {"time": "2026-09-01", "open": 100.0, "high": 105.0, "low": 95.0, "close": 102.0, "volume": 1000},
        {"time": "2026-09-02", "open": 102.0, "high": 90.0, "low": 80.0, "close": 85.0, "volume": 1000},  # Corrupt
        {"time": "2026-09-03", "open": 103.0, "high": 108.0, "low": 101.0, "close": 106.0, "volume": 1500},
    ]

    validated = validator.filter_and_validate_candles(mixed_candles, symbol="TEST")
    assert len(validated) == 2
    assert validated[0].time == "2026-09-01"
    assert validated[1].time == "2026-09-03"
