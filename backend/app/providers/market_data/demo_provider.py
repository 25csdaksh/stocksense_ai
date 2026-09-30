"""
MarketMind AI — Demo Market Data Provider Adapter.
Phase 6.1: Offline synthetic sandbox market provider with transparent data provenance (DEMO/MODEL_DERIVED).
"""
import time
from datetime import datetime, timezone, timedelta
from typing import Dict, Any, List, Optional
import numpy as np
import pandas as pd

from app.providers.market_data.base import MarketDataProvider
from app.providers.market_data.models import (
    NormalizedQuote,
    HistoricalCandle,
    HistoricalDataResponse,
    MarketIndexQuote,
    CompanyFundamentals,
    CompanyProfile,
    MarketNewsItem,
    MarketSessionStatus,
    ProviderHealth,
    DataStatus,
    ProviderStatus
)
from app.providers.market_data.symbol_normalizer import normalize_symbol
from app.providers.market_data.session import market_session_manager
from app.providers.market_data.validator import validator
from app.providers.market_data.rate_limiter import ProviderRateLimiter
from app.providers.market_data.observability import log_market_data_operation
from app.analytics.technical import compute_all_technical_indicators
from app.utils.constants import SUPPORTED_UNIVERSE, DEFAULT_INDICES


class DemoMarketProvider(MarketDataProvider):
    """
    High-fidelity offline synthetic provider.
    Explicitly labels all payloads as DEMO/MODEL_DERIVED with is_synthetic=True.
    """

    def __init__(self):
        self.provider_name = "DemoMarketProvider"
        self.market = "GLOBAL"
        self.rate_limiter = ProviderRateLimiter(self.provider_name, max_requests_per_minute=10000)
        self.status = ProviderStatus.DEMO
        self.last_successful_request: Optional[str] = None
        self.last_latency_ms: Optional[float] = None

    async def get_quote(self, symbol: str) -> NormalizedQuote:
        start_t = time.perf_counter()
        norm = normalize_symbol(symbol)
        canonical = norm.canonical_symbol

        base_p = 150.0 if norm.market == "US" else 1500.0
        currency = "USD" if norm.market == "US" else "INR"

        np.random.seed(abs(hash(canonical)) % 10000)
        chg_pct = round(float(np.sin(hash(canonical)) * 1.5), 2)
        chg = round(base_p * (chg_pct / 100.0), 2)
        open_p = round(base_p * 0.995, 2)
        high_p = round(max(open_p, base_p + chg) * 1.012, 2)
        low_p = round(min(open_p, base_p + chg) * 0.988, 2)
        cur_p = round(base_p + chg, 2)

        latency = (time.perf_counter() - start_t) * 1000.0
        self.last_latency_ms = latency
        self.last_successful_request = datetime.now(timezone.utc).isoformat()

        quote = NormalizedQuote(
            symbol=canonical,
            ticker=norm.display_symbol,
            name=norm.name or f"{norm.display_symbol} Demo Asset",
            exchange=norm.exchange,
            currency=currency,
            price=cur_p,
            open=open_p,
            high=high_p,
            low=low_p,
            previous_close=base_p,
            change=chg,
            change_percent=chg_pct,
            change_pct=chg_pct,
            volume=15000000.0,
            market_cap=500e9 if currency == "USD" else 50000000000.0,
            pe_ratio=25.0,
            week_52_high=round(base_p * 1.25, 2),
            week_52_low=round(base_p * 0.75, 2),
            market_status="REGULAR",
            data_source="DEMO_SYNTHETIC_FEED",
            data_status=DataStatus.DEMO,
            is_synthetic=True,
            timestamp=datetime.now(timezone.utc).isoformat()
        )
        log_market_data_operation(self.provider_name, "get_quote", canonical, latency, True)
        return quote

    async def get_quotes(self, symbols: List[str]) -> List[NormalizedQuote]:
        return [await self.get_quote(s) for s in symbols]

    async def get_historical_data(
        self,
        symbol: str,
        start: Optional[datetime] = None,
        end: Optional[datetime] = None,
        interval: str = "1d",
        timeframe: Optional[str] = "6m"
    ) -> HistoricalDataResponse:
        start_t = time.perf_counter()
        norm = normalize_symbol(symbol)
        canonical = norm.canonical_symbol
        tf = (timeframe or "6m").lower()
        currency = "USD" if norm.market == "US" else "INR"

        days_map = {"1m": 22, "3m": 65, "6m": 120, "1y": 252, "2y": 504, "5y": 1260}
        total_bars = days_map.get(tf, 120)

        base_p = 150.0 if norm.market == "US" else 1500.0
        np.random.seed(abs(hash(canonical)) % 10000)
        daily_returns = np.random.normal(0.0005, 0.015, total_bars)
        price_curve = base_p * np.cumprod(1 + daily_returns[::-1])[::-1]

        end_date = datetime.now(timezone.utc)
        raw_bars = []

        for i in range(total_bars):
            bar_date = end_date - timedelta(days=(total_bars - i))
            c = float(price_curve[i])
            o = float(c * (1 + np.random.uniform(-0.005, 0.005)))
            h = float(max(o, c) * (1 + np.random.uniform(0.002, 0.010)))
            l = float(min(o, c) * (1 - np.random.uniform(0.002, 0.010)))
            vol = float(np.random.uniform(1_000_000, 10_000_000))

            raw_bars.append({
                "time": bar_date.strftime("%Y-%m-%d"),
                "timestamp": bar_date,
                "open": round(o, 2),
                "high": round(h, 2),
                "low": round(l, 2),
                "close": round(c, 2),
                "volume": round(vol, 0),
                "symbol": canonical,
                "exchange": norm.exchange,
                "currency": currency,
                "data_source": "DEMO_SYNTHETIC_GENERATOR",
                "data_status": DataStatus.DEMO,
                "sma_20": round(c * 0.99, 2),
                "sma_50": round(c * 0.97, 2),
                "ema_20": round(c * 0.992, 2),
                "rsi_14": round(50.0 + float(np.sin(i / 6.0) * 18.0), 2),
                "vwap": round(c * 1.001, 2)
            })

        validated = validator.filter_and_validate_candles(raw_bars, symbol=canonical)
        latency = (time.perf_counter() - start_t) * 1000.0
        self.last_latency_ms = latency
        self.last_successful_request = datetime.now(timezone.utc).isoformat()

        res = HistoricalDataResponse(
            symbol=canonical,
            ticker=norm.display_symbol,
            timeframe=tf,
            interval=interval,
            currency=currency,
            bars=validated,
            total_bars=len(validated),
            data_source="DEMO_SYNTHETIC_GENERATOR",
            data_status=DataStatus.DEMO,
            is_synthetic=True
        )
        log_market_data_operation(self.provider_name, "get_historical_data", canonical, latency, True)
        return res

    async def get_fundamentals(self, symbol: str) -> CompanyFundamentals:
        norm = normalize_symbol(symbol)
        currency = "USD" if norm.market == "US" else "INR"
        return CompanyFundamentals(
            symbol=norm.canonical_symbol,
            name=norm.name or norm.display_symbol,
            market_cap=500e9 if currency == "USD" else 50000000000.0,
            pe_ratio=25.0,
            pb_ratio=4.0,
            dividend_yield=0.015,
            beta=1.0,
            eps=6.0,
            currency=currency,
            data_source="DEMO_FUNDAMENTALS",
            data_status=DataStatus.DEMO
        )

    async def get_company_profile(self, symbol: str) -> CompanyProfile:
        norm = normalize_symbol(symbol)
        currency = "USD" if norm.market == "US" else "INR"
        return CompanyProfile(
            symbol=norm.canonical_symbol,
            name=norm.name or norm.display_symbol,
            exchange=norm.exchange,
            sector="Demo Sandbox",
            industry="Simulated Market",
            description=f"Simulated demo entity for {norm.display_symbol}.",
            currency=currency,
            data_source="DEMO_REGISTRY"
        )

    async def get_market_indices(self) -> List[MarketIndexQuote]:
        return [
            MarketIndexQuote(
                symbol="^GSPC",
                name="S&P 500",
                exchange="NYSE",
                price=5748.20,
                change=26.40,
                change_pct=0.46,
                currency="USD",
                timestamp=datetime.now(timezone.utc).isoformat(),
                data_source="DEMO_INDICES",
                data_status=DataStatus.DEMO
            ),
            MarketIndexQuote(
                symbol="^NSEI",
                name="NIFTY 50",
                exchange="NSE",
                price=24850.0,
                change=112.50,
                change_pct=0.45,
                currency="INR",
                timestamp=datetime.now(timezone.utc).isoformat(),
                data_source="DEMO_INDICES",
                data_status=DataStatus.DEMO
            )
        ]

    async def get_news(self, symbol: Optional[str] = None, limit: int = 10) -> List[MarketNewsItem]:
        sym = symbol or "DEMO"
        return [
            MarketNewsItem(
                id=f"demo-news-{i}",
                title=f"{sym} Demo News: Synthetic Market Simulation Running Stable",
                summary="MarketMind AI deterministic simulation engine operating with full schema integrity.",
                source="MarketMind Sandbox",
                url=None,
                published_at=datetime.now(timezone.utc).isoformat(),
                sentiment="NEUTRAL",
                sentiment_score=0.0,
                symbols=[sym]
            )
            for i in range(1, min(limit + 1, 3))
        ]

    async def get_market_status(self) -> MarketSessionStatus:
        return market_session_manager.get_session_status("GLOBAL")

    async def get_health(self) -> ProviderHealth:
        return ProviderHealth(
            provider_name=self.provider_name,
            market=self.market,
            status=self.status,
            last_successful_request=self.last_successful_request,
            latency_ms=self.last_latency_ms,
            configuration_status="Demo Market Provider (Offline Synthetic Mode Active)",
            requests_remaining=self.rate_limiter.requests_remaining,
            rate_limit_status=self.rate_limiter.rate_limit_status
        )


demo_market_provider = DemoMarketProvider()
