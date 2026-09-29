"""
Volume Spike & Institutional Flow Deviation Detector.
"""
from typing import Dict, Any, List
import numpy as np
import pandas as pd


class VolumeSpikeDetector:
    """
    Detects abnormal trading volume bursts and institutional accumulation/distribution patterns.
    """

    def __init__(self, window: int = 20, z_threshold: float = 2.0):
        self.window = window
        self.z_threshold = z_threshold

    def analyze(self, df: pd.DataFrame, ticker: str = "TICKER") -> Dict[str, Any]:
        """
        Analyzes the volume profile and recent volume anomalies.
        """
        if len(df) < self.window:
            return {
                "ticker": ticker,
                "latest_volume": float(df["volume"].iloc[-1]) if len(df) > 0 else 0,
                "volume_zscore": 0.0,
                "is_spike": False,
                "volume_ratio_to_20d_avg": 1.0,
                "volume_profile": "NORMAL"
            }

        volumes = df["volume"].astype(float)
        closes = df["close"].astype(float)
        opens = df["open"].astype(float)

        rolling_mean = volumes.rolling(self.window).mean()
        rolling_std = volumes.rolling(self.window).std().replace(0, 1.0)
        zscores = (volumes - rolling_mean) / rolling_std

        latest_vol = float(volumes.iloc[-1])
        latest_mean = float(rolling_mean.iloc[-1])
        latest_z = float(zscores.iloc[-1])
        ratio = round(latest_vol / max(1.0, latest_mean), 2)

        # Estimate buying vs selling pressure based on close relative to open
        price_diff = closes.iloc[-1] - opens.iloc[-1]
        flow_type = "ACCUMULATION" if price_diff > 0 and latest_z > 1.5 else (
            "DISTRIBUTION" if price_diff < 0 and latest_z > 1.5 else "NEUTRAL"
        )

        # Historical spikes in the series
        spike_indices = np.where(zscores.values > self.z_threshold)[0]
        recent_spikes = []
        for idx in spike_indices[-5:]:
            row = df.iloc[idx]
            time_val = str(row.name) if isinstance(row.name, (pd.Timestamp, str)) else str(row.get("time", idx))
            recent_spikes.append({
                "date": time_val,
                "volume": float(volumes.iloc[idx]),
                "z_score": round(float(zscores.iloc[idx]), 2),
                "price_change_pct": round(float((closes.iloc[idx] - opens.iloc[idx]) / opens.iloc[idx] * 100), 2)
            })

        return {
            "ticker": ticker,
            "latest_volume": latest_vol,
            "average_volume_20d": round(latest_mean, 0),
            "volume_zscore": round(latest_z, 2),
            "volume_ratio_to_20d_avg": ratio,
            "is_spike": latest_z >= self.z_threshold,
            "institutional_flow_hint": flow_type,
            "recent_spikes_count": len(spike_indices),
            "recent_spikes": recent_spikes
        }
