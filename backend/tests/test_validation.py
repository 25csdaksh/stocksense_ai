"""
Request Validation & Parameter Sanitation Unit Tests.
"""
import pytest
from app.utils.validators import (
    validate_ticker,
    validate_timeframe,
    validate_interval,
    validate_monte_carlo_params
)
from app.core.exceptions import ValidationException


def test_validate_ticker_success():
    assert validate_ticker("aapl") == "AAPL"
    assert validate_ticker("NVDA") == "NVDA"
    assert validate_ticker("  msft  ") == "MSFT"


def test_validate_ticker_failure():
    with pytest.raises(ValidationException):
        validate_ticker("")

    with pytest.raises(ValidationException):
        validate_ticker("INVALID$$$")

    with pytest.raises(ValidationException):
        validate_ticker("TOOLONGTICKERNAME")


def test_validate_timeframe():
    assert validate_timeframe("1m") == "1m"
    assert validate_timeframe("6m") == "6m"
    assert validate_timeframe("5y") == "5y"

    with pytest.raises(ValidationException):
        validate_timeframe("10y")


def test_validate_interval():
    assert validate_interval("1d") == "1d"
    assert validate_interval("1wk") == "1wk"

    with pytest.raises(ValidationException):
        validate_interval("1s")


def test_validate_monte_carlo_params():
    days, iters = validate_monte_carlo_params(90, 5000)
    assert days == 90
    assert iters == 5000

    days_clamped, iters_clamped = validate_monte_carlo_params(2, 50000)
    assert days_clamped == 5
    assert iters_clamped == 20000
