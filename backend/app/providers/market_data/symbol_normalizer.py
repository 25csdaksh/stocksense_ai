"""
MarketMind AI — Centralized Symbol Normalization & Ticker Routing Module.
Normalizes Indian (NSE/BSE) and US equities/indices consistently across all services.
"""
import re
from dataclasses import dataclass
from typing import Optional, Dict, Any
from app.providers.market_data.exceptions import InvalidSymbol


@dataclass
class NormalizedSymbolInfo:
    """Standardized metadata for a normalized financial symbol."""
    raw_symbol: str
    canonical_symbol: str
    display_symbol: str
    name: Optional[str]
    exchange: str
    market: str  # "IN", "US", "GLOBAL"
    is_index: bool
    currency: str


# Mapping of recognized Indian benchmarks & aliases
INDIAN_INDICES_MAP: Dict[str, Dict[str, Any]] = {
    "^NSEI": {"canonical": "^NSEI", "display": "NIFTY 50", "name": "NIFTY 50 Benchmark Index", "exchange": "NSE", "currency": "INR"},
    "NIFTY 50": {"canonical": "^NSEI", "display": "NIFTY 50", "name": "NIFTY 50 Benchmark Index", "exchange": "NSE", "currency": "INR"},
    "NIFTY": {"canonical": "^NSEI", "display": "NIFTY 50", "name": "NIFTY 50 Benchmark Index", "exchange": "NSE", "currency": "INR"},
    "NIFTY50": {"canonical": "^NSEI", "display": "NIFTY 50", "name": "NIFTY 50 Benchmark Index", "exchange": "NSE", "currency": "INR"},
    "^NSEBANK": {"canonical": "^NSEBANK", "display": "NIFTY BANK", "name": "NIFTY Bank Sectoral Index", "exchange": "NSE", "currency": "INR"},
    "NIFTY BANK": {"canonical": "^NSEBANK", "display": "NIFTY BANK", "name": "NIFTY Bank Sectoral Index", "exchange": "NSE", "currency": "INR"},
    "BANKNIFTY": {"canonical": "^NSEBANK", "display": "NIFTY BANK", "name": "NIFTY Bank Sectoral Index", "exchange": "NSE", "currency": "INR"},
    "^CNXIT": {"canonical": "^CNXIT", "display": "NIFTY IT", "name": "NIFTY Information Technology Index", "exchange": "NSE", "currency": "INR"},
    "NIFTY IT": {"canonical": "^CNXIT", "display": "NIFTY IT", "name": "NIFTY Information Technology Index", "exchange": "NSE", "currency": "INR"},
    "CNXIT": {"canonical": "^CNXIT", "display": "NIFTY IT", "name": "NIFTY Information Technology Index", "exchange": "NSE", "currency": "INR"},
    "^BSESN": {"canonical": "^BSESN", "display": "SENSEX", "name": "BSE SENSEX 30 Benchmark", "exchange": "BSE", "currency": "INR"},
    "SENSEX": {"canonical": "^BSESN", "display": "SENSEX", "name": "BSE SENSEX 30 Benchmark", "exchange": "BSE", "currency": "INR"},
    "BSE SENSEX": {"canonical": "^BSESN", "display": "SENSEX", "name": "BSE SENSEX 30 Benchmark", "exchange": "BSE", "currency": "INR"},
}

# Known Indian Equities dictionary for smart lookup
INDIAN_EQUITY_SYMBOLS = {
    "RELIANCE": "Reliance Industries Limited",
    "TCS": "Tata Consultancy Services Limited",
    "INFY": "Infosys Limited",
    "HDFCBANK": "HDFC Bank Limited",
    "ICICIBANK": "ICICI Bank Limited",
    "TATAMOTORS": "Tata Motors Limited",
    "ITC": "ITC Limited",
    "SBIN": "State Bank of India",
    "LT": "Larsen & Toubro Limited",
    "BHARTIARTL": "Bharti Airtel Limited",
    "KOTAKBANK": "Kotak Mahindra Bank Limited",
    "HINDUNILVR": "Hindustan Unilever Limited",
    "WIPRO": "Wipro Limited",
    "AXISBANK": "Axis Bank Limited",
    "MARUTI": "Maruti Suzuki India Limited",
    "BAJFINANCE": "Bajaj Finance Limited",
    "SUNPHARMA": "Sun Pharmaceutical Industries Limited",
    "ASIANPAINT": "Asian Paints Limited",
    "TITAN": "Titan Company Limited",
    "ADANIENT": "Adani Enterprises Limited",
}

# Mapping of recognized US benchmarks & ETFs
US_INDICES_MAP: Dict[str, Dict[str, Any]] = {
    "^GSPC": {"canonical": "^GSPC", "display": "S&P 500", "name": "S&P 500 Index", "exchange": "NYSE", "currency": "USD"},
    "S&P 500": {"canonical": "^GSPC", "display": "S&P 500", "name": "S&P 500 Index", "exchange": "NYSE", "currency": "USD"},
    "SP500": {"canonical": "^GSPC", "display": "S&P 500", "name": "S&P 500 Index", "exchange": "NYSE", "currency": "USD"},
    "^IXIC": {"canonical": "^IXIC", "display": "NASDAQ", "name": "NASDAQ Composite Index", "exchange": "NASDAQ", "currency": "USD"},
    "NASDAQ": {"canonical": "^IXIC", "display": "NASDAQ", "name": "NASDAQ Composite Index", "exchange": "NASDAQ", "currency": "USD"},
    "^TNX": {"canonical": "^TNX", "display": "10Y Treasury", "name": "10Y Treasury Yield Index", "exchange": "CBOE", "currency": "USD"},
    "^VIX": {"canonical": "^VIX", "display": "VIX", "name": "CBOE Volatility Index", "exchange": "CBOE", "currency": "USD"},
    "VIX": {"canonical": "^VIX", "display": "VIX", "name": "CBOE Volatility Index", "exchange": "CBOE", "currency": "USD"},
    "SPY": {"canonical": "SPY", "display": "SPY", "name": "SPDR S&P 500 ETF Trust", "exchange": "NYSE", "currency": "USD"},
    "QQQ": {"canonical": "QQQ", "display": "QQQ", "name": "Invesco QQQ Trust", "exchange": "NASDAQ", "currency": "USD"},
}


class SymbolNormalizer:
    """Centralized financial symbol normalizer and router."""

    @staticmethod
    def normalize(symbol: str) -> NormalizedSymbolInfo:
        """
        Normalizes a raw ticker string into a standardized NormalizedSymbolInfo object.
        Handles prefixes ('NSE:RELIANCE', 'BSE:INFY', 'NASDAQ:AAPL'),
        suffixes ('RELIANCE.NS', 'TCS.BO'), index identifiers ('^NSEI', 'NIFTY 50'), and bare tickers.
        """
        if not symbol or not isinstance(symbol, str):
            raise InvalidSymbol(str(symbol), reason="Symbol cannot be empty.")

        clean = symbol.strip().upper()

        # Check direct index match (case-insensitive)
        if clean in INDIAN_INDICES_MAP:
            meta = INDIAN_INDICES_MAP[clean]
            return NormalizedSymbolInfo(
                raw_symbol=symbol,
                canonical_symbol=meta["canonical"],
                display_symbol=meta["display"],
                name=meta["name"],
                exchange=meta["exchange"],
                market="IN",
                is_index=True,
                currency=meta["currency"]
            )

        if clean in US_INDICES_MAP:
            meta = US_INDICES_MAP[clean]
            return NormalizedSymbolInfo(
                raw_symbol=symbol,
                canonical_symbol=meta["canonical"],
                display_symbol=meta["display"],
                name=meta["name"],
                exchange=meta["exchange"],
                market="US",
                is_index=True,
                currency=meta["currency"]
            )

        # Handle prefix formats like "NSE:RELIANCE", "BSE:TCS", "NASDAQ:AAPL"
        exchange_prefix = None
        if ":" in clean:
            parts = clean.split(":", 1)
            exchange_prefix = parts[0].strip()
            clean = parts[1].strip()

        # Check index again after prefix stripping (e.g. "NSE:NIFTY", "BSE:SENSEX")
        if clean in INDIAN_INDICES_MAP:
            meta = INDIAN_INDICES_MAP[clean]
            return NormalizedSymbolInfo(
                raw_symbol=symbol,
                canonical_symbol=meta["canonical"],
                display_symbol=meta["display"],
                name=meta["name"],
                exchange=meta["exchange"],
                market="IN",
                is_index=True,
                currency=meta["currency"]
            )

        # Validate ticker characters
        if not re.match(r"^[A-Z0-9\.\-\^]{1,20}$", clean):
            raise InvalidSymbol(symbol, reason=f"Contains invalid characters or exceeds length: '{clean}'")

        # Indian NSE Suffix (.NS)
        if clean.endswith(".NS"):
            base = clean[:-3]
            name = INDIAN_EQUITY_SYMBOLS.get(base, f"{base} India Ltd")
            return NormalizedSymbolInfo(
                raw_symbol=symbol,
                canonical_symbol=clean,
                display_symbol=clean,
                name=name,
                exchange="NSE",
                market="IN",
                is_index=False,
                currency="INR"
            )

        # Indian BSE Suffix (.BO)
        if clean.endswith(".BO"):
            base = clean[:-3]
            name = INDIAN_EQUITY_SYMBOLS.get(base, f"{base} India Ltd")
            return NormalizedSymbolInfo(
                raw_symbol=symbol,
                canonical_symbol=clean,
                display_symbol=clean,
                name=name,
                exchange="BSE",
                market="IN",
                is_index=False,
                currency="INR"
            )

        # Exchange prefix specified as NSE
        if exchange_prefix == "NSE":
            canonical = f"{clean}.NS"
            name = INDIAN_EQUITY_SYMBOLS.get(clean, f"{clean} India Ltd")
            return NormalizedSymbolInfo(
                raw_symbol=symbol,
                canonical_symbol=canonical,
                display_symbol=canonical,
                name=name,
                exchange="NSE",
                market="IN",
                is_index=False,
                currency="INR"
            )

        # Exchange prefix specified as BSE
        if exchange_prefix == "BSE":
            canonical = f"{clean}.BO"
            name = INDIAN_EQUITY_SYMBOLS.get(clean, f"{clean} India Ltd")
            return NormalizedSymbolInfo(
                raw_symbol=symbol,
                canonical_symbol=canonical,
                display_symbol=canonical,
                name=name,
                exchange="BSE",
                market="IN",
                is_index=False,
                currency="INR"
            )

        # Check if bare symbol is in known Indian equities universe
        if clean in INDIAN_EQUITY_SYMBOLS:
            canonical = f"{clean}.NS"
            return NormalizedSymbolInfo(
                raw_symbol=symbol,
                canonical_symbol=canonical,
                display_symbol=canonical,
                name=INDIAN_EQUITY_SYMBOLS[clean],
                exchange="NSE",
                market="IN",
                is_index=False,
                currency="INR"
            )

        # Default US Market Equity (e.g. AAPL, MSFT, NVDA)
        exch = exchange_prefix if exchange_prefix in ["NASDAQ", "NYSE", "AMEX"] else "NASDAQ"
        return NormalizedSymbolInfo(
            raw_symbol=symbol,
            canonical_symbol=clean,
            display_symbol=clean,
            name=f"{clean} Corporation",
            exchange=exch,
            market="US",
            is_index=False,
            currency="USD"
        )


def normalize_symbol(symbol: str) -> NormalizedSymbolInfo:
    """Convenience functional wrapper for SymbolNormalizer.normalize."""
    return SymbolNormalizer.normalize(symbol)


def is_indian_symbol(symbol: str) -> bool:
    """Returns True if symbol belongs to Indian NSE/BSE markets or benchmark indices."""
    try:
        norm = normalize_symbol(symbol)
        return norm.market == "IN"
    except Exception:
        return False


def is_us_symbol(symbol: str) -> bool:
    """Returns True if symbol belongs to US equity/index markets."""
    try:
        norm = normalize_symbol(symbol)
        return norm.market == "US"
    except Exception:
        return False
