"""
High-Fidelity Synthetic Market Data Provider.
Explicitly tags all records with is_synthetic=True for transparent academic sandbox development.
"""
from typing import Dict, Any, List
from datetime import datetime, timedelta
import numpy as np
import pandas as pd
from app.providers.market_data.base import MarketDataProvider
from app.analytics.technical import compute_all_technical_indicators
from app.utils.constants import SUPPORTED_UNIVERSE, DEFAULT_INDICES


class MockMarketProvider(MarketDataProvider):

    async def get_history(self, ticker: str, timeframe: str = "6m", interval: str = "1d") -> Dict[str, Any]:
        ticker = ticker.upper()
        meta = SUPPORTED_UNIVERSE.get(ticker, {"base_price": 120.0, "beta": 1.10})
        days_map = {"1m": 22, "3m": 65, "6m": 126, "1y": 252, "5y": 1260}
        total_days = days_map.get(timeframe, 126)

        np.random.seed(abs(hash(ticker)) % 50000)
        end_date = datetime.utcnow().date()
        date_list = [end_date - timedelta(days=x) for x in range(total_days * 2) if (end_date - timedelta(days=x)).weekday() < 5][:total_days]
        date_list.reverse()

        base_p = meta["base_price"] * 0.85
        vol = 0.016 * meta.get("beta", 1.0)
        returns = np.random.normal(0.0006, vol, size=total_days)

        price_series = [base_p]
        for r in returns:
            price_series.append(price_series[-1] * np.exp(r))
        price_series = price_series[1:]

        rows = []
        for i, d in enumerate(date_list):
            c = price_series[i]
            o = c * (1.0 + np.random.normal(0, 0.004))
            h = max(o, c) * (1.0 + abs(np.random.normal(0, 0.007)))
            l = min(o, c) * (1.0 - abs(np.random.normal(0, 0.007)))
            v = int(np.random.normal(30_000_000, 6_000_000))
            rows.append({
                "time": d.strftime("%Y-%m-%d"),
                "open": round(o, 2),
                "high": round(h, 2),
                "low": round(l, 2),
                "close": round(c, 2),
                "volume": max(100_000, v)
            })

        df = pd.DataFrame(rows)
        df = compute_all_technical_indicators(df)

        bars = []
        for _, row in df.iterrows():
            bars.append({
                "time": str(row["time"]),
                "open": float(row["open"]),
                "high": float(row["high"]),
                "low": float(row["low"]),
                "close": float(row["close"]),
                "volume": float(row["volume"]),
                "sma_20": float(row["sma_20"]) if pd.notna(row.get("sma_20")) else None,
                "sma_50": float(row["sma_50"]) if pd.notna(row.get("sma_50")) else None,
                "ema_20": float(row["ema_20"]) if pd.notna(row.get("ema_20")) else None,
                "rsi_14": float(row["rsi_14"]) if pd.notna(row.get("rsi_14")) else None,
                "vwap": float(row["vwap"]) if pd.notna(row.get("vwap")) else None,
            })

        return {
            "ticker": ticker,
            "timeframe": timeframe,
            "interval": interval,
            "bars": bars,
            "is_synthetic": True,
            "total_bars": len(bars)
        }

    async def get_quote(self, ticker: str) -> Dict[str, Any]:
        ticker = ticker.upper()
        hist = await self.get_history(ticker, timeframe="1m")
        bars = hist["bars"]
        latest = bars[-1]
        prev = bars[-2]

        price = latest["close"]
        prev_close = prev["close"]
        change = price - prev_close
        change_pct = (change / prev_close) * 100.0
        meta = SUPPORTED_UNIVERSE.get(ticker, {"name": ticker, "pe": 28.0, "market_cap": 1e12})

        return {
            "ticker": ticker,
            "name": meta.get("name", ticker),
            "price": round(float(price), 2),
            "change": round(float(change), 2),
            "change_pct": round(float(change_pct), 2),
            "open": round(float(latest["open"]), 2),
            "high": round(float(latest["high"]), 2),
            "low": round(float(latest["low"]), 2),
            "previous_close": round(float(prev_close), 2),
            "volume": float(latest["volume"]),
            "market_cap": meta.get("market_cap", 1e12),
            "pe_ratio": meta.get("pe", 28.0),
            "week_52_high": round(float(price * 1.15), 2),
            "week_52_low": round(float(price * 0.85), 2),
            "is_synthetic": True,
            "data_source": "SYNTHETIC_MOCK_FEED",
            "timestamp": datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC")
        }

    async def get_indices(self) -> List[Dict[str, Any]]:
        return DEFAULT_INDICES
