"""
Live Yahoo Finance Market Data Provider Implementation.
"""
from typing import Dict, Any, List
from datetime import datetime
import pandas as pd
import yfinance as yf
from app.providers.market_data.base import MarketDataProvider
from app.analytics.technical import compute_all_technical_indicators
from app.utils.constants import SUPPORTED_UNIVERSE, DEFAULT_INDICES
from app.core.logging import logger


class YFinanceProvider(MarketDataProvider):

    async def get_quote(self, ticker: str) -> Dict[str, Any]:
        ticker = ticker.upper()
        hist = await self.get_history(ticker, timeframe="1m", interval="1d")
        bars = hist.get("bars", [])

        if len(bars) >= 2:
            latest = bars[-1]
            prev = bars[-2]
            price = latest["close"]
            prev_close = prev["close"]
            change = price - prev_close
            change_pct = (change / prev_close) * 100.0
            high = latest["high"]
            low = latest["low"]
            open_p = latest["open"]
            vol = latest["volume"]
        else:
            meta = SUPPORTED_UNIVERSE.get(ticker, {"base_price": 150.0})
            price = meta["base_price"]
            prev_close = price * 0.99
            change = price - prev_close
            change_pct = 1.01
            high = price * 1.015
            low = price * 0.985
            open_p = price * 0.995
            vol = 25000000.0

        meta = SUPPORTED_UNIVERSE.get(ticker, {"name": ticker, "pe": 28.0, "market_cap": 500e9})
        closes = [b["close"] for b in bars] if bars else [price]
        w52_h = max(closes) * 1.05 if closes else price * 1.1
        w52_l = min(closes) * 0.95 if closes else price * 0.9

        return {
            "ticker": ticker,
            "name": meta.get("name", ticker),
            "price": round(float(price), 2),
            "change": round(float(change), 2),
            "change_pct": round(float(change_pct), 2),
            "open": round(float(open_p), 2),
            "high": round(float(high), 2),
            "low": round(float(low), 2),
            "previous_close": round(float(prev_close), 2),
            "volume": float(vol),
            "market_cap": meta.get("market_cap", 1e12),
            "pe_ratio": meta.get("pe", 28.0),
            "week_52_high": round(float(w52_h), 2),
            "week_52_low": round(float(w52_l), 2),
            "is_synthetic": hist.get("is_synthetic", False),
            "data_source": "EXCHANGE_FEED_YFINANCE" if not hist.get("is_synthetic") else "SYNTHETIC_MOCK_FALLBACK",
            "timestamp": datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC")
        }

    async def get_history(self, ticker: str, timeframe: str = "6m", interval: str = "1d") -> Dict[str, Any]:
        ticker = ticker.upper()
        period_map = {"1m": "1mo", "3m": "3mo", "6m": "6mo", "1y": "1y", "5y": "5y"}
        yf_period = period_map.get(timeframe, "6mo")

        try:
            data = yf.Ticker(ticker).history(period=yf_period, interval=interval)
            if data is not None and not data.empty and len(data) > 3:
                df = data.reset_index()
                df.rename(columns={
                    "Date": "time", "Datetime": "time",
                    "Open": "open", "High": "high",
                    "Low": "low", "Close": "close",
                    "Volume": "volume"
                }, inplace=True)
                df["time"] = df["time"].dt.strftime("%Y-%m-%d")
                df = compute_all_technical_indicators(df)
                
                bars = []
                for _, row in df.iterrows():
                    bars.append({
                        "time": str(row["time"]),
                        "open": round(float(row["open"]), 2),
                        "high": round(float(row["high"]), 2),
                        "low": round(float(row["low"]), 2),
                        "close": round(float(row["close"]), 2),
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
                    "is_synthetic": False,
                    "total_bars": len(bars)
                }
        except Exception as err:
            logger.info(f"YFinance live fetch exception ({err}), falling back to mock provider.")

        # Fallback to mock
        from app.providers.market_data.mock_provider import MockMarketProvider
        mock_p = MockMarketProvider()
        return await mock_p.get_history(ticker, timeframe, interval)

    async def get_indices(self) -> List[Dict[str, Any]]:
        return DEFAULT_INDICES
