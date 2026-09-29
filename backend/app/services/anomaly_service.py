"""
Market Anomaly Detection & Cross-Asset Volatility Service.
"""
from typing import Dict, Any, List
from datetime import datetime
import pandas as pd
from app.providers.market_data.factory import get_market_data_provider
from app.analytics.anomaly import MarketAnomalyDetector, GARCHVolatilityModel, VolumeSpikeDetector
from app.utils.constants import SUPPORTED_UNIVERSE
from app.utils.validators import validate_ticker


class AnomalyService:

    def __init__(self):
        self.market_provider = get_market_data_provider()
        self.detector = MarketAnomalyDetector(contamination=0.06)
        self.garch = GARCHVolatilityModel()
        self.spike_detector = VolumeSpikeDetector()

    async def get_ticker_anomalies(self, ticker: str) -> Dict[str, Any]:
        sym = validate_ticker(ticker)
        hist = await self.market_provider.get_history(sym, timeframe="3m", interval="1d")
        bars = hist["bars"]
        if not bars or len(bars) < 15:
            return {"ticker": sym, "anomalies": [], "volatility_regime": {}, "volume_spike": {}}

        df = pd.DataFrame(bars)
        anomalies = self.detector.detect_anomalies(df, ticker=sym)
        returns = df["close"].pct_change().dropna().values
        vol_regime = self.garch.forecast(returns, horizon=5)
        vol_spike = self.spike_detector.analyze(df, ticker=sym)

        return {
            "ticker": sym,
            "anomalies": anomalies[-10:],
            "volatility_regime": vol_regime,
            "volume_spike": vol_spike
        }

    async def get_market_anomaly_stream(self) -> Dict[str, Any]:
        all_anomalies: List[Dict[str, Any]] = []
        tickers = list(SUPPORTED_UNIVERSE.keys())

        for t in tickers:
            hist = await self.market_provider.get_history(t, timeframe="3m", interval="1d")
            bars = hist["bars"]
            if bars and len(bars) >= 15:
                df = pd.DataFrame(bars)
                anoms = self.detector.detect_anomalies(df, ticker=t)
                if anoms:
                    all_anomalies.extend(anoms[-2:])

        # Sort by severity descending
        all_anomalies.sort(key=lambda x: x.get("severity_score", 0), reverse=True)

        # Calculate systemic stress index from average severity
        if all_anomalies:
            avg_sev = sum(a.get("severity_score", 0.5) for a in all_anomalies) / len(all_anomalies)
            stress_index = round(float(avg_sev * 100.0), 2)
        else:
            stress_index = 18.5

        return {
            "anomalies": all_anomalies[:25],
            "total_active": len(all_anomalies),
            "systemic_stress_index": stress_index,
            "timestamp": datetime.utcnow().isoformat()
        }


anomaly_service = AnomalyService()
