"""
Validation Helper Functions for Inputs, Tickers, and Ranges.
"""
import re
from typing import Tuple
from app.core.exceptions import ValidationException
from app.utils.constants import VALID_TIMEFRAMES, VALID_INTERVALS, SUPPORTED_UNIVERSE


def validate_ticker(ticker: str) -> str:
    """Validates and standardizes stock ticker string."""
    if not ticker or not isinstance(ticker, str):
        raise ValidationException("Stock ticker symbol cannot be empty.")
    clean = ticker.strip().upper()
    if not re.match(r"^[A-Z0-9\.\-\^:\s]{1,25}$", clean):
        raise ValidationException(f"Invalid ticker format: '{clean}'")
    # Bare symbol without market delimiters (. : ^ space) must not exceed 10 characters
    if not any(c in clean for c in [".", ":", "^", " "]) and len(clean) > 10:
        raise ValidationException(f"Invalid ticker format: '{clean}' (bare symbol exceeds 10 characters)")
    return clean


def validate_timeframe(timeframe: str) -> str:
    """Validates historical timeframe range string."""
    clean = timeframe.strip().lower()
    if clean not in VALID_TIMEFRAMES:
        raise ValidationException(
            f"Invalid timeframe '{clean}'. Supported timeframes: {', '.join(VALID_TIMEFRAMES)}"
        )
    return clean


def validate_interval(interval: str) -> str:
    """Validates historical bar interval."""
    clean = interval.strip().lower()
    if clean not in VALID_INTERVALS:
        raise ValidationException(
            f"Invalid interval '{clean}'. Supported intervals: {', '.join(VALID_INTERVALS)}"
        )
    return clean


def validate_monte_carlo_params(days: int, iterations: int) -> Tuple[int, int]:
    """Validates and bounds Monte Carlo days and iterations."""
    clamped_days = max(5, min(365, days))
    clamped_iterations = max(100, min(20000, iterations))
    return clamped_days, clamped_iterations


def validate_simulation_parameters(days: int, iterations: int, drift: float, volatility: float):
    """Validates Monte Carlo stochastic parameters."""
    if not (5 <= days <= 365):
        raise ValidationException("Simulation horizon (days) must be between 5 and 365.")
    if not (100 <= iterations <= 20000):
        raise ValidationException("Iterations must be between 100 and 20,000.")
    if not (-1.0 <= drift <= 2.0):
        raise ValidationException("Annualized drift (mu) must be between -100% and +200%.")
    if not (0.01 <= volatility <= 3.0):
        raise ValidationException("Annualized volatility (sigma) must be between 1% and 300%.")
