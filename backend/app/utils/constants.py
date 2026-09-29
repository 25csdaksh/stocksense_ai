"""
MarketMind AI — Global Constants, Supported Universe & Regulatory Disclaimers.
"""

FINANCIAL_DISCLAIMER_TEXT = (
    "MarketMind AI is an academic and quantitative scenario analysis platform "
    "designed strictly for educational and analytical research purposes. It does not "
    "constitute financial advice, investment advisory, or an endorsement to buy or sell securities. "
    "All scenario simulations, Value-at-Risk (VaR) projections, and multi-factor scores are "
    "probabilistic statistical models subject to parameter uncertainty. Past statistical performance "
    "is not indicative of future market outcomes."
)

FINANCIAL_DISCLAIMER = FINANCIAL_DISCLAIMER_TEXT

SUPPORTED_UNIVERSE = {
    "AAPL": {
        "name": "Apple Inc.",
        "sector": "Information Technology",
        "industry": "Consumer Electronics",
        "base_price": 227.50,
        "beta": 1.12,
        "pe": 33.8,
        "pb": 48.5,
        "dividend_yield": 0.005,
        "market_cap": 3.48e12
    },
    "MSFT": {
        "name": "Microsoft Corporation",
        "sector": "Information Technology",
        "industry": "Software - Infrastructure",
        "base_price": 432.20,
        "beta": 0.95,
        "pe": 36.2,
        "pb": 12.4,
        "dividend_yield": 0.007,
        "market_cap": 3.22e12
    },
    "NVDA": {
        "name": "NVIDIA Corporation",
        "sector": "Information Technology",
        "industry": "Semiconductors",
        "base_price": 124.80,
        "beta": 1.68,
        "pe": 54.1,
        "pb": 39.2,
        "dividend_yield": 0.001,
        "market_cap": 3.15e12
    },
    "GOOGL": {
        "name": "Alphabet Inc.",
        "sector": "Communication Services",
        "industry": "Internet Content & Information",
        "base_price": 166.40,
        "beta": 1.05,
        "pe": 24.5,
        "pb": 6.9,
        "dividend_yield": 0.005,
        "market_cap": 2.18e12
    },
    "AMZN": {
        "name": "Amazon.com Inc.",
        "sector": "Consumer Discretionary",
        "industry": "Internet Retail",
        "base_price": 188.90,
        "beta": 1.25,
        "pe": 42.8,
        "pb": 8.6,
        "dividend_yield": 0.0,
        "market_cap": 2.01e12
    },
    "TSLA": {
        "name": "Tesla Inc.",
        "sector": "Consumer Discretionary",
        "industry": "Auto Manufacturers",
        "base_price": 252.30,
        "beta": 2.15,
        "pe": 69.4,
        "pb": 11.5,
        "dividend_yield": 0.0,
        "market_cap": 7.95e11
    },
    "JPM": {
        "name": "JPMorgan Chase & Co.",
        "sector": "Financials",
        "industry": "Banks - Diversified",
        "base_price": 221.10,
        "beta": 1.08,
        "pe": 12.3,
        "pb": 1.75,
        "dividend_yield": 0.022,
        "market_cap": 6.35e11
    },
    "SPY": {
        "name": "SPDR S&P 500 ETF Trust",
        "sector": "Index ETF",
        "industry": "Large Cap Blend",
        "base_price": 574.80,
        "beta": 1.00,
        "pe": 28.1,
        "pb": 5.0,
        "dividend_yield": 0.013,
        "market_cap": 5.5e11
    },
    "QQQ": {
        "name": "Invesco QQQ Trust",
        "sector": "Index ETF",
        "industry": "Large Cap Growth",
        "base_price": 489.30,
        "beta": 1.18,
        "pe": 31.6,
        "pb": 7.3,
        "dividend_yield": 0.006,
        "market_cap": 2.9e11
    }
}

DEFAULT_INDICES = [
    {"symbol": "^GSPC", "name": "S&P 500", "price": 5748.20, "change": +26.40, "change_pct": +0.46},
    {"symbol": "^IXIC", "name": "NASDAQ Composite", "price": 18145.80, "change": +154.20, "change_pct": +0.86},
    {"symbol": "^TNX", "name": "10Y Treasury Yield", "price": 4.18, "change": -0.04, "change_pct": -0.95},
    {"symbol": "^VIX", "name": "CBOE Volatility Index", "price": 14.85, "change": -0.62, "change_pct": -4.01},
]

VALID_TIMEFRAMES = ["1m", "3m", "6m", "1y", "2y", "5y"]
VALID_INTERVALS = ["1d", "1wk", "1mo"]
