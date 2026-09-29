"""
Stock DNA Multi-Factor Quantitative Profiler & Radar Normalization.
Quantifies 5 structural pillars: Value, Growth, Quality, Momentum, Low Volatility.
"""
from typing import Dict, Any, List, Optional
import numpy as np


class StockDNAProfiler:
    """Calculates multi-dimensional factor percentile scores on a 0-100 scale."""

    @staticmethod
    def _normalize(val: float, min_v: float, max_v: float, invert: bool = False) -> float:
        if np.isnan(val) or np.isinf(val):
            return 50.0
        clipped = np.clip(val, min_v, max_v)
        pct = (clipped - min_v) / (max_v - min_v) * 100.0
        return round(float(100.0 - pct if invert else pct), 1)

    def calculate(
        self,
        ticker: str,
        fundamentals: Dict[str, Any],
        price_metrics: Dict[str, Any]
    ) -> Dict[str, Any]:
        pe = fundamentals.get("pe_ratio", 28.0) or 28.0
        pb = fundamentals.get("pb_ratio", 5.0) or 5.0
        div = fundamentals.get("dividend_yield", 0.01) or 0.01
        roe = fundamentals.get("roe", 0.20) or 0.20
        roa = fundamentals.get("roa", 0.10) or 0.10
        de = fundamentals.get("debt_to_equity", 0.70) or 0.70
        rev_g = fundamentals.get("revenue_growth_yoy", 0.15) or 0.15
        inc_g = fundamentals.get("net_income_growth_yoy", 0.18) or 0.18

        beta = price_metrics.get("beta", 1.10) or 1.10
        vol = price_metrics.get("annualized_volatility", 25.0) or 25.0
        r3m = price_metrics.get("return_3m_pct", 8.0) or 8.0
        r1y = price_metrics.get("return_1y_pct", 20.0) or 20.0

        # Factor 1: Value
        pe_s = self._normalize(pe, 8.0, 60.0, invert=True)
        pb_s = self._normalize(pb, 1.0, 15.0, invert=True)
        div_s = self._normalize(div * 100.0, 0.0, 6.0, invert=False)
        val_score = round(pe_s * 0.45 + pb_s * 0.35 + div_s * 0.20, 1)

        # Factor 2: Growth
        rev_s = self._normalize(rev_g * 100.0, -10.0, 45.0, invert=False)
        inc_s = self._normalize(inc_g * 100.0, -15.0, 50.0, invert=False)
        gro_score = round(rev_s * 0.50 + inc_s * 0.50, 1)

        # Factor 3: Quality
        roe_s = self._normalize(roe * 100.0, 0.0, 40.0, invert=False)
        roa_s = self._normalize(roa * 100.0, 0.0, 20.0, invert=False)
        de_s = self._normalize(de, 0.0, 3.0, invert=True)
        qua_score = round(roe_s * 0.40 + roa_s * 0.30 + de_s * 0.30, 1)

        # Factor 4: Momentum
        m3_s = self._normalize(r3m, -20.0, 40.0, invert=False)
        m1y_s = self._normalize(r1y, -30.0, 70.0, invert=False)
        mom_score = round(m3_s * 0.40 + m1y_s * 0.60, 1)

        # Factor 5: Low Volatility
        beta_s = self._normalize(beta, 0.4, 2.2, invert=True)
        vol_s = self._normalize(vol, 10.0, 60.0, invert=True)
        vol_score = round(beta_s * 0.50 + vol_s * 0.50, 1)

        radar_data = [
            {"factor": "Value", "score": val_score, "fullMark": 100},
            {"factor": "Growth", "score": gro_score, "fullMark": 100},
            {"factor": "Quality", "score": qua_score, "fullMark": 100},
            {"factor": "Momentum", "score": mom_score, "fullMark": 100},
            {"factor": "Low Volatility", "score": vol_score, "fullMark": 100},
        ]

        personas = {
            "Deep Value": val_score,
            "High Growth": gro_score,
            "High Quality Compounder": qua_score,
            "High Momentum": mom_score,
            "Defensive / Low Beta": vol_score
        }
        dominant = max(personas, key=personas.get)

        return {
            "ticker": ticker,
            "factor_scores": {
                "value": val_score,
                "growth": gro_score,
                "quality": qua_score,
                "momentum": mom_score,
                "low_volatility": vol_score,
            },
            "radar_data": radar_data,
            "dominant_persona": dominant,
            "summary": f"{ticker} exhibits strongest quantitative factor loading in {dominant} (Score: {personas[dominant]}/100)."
        }
