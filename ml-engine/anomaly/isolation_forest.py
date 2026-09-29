"""
Market Anomaly Detection Module using Isolation Forest and Statistical Z-Score Filters.
"""
from typing import List, Dict, Any, Optional
import numpy as np
import pandas as pd
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler


class MarketAnomalyDetector:
    """
    Detects unusual market behavior by analyzing price returns, volume deviations,
    high-low volatility spreads, and return acceleration.
    """

    def __init__(self, contamination: float = 0.05, random_state: int = 42):
        self.contamination = contamination
        self.random_state = random_state
        self.model = IsolationForest(
            contamination=self.contamination,
            random_state=self.random_state,
            n_estimators=100,
        )
        self.scaler = StandardScaler()

    def _extract_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Extracts multi-dimensional quantitative features from standard OHLCV DataFrame.
        Expected columns: ['open', 'high', 'low', 'close', 'volume']
        """
        data = df.copy()
        data["log_return"] = np.log(data["close"] / data["close"].shift(1)).fillna(0)
        data["return_accel"] = data["log_return"] - data["log_return"].shift(1).fillna(0)
        data["hl_spread"] = (data["high"] - data["low"]) / data["close"]
        
        # Volume relative to 20-day rolling mean
        vol_rolling_mean = data["volume"].rolling(window=20, min_periods=5).mean().fillna(data["volume"])
        vol_rolling_std = data["volume"].rolling(window=20, min_periods=5).std().replace(0, 1).fillna(1)
        data["vol_zscore"] = (data["volume"] - vol_rolling_mean) / vol_rolling_std
        
        # 5-day realized volatility
        data["volatility_5d"] = data["log_return"].rolling(window=5, min_periods=2).std().fillna(0)
        
        feature_cols = ["log_return", "return_accel", "hl_spread", "vol_zscore", "volatility_5d"]
        return data[feature_cols].fillna(0)

    def detect_anomalies(self, df: pd.DataFrame, ticker: str = "TICKER") -> List[Dict[str, Any]]:
        """
        Runs Isolation Forest and returns structured anomaly events.
        """
        if len(df) < 15:
            return []

        features_df = self._extract_features(df)
        scaled_features = self.scaler.fit_transform(features_df)
        
        # -1 for anomaly, 1 for normal
        predictions = self.model.fit_predict(scaled_features)
        # Higher negative scores indicate greater anomaly severity
        decision_scores = self.model.decision_function(scaled_features)

        anomalies = []
        for idx in range(len(df)):
            if predictions[idx] == -1:
                # Raw decision score is negative for anomalies; convert to 0-1 severity
                raw_score = decision_scores[idx]
                severity = float(np.clip(1.0 - (raw_score + 0.5), 0.1, 1.0))
                
                row = df.iloc[idx]
                feat = features_df.iloc[idx]
                time_val = str(row.name) if isinstance(row.name, (pd.Timestamp, str)) else str(row.get("time", idx))
                
                # Determine anomaly type
                reasons = []
                if abs(feat["vol_zscore"]) > 2.5:
                    reasons.append(f"Volume spike ({feat['vol_zscore']:.1f}σ above 20d mean)")
                if abs(feat["log_return"]) > 0.04:
                    reasons.append(f"Price shock ({feat['log_return']*100:+.2f}% intraday move)")
                if feat["hl_spread"] > 0.05:
                    reasons.append(f"High-Low spread expansion ({feat['hl_spread']*100:.1f}%)")
                if feat["volatility_5d"] > 0.03:
                    reasons.append(f"Volatility regime shift ({feat['volatility_5d']*100:.1f}%)")
                
                summary = " & ".join(reasons) if reasons else "Multi-factor statistical deviation"
                
                anomalies.append({
                    "ticker": ticker,
                    "timestamp": time_val,
                    "anomaly_type": "VOLATILITY_BURST" if "Volatility" in summary else ("VOLUME_SPIKE" if "Volume" in summary else "PRICE_GAP"),
                    "severity_score": round(severity, 3),
                    "isolation_score": round(float(raw_score), 4),
                    "summary": summary,
                    "metrics": {
                        "close": float(row["close"]),
                        "volume": float(row["volume"]),
                        "volume_zscore": round(float(feat["vol_zscore"]), 2),
                        "log_return_pct": round(float(feat["log_return"] * 100), 2),
                        "hl_spread_pct": round(float(feat["hl_spread"] * 100), 2),
                    }
                })

        return anomalies
