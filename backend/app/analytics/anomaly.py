"""
Statistical Anomaly Detection & Volatility Regime Modeling.
Combines Isolation Forest, GARCH(1,1) Maximum Likelihood, and Rolling Z-Scores.
"""
from typing import List, Dict, Any, Optional
import numpy as np
import pandas as pd
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler
from scipy.optimize import minimize


class MarketAnomalyDetector:
    """
    Detects multivariate statistical deviations in trading time-series using Isolation Forest.
    """

    def __init__(self, contamination: float = 0.05, random_state: int = 42):
        self.contamination = contamination
        self.random_state = random_state
        self.model = IsolationForest(
            contamination=self.contamination,
            random_state=self.random_state,
            n_estimators=100
        )
        self.scaler = StandardScaler()

    def _extract_features(self, df: pd.DataFrame) -> pd.DataFrame:
        data = df.copy()
        c = data["close"].astype(float)
        h = data["high"].astype(float)
        l = data["low"].astype(float)
        v = data["volume"].astype(float)

        data["log_return"] = np.log(c / c.shift(1)).fillna(0)
        data["return_accel"] = (data["log_return"] - data["log_return"].shift(1)).fillna(0)
        data["hl_spread"] = (h - l) / c.replace(0, 1)

        vol_mean = v.rolling(20, min_periods=5).mean().fillna(v)
        vol_std = v.rolling(20, min_periods=5).std().replace(0, 1).fillna(1)
        data["vol_zscore"] = (v - vol_mean) / vol_std
        data["volatility_5d"] = data["log_return"].rolling(5, min_periods=2).std().fillna(0)

        feature_cols = ["log_return", "return_accel", "hl_spread", "vol_zscore", "volatility_5d"]
        return data[feature_cols].fillna(0)

    def detect_anomalies(self, df: pd.DataFrame, ticker: str = "TICKER") -> List[Dict[str, Any]]:
        if len(df) < 15:
            return []

        features_df = self._extract_features(df)
        scaled = self.scaler.fit_transform(features_df)

        preds = self.model.fit_predict(scaled)
        decision_scores = self.model.decision_function(scaled)

        anomalies = []
        for idx in range(len(df)):
            if preds[idx] == -1:
                raw_score = decision_scores[idx]
                severity = float(np.clip(1.0 - (raw_score + 0.5), 0.1, 1.0))
                row = df.iloc[idx]
                feat = features_df.iloc[idx]
                time_val = str(row.name) if isinstance(row.name, (pd.Timestamp, str)) else str(row.get("time", idx))

                reasons = []
                if abs(feat["vol_zscore"]) > 2.2:
                    reasons.append(f"Volume burst ({feat['vol_zscore']:.1f}σ from 20d mean)")
                if abs(feat["log_return"]) > 0.035:
                    reasons.append(f"Price shock ({feat['log_return']*100:+.2f}% intraday return)")
                if feat["hl_spread"] > 0.045:
                    reasons.append(f"High-Low spread expansion ({feat['hl_spread']*100:.1f}%)")

                summary = " & ".join(reasons) if reasons else "Multi-factor statistical deviation"
                atype = "VOLATILITY_BURST" if "spread" in summary.lower() else ("VOLUME_SPIKE" if "volume" in summary.lower() else "PRICE_GAP")

                anomalies.append({
                    "ticker": ticker,
                    "timestamp": time_val,
                    "anomaly_type": atype,
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


class GARCHVolatilityModel:
    """
    GARCH(1,1) conditional volatility process:
      sigma_t^2 = omega + alpha * eps_{t-1}^2 + beta * sigma_{t-1}^2
    """

    def __init__(self):
        self.omega: float = 0.0001
        self.alpha: float = 0.08
        self.beta: float = 0.88
        self.mu: float = 0.0

    def fit(self, returns: np.ndarray) -> "GARCHVolatilityModel":
        returns = np.asarray(returns, dtype=float)
        returns = returns[np.isfinite(returns)]
        if len(returns) < 25:
            self.omega = float(np.var(returns) * 0.1) if len(returns) > 0 else 0.0001
            self.mu = float(np.mean(returns)) if len(returns) > 0 else 0.0
            return self

        mu_init = np.mean(returns)
        var_init = np.var(returns)
        omega_init = var_init * 0.05
        bounds = ((1e-7, None), (0.001, 0.4), (0.4, 0.98))

        def garch_nll(params):
            omega, alpha, beta = params
            if alpha + beta >= 0.999:
                return 1e10
            resids = returns - mu_init
            n = len(resids)
            sig2 = np.zeros(n)
            sig2[0] = var_init
            for t in range(1, n):
                sig2[t] = omega + alpha * (resids[t - 1] ** 2) + beta * sig2[t - 1]
            return 0.5 * np.sum(np.log(2 * np.pi) + np.log(sig2) + (resids ** 2) / sig2)

        opt = minimize(garch_nll, [omega_init, 0.08, 0.88], bounds=bounds, method="L-BFGS-B")
        if opt.success:
            self.omega, self.alpha, self.beta = opt.x
        else:
            self.omega, self.alpha, self.beta = omega_init, 0.08, 0.88
        self.mu = mu_init
        return self

    def forecast(self, returns: np.ndarray, horizon: int = 5) -> Dict[str, Any]:
        returns = np.asarray(returns, dtype=float)
        returns = returns[np.isfinite(returns)]
        if len(returns) < 5:
            return {
                "current_annualized_volatility_pct": 20.0,
                "historical_mean_volatility_pct": 20.0,
                "volatility_zscore": 0.0,
                "regime": "NORMAL_VOLATILITY",
                "forecast_next_days": [20.0] * horizon
            }

        self.fit(returns)
        resids = returns - self.mu
        n = len(resids)
        sig2 = np.zeros(n)
        sig2[0] = np.var(returns)
        for t in range(1, n):
            sig2[t] = self.omega + self.alpha * (resids[t - 1] ** 2) + self.beta * sig2[t - 1]

        ann_vols = np.sqrt(sig2 * 252) * 100.0
        current_vol = ann_vols[-1]
        mean_vol = np.mean(ann_vols)
        zscore = (current_vol - mean_vol) / (np.std(ann_vols) + 1e-6)

        forecasts = []
        cur_s2 = sig2[-1]
        for _ in range(horizon):
            cur_s2 = self.omega + (self.alpha + self.beta) * cur_s2
            forecasts.append(round(float(np.sqrt(cur_s2 * 252) * 100.0), 2))

        return {
            "current_annualized_volatility_pct": round(float(current_vol), 2),
            "historical_mean_volatility_pct": round(float(mean_vol), 2),
            "volatility_zscore": round(float(zscore), 2),
            "persistence_factor": round(float(self.alpha + self.beta), 4),
            "forecast_next_days": forecasts,
            "regime": "HIGH_VOLATILITY" if zscore > 1.5 else ("LOW_VOLATILITY" if zscore < -1.0 else "NORMAL_VOLATILITY")
        }


class VolumeSpikeDetector:
    """Detects abnormal volume bursts and institutional accumulation patterns."""

    def __init__(self, window: int = 20, z_threshold: float = 2.0):
        self.window = window
        self.z_threshold = z_threshold

    def analyze(self, df: pd.DataFrame, ticker: str = "TICKER") -> Dict[str, Any]:
        if len(df) < self.window:
            return {
                "ticker": ticker,
                "latest_volume": float(df["volume"].iloc[-1]) if len(df) > 0 else 0,
                "volume_zscore": 0.0,
                "is_spike": False,
                "volume_ratio_to_20d_avg": 1.0,
                "institutional_flow_hint": "NEUTRAL"
            }

        vols = df["volume"].astype(float)
        closes = df["close"].astype(float)
        opens = df["open"].astype(float)

        mean_v = vols.rolling(self.window).mean()
        std_v = vols.rolling(self.window).std().replace(0, 1.0)
        z = (vols - mean_v) / std_v

        latest_z = float(z.iloc[-1])
        latest_vol = float(vols.iloc[-1])
        latest_mean = float(mean_v.iloc[-1])
        ratio = round(latest_vol / max(1.0, latest_mean), 2)

        price_delta = closes.iloc[-1] - opens.iloc[-1]
        flow = "ACCUMULATION" if price_delta > 0 and latest_z > 1.5 else (
            "DISTRIBUTION" if price_delta < 0 and latest_z > 1.5 else "NEUTRAL"
        )

        return {
            "ticker": ticker,
            "latest_volume": latest_vol,
            "average_volume_20d": round(latest_mean, 0),
            "volume_zscore": round(latest_z, 2),
            "volume_ratio_to_20d_avg": ratio,
            "is_spike": latest_z >= self.z_threshold,
            "institutional_flow_hint": flow
        }
