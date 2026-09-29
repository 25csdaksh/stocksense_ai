"""
Econometric Granger Causality Analysis for Lead-Lag Financial Relationships.
"""
from typing import Dict, Any, List, Optional
import numpy as np
import pandas as pd
from statsmodels.tsa.stattools import grangercausalitytests


class GrangerCausalityAnalyzer:
    """
    Tests whether past values of series X contain information that helps predict
    series Y beyond the information contained in past values of Y alone.
    """

    def __init__(self, max_lag: int = 5):
        self.max_lag = max_lag

    def test_causality(
        self,
        series_cause: pd.Series,
        series_effect: pd.Series,
        cause_name: str = "X",
        effect_name: str = "Y"
    ) -> Dict[str, Any]:
        """
        Executes Vector Autoregressive Granger Causality test.
        """
        df = pd.concat([series_effect, series_cause], axis=1).dropna()
        if len(df) < (self.max_lag * 3 + 10):
            return {
                "cause": cause_name,
                "effect": effect_name,
                "is_causal": False,
                "min_p_value": 1.0,
                "optimal_lag": 1,
                "summary": "Insufficient time-series observations to infer causality."
            }

        try:
            # grangercausalitytests expects [y, x] in columns
            test_results = grangercausalitytests(
                df.values,
                maxlag=self.max_lag,
                verbose=False
            )

            p_values = {}
            f_stats = {}
            for lag, result in test_results.items():
                # Extract F-test p-value (ssr_ftest)
                f_test = result[0]["ssr_ftest"]
                f_stats[lag] = float(f_test[0])
                p_values[lag] = float(f_test[1])

            # Find best lag with lowest p-value
            best_lag = min(p_values, key=p_values.get)
            min_p = p_values[best_lag]
            is_significant = min_p < 0.05

            summary = (
                f"{cause_name} significantly Granger-causes {effect_name} "
                f"at lag {best_lag} days (p={min_p:.4f}, F={f_stats[best_lag]:.2f})"
                if is_significant else
                f"No significant lead-lag predictive relationship found from {cause_name} to {effect_name} (p={min_p:.4f})"
            )

            return {
                "cause": cause_name,
                "effect": effect_name,
                "is_causal": bool(is_significant),
                "min_p_value": round(float(min_p), 4),
                "optimal_lag": int(best_lag),
                "f_statistic": round(float(f_stats[best_lag]), 2),
                "p_values_by_lag": {k: round(v, 4) for k, v in p_values.items()},
                "summary": summary
            }
        except Exception as err:
            return {
                "cause": cause_name,
                "effect": effect_name,
                "is_causal": False,
                "min_p_value": 1.0,
                "optimal_lag": 1,
                "summary": f"Granger test numerical exception: {str(err)}"
            }
