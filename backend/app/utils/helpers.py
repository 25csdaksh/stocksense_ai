"""
General Mathematical, Time-Series & Formatting Helper Functions.
"""
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
import numpy as np


def format_currency(val: Optional[float], decimals: int = 2) -> str:
    """Formats numeric float to USD currency representation."""
    if val is None:
        return "$0.00"
    return f"${val:,.{decimals}f}"


def format_percentage(val: Optional[float], decimals: int = 2) -> str:
    """Formats ratio to percentage representation."""
    if val is None:
        return "0.00%"
    return f"{val:+.{decimals}f}%" if val != 0 else f"{val:.{decimals}f}%"


def generate_business_dates(end_date: datetime, count: int) -> List[str]:
    """Generates a list of past N Monday-Friday business dates."""
    dates = []
    curr = end_date
    while len(dates) < count:
        if curr.weekday() < 5:  # Monday to Friday
            dates.append(curr.strftime("%Y-%m-%d"))
        curr -= timedelta(days=1)
    dates.reverse()
    return dates


def clean_nan(val: Any, default: Any = 0.0) -> Any:
    """Replaces NaNs or Infs with default value."""
    if val is None:
        return default
    if isinstance(val, (float, int)):
        if np.isnan(val) or np.isinf(val):
            return default
    return val
