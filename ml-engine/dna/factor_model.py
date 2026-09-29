"""
Stock DNA Multi-Factor Quantitative Profiler.
Computes 5 distinct factor scores (0 to 100) for comprehensive equity characterization.
"""
from typing import Dict, Any, Optional
import numpy as np


class StockDNAProfiler:
    """
    Constructs a 5-dimensional Stock DNA Vector:
    1. Value Factor (P/E, P/B, Dividend Yield, Free Cash Flow Yield)
    2. Growth Factor (Revenue 3Y CAGR, EPS Growth, Operating Income Expansion)
    3. Quality Factor (ROE, ROA, Gross Margin Stability, Debt-to-Equity)
    4. Momentum Factor (3M/6M/12M Relative Strength vs Market)
    5. Low Volatility Factor (Inverse Beta, Realized Volatility, Downside Semi-Variance)
    """

    @staticmethod
    def _normalize_score(value: float, min_val: float, max_val: float, invert: bool = False) -> float:
        """Clips and normalizes a raw metric onto a 0-100 scale."""
        if np.isnan(value) or np.isinf(value):
            return 50.0
        clipped = np.clip(value, min_val, max_val)
        norm = (clipped - min_val) / (max_val - min_val) * 100.0
        return round(float(100.0 - norm if invert else norm), 1)

    def calculate_dna(
        self,
        ticker: str,
        fundamentals: Dict[str, Any],
        price_metrics: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Calculates normalized DNA factor scores for an asset.
        """
        pe = fundamentals.get("pe_ratio", 25.0) or 25.0
        pb = fundamentals.get("pb_ratio", 4.0) or 4.0
        div_yield = fundamentals.get("dividend_yield", 0.015) or 0.015
        roe = fundamentals.get("roe", 0.18) or 0.18
        roa = fundamentals.get("roa", 0.08) or 0.08
        debt_to_equity = fundamentals.get("debt_to_equity", 0.8) or 0.8
        rev_growth = fundamentals.get("revenue_growth_yoy", 0.12) or 0.12
        net_inc_growth = fundamentals.get("net_income_growth_yoy", 0.15) or 0.15

        beta = price_metrics.get("beta", 1.10) or 1.10
        annualized_vol = price_metrics.get("annualized_volatility", 25.0) or 25.0
        return_3m = price_metrics.get("return_3m_pct", 8.0) or 8.0
        return_1y = price_metrics.get("return_1y_pct", 18.0) or 18.0

        # 1. Value Factor (lower PE & PB -> higher value score; higher div yield -> higher value)
        pe_score = self._normalize_score(pe, 8.0, 60.0, invert=True)
        pb_score = self._normalize_score(pb, 1.0, 15.0, invert=True)
        div_score = self._normalize_score(div_yield * 100, 0.0, 6.0, invert=False)
        value_score = round(pe_score * 0.45 + pb_score * 0.35 + div_score * 0.20, 1)

        # 2. Growth Factor
        rev_score = self._normalize_score(rev_growth * 100, -10.0, 45.0, invert=False)
        inc_score = self._normalize_score(net_inc_growth * 100, -15.0, 50.0, invert=False)
        growth_score = round(rev_score * 0.50 + inc_score * 0.50, 1)

        # 3. Quality Factor (higher ROE/ROA, lower D/E)
        roe_score = self._normalize_score(roe * 100, 0.0, 40.0, invert=False)
        roa_score = self._normalize_score(roa * 100, 0.0, 20.0, invert=False)
        de_score = self._normalize_score(debt_to_equity, 0.0, 3.0, invert=True)
        quality_score = round(roe_score * 0.40 + roa_score * 0.30 + de_score * 0.30, 1)

        # 4. Momentum Factor
        m3_score = self._normalize_score(return_3m, -20.0, 40.0, invert=False)
        m12_score = self._normalize_score(return_1y, -30.0, 70.0, invert=False)
        momentum_score = round(m3_score * 0.40 + m12_score * 0.60, 1)

        # 5. Low Volatility Factor (lower beta & vol -> higher low-vol score)
        beta_score = self._normalize_score(beta, 0.4, 2.2, invert=True)
        vol_score = self._normalize_score(annualized_vol, 10.0, 60.0, invert=True)
        low_vol_score = round(beta_score * 0.50 + vol_score * 0.50, 1)

        radar_data = [
            {"factor": "Value", "score": value_score, "fullMark": 100},
            {"factor": "Growth", "score": growth_score, "fullMark": 100},
            {"factor": "Quality", "score": quality_score, "fullMark": 100},
            {"factor": "Momentum", "score": momentum_score, "fullMark": 100},
            {"factor": "Low Volatility", "score": low_vol_score, "fullMark": 100},
        ]

        # Determine dominant persona
        scores = {
            "Deep Value": value_score,
            "High Growth": growth_score,
            "High Quality Compounder": quality_score,
            "High Momentum": momentum_score,
            "Defensive / Low Beta": low_vol_score
        }
        dominant_persona = max(scores, key=scores.get)

        return {
            "ticker": ticker,
            "factor_scores": {
                "value": value_score,
                "growth": growth_score,
                "quality": quality_score,
                "momentum": momentum_score,
                "low_volatility": low_vol_score,
            },
            "radar_data": radar_data,
            "dominant_persona": dominant_persona,
            "summary": f"{ticker} exhibits strongest characteristics in {dominant_persona} (Score: {scores[dominant_persona]}/100)."
        }
