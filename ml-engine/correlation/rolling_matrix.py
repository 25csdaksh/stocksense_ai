"""
Dynamic Rolling Correlation & Covariance Matrix Engine for Multi-Asset Portfolios.
"""
from typing import Dict, List, Any, Optional
import numpy as np
import pandas as pd


class RollingCorrelationEngine:
    """
    Computes Pearson and Spearman correlation matrices, rolling correlation time series,
    and asset betas against benchmark indices.
    """

    @staticmethod
    def compute_correlation_matrix(
        returns_df: pd.DataFrame,
        method: str = "pearson"
    ) -> Dict[str, Any]:
        """
        Computes pairwise correlation matrix for a DataFrame of asset returns.
        """
        clean_returns = returns_df.dropna()
        if clean_returns.empty or clean_returns.shape[1] < 2:
            cols = list(returns_df.columns)
            n = len(cols)
            eye = np.eye(n).tolist()
            return {
                "assets": cols,
                "matrix": eye,
                "method": method,
                "observations": 0
            }

        corr_matrix = clean_returns.corr(method=method).round(4)
        assets = list(corr_matrix.columns)
        
        # Convert to nested list for JSON serialization
        matrix_list = []
        for i, row in corr_matrix.iterrows():
            matrix_list.append(row.tolist())

        # Extract top correlated pairs (excluding self 1.0)
        pairs = []
        for i in range(len(assets)):
            for j in range(i + 1, len(assets)):
                pairs.append({
                    "asset_a": assets[i],
                    "asset_b": assets[j],
                    "correlation": float(corr_matrix.iloc[i, j])
                })
        
        pairs.sort(key=lambda x: abs(x["correlation"]), reverse=True)

        return {
            "assets": assets,
            "matrix": matrix_list,
            "method": method,
            "top_pairs": pairs[:10],
            "observations": len(clean_returns)
        }

    @staticmethod
    def compute_rolling_correlation(
        series_a: pd.Series,
        series_b: pd.Series,
        window: int = 30
    ) -> List[Dict[str, Any]]:
        """
        Computes rolling correlation between two assets over a specified window.
        """
        df = pd.concat([series_a, series_b], axis=1).dropna()
        if len(df) < window:
            return []

        rolling_corr = df.iloc[:, 0].rolling(window=window).corr(df.iloc[:, 1]).dropna()
        
        results = []
        for date, val in rolling_corr.items():
            results.append({
                "date": str(date)[:10],
                "correlation": round(float(val), 4) if np.isfinite(val) else 0.0
            })
        return results

    @staticmethod
    def compute_asset_beta(
        asset_returns: pd.Series,
        benchmark_returns: pd.Series
    ) -> Dict[str, float]:
        """
        Computes Capital Asset Pricing Model (CAPM) Beta: Cov(Ra, Rb) / Var(Rb).
        """
        df = pd.concat([asset_returns, benchmark_returns], axis=1).dropna()
        if len(df) < 10:
            return {"beta": 1.0, "alpha": 0.0, "r_squared": 0.0}

        y = df.iloc[:, 0].values
        x = df.iloc[:, 1].values

        covariance = np.cov(y, x)[0, 1]
        market_variance = np.var(x)
        beta = float(covariance / market_variance) if market_variance > 0 else 1.0
        
        alpha = float(np.mean(y) - beta * np.mean(x)) * 252 # Annualized alpha
        corr = np.corrcoef(y, x)[0, 1] if market_variance > 0 else 0.0
        r_squared = float(corr ** 2) if np.isfinite(corr) else 0.0

        return {
            "beta": round(beta, 3),
            "annualized_alpha": round(alpha, 4),
            "r_squared": round(r_squared, 4)
        }
