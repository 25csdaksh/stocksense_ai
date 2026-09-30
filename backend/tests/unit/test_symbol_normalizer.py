"""
Unit Tests for Centralized Symbol Normalizer and Market Routing.
Phase 6.1: Validates normalization of Indian NSE/BSE stocks, benchmark indices, and US tickers.
"""
import pytest
from app.providers.market_data.symbol_normalizer import (
    normalize_symbol,
    is_indian_symbol,
    is_us_symbol,
    NormalizedSymbolInfo
)
from app.providers.market_data.exceptions import InvalidSymbol


def test_indian_equity_normalization():
    # Bare symbol in universe
    norm1 = normalize_symbol("RELIANCE")
    assert norm1.canonical_symbol == "RELIANCE.NS"
    assert norm1.market == "IN"
    assert norm1.exchange == "NSE"
    assert norm1.currency == "INR"

    # With .NS suffix
    norm2 = normalize_symbol("TCS.NS")
    assert norm2.canonical_symbol == "TCS.NS"
    assert norm2.market == "IN"
    assert norm2.exchange == "NSE"

    # With NSE prefix
    norm3 = normalize_symbol("NSE:INFY")
    assert norm3.canonical_symbol == "INFY.NS"
    assert norm3.market == "IN"
    assert norm3.exchange == "NSE"

    # Long ticker like TATAMOTORS.NS
    norm4 = normalize_symbol("TATAMOTORS.NS")
    assert norm4.canonical_symbol == "TATAMOTORS.NS"
    assert norm4.market == "IN"

    # BSE Suffix
    norm5 = normalize_symbol("INFY.BO")
    assert norm5.canonical_symbol == "INFY.BO"
    assert norm5.market == "IN"
    assert norm5.exchange == "BSE"


def test_indian_index_normalization():
    # NIFTY 50 variants
    for variant in ["NIFTY 50", "NIFTY", "NIFTY50", "^NSEI", "NSE:NIFTY"]:
        norm = normalize_symbol(variant)
        assert norm.canonical_symbol == "^NSEI"
        assert norm.display_symbol == "NIFTY 50"
        assert norm.market == "IN"
        assert norm.is_index is True
        assert norm.currency == "INR"

    # SENSEX variants
    for variant in ["SENSEX", "^BSESN", "BSE:SENSEX"]:
        norm = normalize_symbol(variant)
        assert norm.canonical_symbol == "^BSESN"
        assert norm.display_symbol == "SENSEX"
        assert norm.market == "IN"
        assert norm.is_index is True
        assert norm.exchange == "BSE"

    # NIFTY BANK
    norm_bank = normalize_symbol("NIFTY BANK")
    assert norm_bank.canonical_symbol == "^NSEBANK"
    assert norm_bank.market == "IN"

    # NIFTY IT
    norm_it = normalize_symbol("NIFTY IT")
    assert norm_it.canonical_symbol == "^CNXIT"
    assert norm_it.market == "IN"


def test_us_equity_and_index_normalization():
    norm_aapl = normalize_symbol("AAPL")
    assert norm_aapl.canonical_symbol == "AAPL"
    assert norm_aapl.market == "US"
    assert norm_aapl.currency == "USD"
    assert norm_aapl.is_index is False

    norm_sp500 = normalize_symbol("S&P 500")
    assert norm_sp500.canonical_symbol == "^GSPC"
    assert norm_sp500.market == "US"
    assert norm_sp500.is_index is True

    norm_vix = normalize_symbol("VIX")
    assert norm_vix.canonical_symbol == "^VIX"
    assert norm_vix.market == "US"


def test_market_helper_functions():
    assert is_indian_symbol("RELIANCE.NS") is True
    assert is_indian_symbol("NIFTY 50") is True
    assert is_indian_symbol("AAPL") is False

    assert is_us_symbol("AAPL") is True
    assert is_us_symbol("S&P 500") is True
    assert is_us_symbol("TCS.NS") is False


def test_invalid_symbol_error():
    with pytest.raises(InvalidSymbol):
        normalize_symbol("")

    with pytest.raises(InvalidSymbol):
        normalize_symbol("   ")

    with pytest.raises(InvalidSymbol):
        normalize_symbol("INVALID$$$SYMBOL!@#")
