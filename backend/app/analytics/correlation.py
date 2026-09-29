"""
Correlation Dynamics, Granger Causality & Market Contagion Network Graph.
"""
from typing import Dict, List, Any, Optional
import numpy as np
import pandas as pd
import networkx as nx
from statsmodels.tsa.stattools import grangercausalitytests


class RollingCorrelationEngine:
    """Computes pairwise multi-asset correlation matrices and CAPM betas."""

    @staticmethod
    def compute_matrix(returns_df: pd.DataFrame, method: str = "pearson") -> Dict[str, Any]:
        clean = returns_df.dropna()
        if clean.empty or clean.shape[1] < 2:
            cols = list(returns_df.columns)
            return {
                "assets": cols,
                "matrix": np.eye(len(cols)).tolist(),
                "method": method,
                "top_pairs": []
            }

        corr = clean.corr(method=method).round(4)
        assets = list(corr.columns)
        matrix_list = [row.tolist() for _, row in corr.iterrows()]

        pairs = []
        for i in range(len(assets)):
            for j in range(i + 1, len(assets)):
                pairs.append({
                    "asset_a": assets[i],
                    "asset_b": assets[j],
                    "correlation": float(corr.iloc[i, j])
                })
        pairs.sort(key=lambda x: abs(x["correlation"]), reverse=True)

        return {
            "assets": assets,
            "matrix": matrix_list,
            "method": method,
            "top_pairs": pairs[:10],
            "observations": len(clean)
        }

    @staticmethod
    def compute_beta(asset_returns: pd.Series, benchmark_returns: pd.Series) -> Dict[str, float]:
        df = pd.concat([asset_returns, benchmark_returns], axis=1).dropna()
        if len(df) < 10:
            return {"beta": 1.0, "alpha": 0.0, "r_squared": 0.0}
        y = df.iloc[:, 0].values
        x = df.iloc[:, 1].values
        var_x = np.var(x)
        beta = float(np.cov(y, x)[0, 1] / var_x) if var_x > 0 else 1.0
        alpha = float(np.mean(y) - beta * np.mean(x)) * 252.0
        r_sq = float((np.corrcoef(y, x)[0, 1] ** 2)) if var_x > 0 else 0.0

        return {
            "beta": round(beta, 3),
            "alpha": round(alpha, 4),
            "r_squared": round(r_sq, 4)
        }


class GrangerCausalityAnalyzer:
    """Tests econometric lead-lag causal forecasting using Vector Autoregression."""

    def __init__(self, max_lag: int = 5):
        self.max_lag = max_lag

    def test(self, cause_series: pd.Series, effect_series: pd.Series, cause_name: str = "X", effect_name: str = "Y") -> Dict[str, Any]:
        df = pd.concat([effect_series, cause_series], axis=1).dropna()
        if len(df) < (self.max_lag * 3 + 10):
            return {
                "cause": cause_name,
                "effect": effect_name,
                "is_causal": False,
                "min_p_value": 1.0,
                "optimal_lag": 1,
                "summary": "Insufficient sample size to infer causality."
            }

        try:
            results = grangercausalitytests(df.values, maxlag=self.max_lag, verbose=False)
            p_vals = {lag: float(res[0]["ssr_ftest"][1]) for lag, res in results.items()}
            f_stats = {lag: float(res[0]["ssr_ftest"][0]) for lag, res in results.items()}
            best_lag = min(p_vals, key=p_vals.get)
            min_p = p_vals[best_lag]
            is_sig = min_p < 0.05

            summary = (
                f"{cause_name} significantly Granger-causes {effect_name} at lag {best_lag} days (p={min_p:.4f})"
                if is_sig else f"No significant predictive lead from {cause_name} to {effect_name} (p={min_p:.4f})"
            )

            return {
                "cause": cause_name,
                "effect": effect_name,
                "is_causal": bool(is_sig),
                "min_p_value": round(float(min_p), 4),
                "optimal_lag": int(best_lag),
                "f_statistic": round(float(f_stats[best_lag]), 2),
                "summary": summary
            }
        except Exception as err:
            return {
                "cause": cause_name,
                "effect": effect_name,
                "is_causal": False,
                "min_p_value": 1.0,
                "optimal_lag": 1,
                "summary": f"Granger test exception: {str(err)}"
            }


class MarketRelationshipGraph:
    """Constructs systemic contagion network graph using NetworkX."""

    def __init__(self, threshold: float = 0.45):
        self.threshold = threshold

    def build_graph(self, returns_df: pd.DataFrame, metadata: Dict[str, Dict[str, Any]]) -> Dict[str, Any]:
        assets = list(returns_df.columns)
        if len(assets) < 2:
            return {"nodes": [], "edges": [], "network_metrics": {}}

        clean = returns_df.dropna()
        corr = clean.corr().fillna(0)
        G = nx.Graph()

        for a in assets:
            meta = metadata.get(a, {})
            vol = float(clean[a].std() * np.sqrt(252) * 100.0) if a in clean else 20.0
            G.add_node(a, label=a, name=meta.get("name", a), sector=meta.get("sector", "General"), vol=round(vol, 2))

        for i in range(len(assets)):
            for j in range(i + 1, len(assets)):
                a, b = assets[i], assets[j]
                r = float(corr.loc[a, b])
                if abs(r) >= self.threshold:
                    G.add_edge(a, b, weight=round(abs(r), 4), correlation=round(r, 4))

        try:
            eigen = nx.eigenvector_centrality_numpy(G, weight="weight")
        except Exception:
            eigen = {n: 1.0 / len(assets) for n in assets}

        try:
            betweenness = nx.betweenness_centrality(G, weight="weight")
        except Exception:
            betweenness = {n: 0.0 for n in assets}

        nodes = []
        for n in G.nodes():
            nd = G.nodes[n]
            nodes.append({
                "id": n,
                "label": nd.get("label", n),
                "name": nd.get("name", n),
                "sector": nd.get("sector", "General"),
                "degree": G.degree(n),
                "eigenvector_centrality": round(float(eigen.get(n, 0)), 4),
                "betweenness_centrality": round(float(betweenness.get(n, 0)), 4),
                "annualized_volatility": nd.get("vol", 20.0)
            })

        edges = []
        for u, v, data in G.edges(data=True):
            edges.append({
                "source": u,
                "target": v,
                "weight": data.get("weight", 0.5),
                "correlation": data.get("correlation", 0.5),
                "edge_type": "POSITIVE" if data.get("correlation", 0) > 0 else "NEGATIVE"
            })

        most_systemic = max(nodes, key=lambda x: x["eigenvector_centrality"])["id"] if nodes else "N/A"

        return {
            "nodes": nodes,
            "edges": edges,
            "network_metrics": {
                "total_nodes": G.number_of_nodes(),
                "total_edges": G.number_of_edges(),
                "graph_density": round(float(nx.density(G)), 4),
                "most_systemic_node": most_systemic,
                "correlation_threshold_applied": self.threshold
            }
        }


class CorrelationEngine:
    """Convenience wrapper for calculating cross-asset rolling correlations."""

    @staticmethod
    async def compute_matrix(method: str = "pearson") -> Dict[str, Any]:
        from app.services.analytics_service import analytics_service
        return await analytics_service.get_correlation_matrix(method=method)
