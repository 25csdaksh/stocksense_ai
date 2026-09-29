"""
Technical Analytics, Correlation Matrix, Relationship Graph & Stock DNA Service.
"""
from typing import Dict, Any, List
import pandas as pd
from app.providers.market_data.factory import get_market_data_provider
from app.analytics.technical import compute_all_technical_indicators
from app.analytics.correlation import RollingCorrelationEngine, MarketRelationshipGraph
from app.analytics.stock_dna import StockDNAProfiler
from app.utils.constants import SUPPORTED_UNIVERSE
from app.utils.validators import validate_ticker


class AnalyticsService:

    def __init__(self):
        self.market_provider = get_market_data_provider()
        self.dna_profiler = StockDNAProfiler()

    async def get_technical_analysis(self, ticker: str) -> Dict[str, Any]:
        sym = validate_ticker(ticker)
        hist = await self.market_provider.get_history(sym, timeframe="6m", interval="1d")
        bars = hist["bars"]
        if not bars:
            return {}

        df = pd.DataFrame(bars)
        df = compute_all_technical_indicators(df)
        latest = df.iloc[-1]

        # Determine technical bias heuristic
        c = latest["close"]
        s20 = latest["sma_20"]
        s50 = latest["sma_50"]
        rsi = latest["rsi_14"]
        
        if c > s20 > s50 and rsi > 50:
            bias = "BULLISH"
        elif c < s20 < s50 and rsi < 50:
            bias = "BEARISH"
        else:
            bias = "NEUTRAL"

        return {
            "ticker": sym,
            "sma_20": float(latest["sma_20"]),
            "sma_50": float(latest["sma_50"]),
            "ema_20": float(latest["ema_20"]),
            "rsi_14": float(latest["rsi_14"]),
            "macd": {
                "line": float(latest["macd_line"]),
                "signal": float(latest["macd_signal"]),
                "histogram": float(latest["macd_hist"])
            },
            "bollinger_bands": {
                "upper": float(latest["bb_upper"]),
                "middle": float(latest["bb_middle"]),
                "lower": float(latest["bb_lower"])
            },
            "atr_14": float(latest["atr_14"]),
            "realized_volatility_20d_pct": float(latest["realized_vol_20d"]),
            "technical_bias": bias
        }

    async def _build_returns_matrix(self) -> pd.DataFrame:
        tickers = list(SUPPORTED_UNIVERSE.keys())
        data = {}
        for t in tickers:
            hist = await self.market_provider.get_history(t, timeframe="6m")
            bars = hist["bars"]
            if bars:
                closes = pd.Series([b["close"] for b in bars])
                data[t] = closes.pct_change().dropna().values[-90:]
        return pd.DataFrame(data)

    async def get_correlation_matrix(self, method: str = "pearson") -> Dict[str, Any]:
        returns_df = await self._build_returns_matrix()
        return RollingCorrelationEngine.compute_matrix(returns_df, method=method)

    async def get_relationship_graph(self, threshold: float = 0.45) -> Dict[str, Any]:
        returns_df = await self._build_returns_matrix()
        metadata = {t: {"name": v["name"], "sector": v["sector"]} for t, v in SUPPORTED_UNIVERSE.items()}
        builder = MarketRelationshipGraph(threshold=threshold)
        return builder.build_graph(returns_df, metadata)

    async def get_stock_dna(self, ticker: str) -> Dict[str, Any]:
        sym = validate_ticker(ticker)
        quote = await self.market_provider.get_quote(sym)
        meta = SUPPORTED_UNIVERSE.get(sym, {"pe": 28.0, "pb": 6.0, "dividend_yield": 0.01, "beta": 1.10})

        return self.dna_profiler.calculate(
            ticker=sym,
            fundamentals={
                "pe_ratio": meta.get("pe", 28.0),
                "pb_ratio": meta.get("pb", 6.0),
                "dividend_yield": meta.get("dividend_yield", 0.01),
                "roe": 0.30,
                "roa": 0.12,
                "debt_to_equity": 0.65,
                "revenue_growth_yoy": 0.16,
                "net_income_growth_yoy": 0.20
            },
            price_metrics={
                "beta": meta.get("beta", 1.10),
                "annualized_volatility": 25.0,
                "return_3m_pct": quote["change_pct"] * 4.0,
                "return_1y_pct": quote["change_pct"] * 12.0
            }
        )


analytics_service = AnalyticsService()
