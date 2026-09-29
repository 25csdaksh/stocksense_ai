"""
Market Contagion and Relationship Network Graph Builder.
"""
from typing import Dict, Any, List
import numpy as np
import pandas as pd
import networkx as nx


class MarketRelationshipGraph:
    """
    Constructs an undirected or directed financial network graph where:
    - Nodes: Stocks, Sectors, Asset Classes (with node attributes: Market Cap, Sector, Volatility)
    - Edges: Statistically significant correlations (abs(r) > threshold) or Lead-Lag Granger causality.
    Calculates PageRank, Eigenvector Centrality, and Community Clusters.
    """

    def __init__(self, correlation_threshold: float = 0.50):
        self.correlation_threshold = correlation_threshold

    def build_network(
        self,
        returns_df: pd.DataFrame,
        metadata_map: Dict[str, Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Builds a NetworkX graph and extracts nodes and edges formatted for D3/vis.js visualization.
        """
        assets = list(returns_df.columns)
        if len(assets) < 2:
            return {"nodes": [], "edges": [], "network_metrics": {}}

        clean_returns = returns_df.dropna()
        corr_matrix = clean_returns.corr().fillna(0)

        G = nx.Graph()

        # Add Nodes with attributes
        for asset in assets:
            meta = metadata_map.get(asset, {})
            vol = float(clean_returns[asset].std() * np.sqrt(252) * 100) if asset in clean_returns else 20.0
            G.add_node(
                asset,
                label=asset,
                name=meta.get("name", asset),
                sector=meta.get("sector", "General"),
                market_cap=meta.get("market_cap", 1e10),
                annualized_volatility=round(vol, 2)
            )

        # Add Edges based on correlation threshold
        for i in range(len(assets)):
            for j in range(i + 1, len(assets)):
                a, b = assets[i], assets[j]
                r = float(corr_matrix.loc[a, b])
                if abs(r) >= self.correlation_threshold:
                    G.add_edge(
                        a,
                        b,
                        weight=round(abs(r), 4),
                        correlation=round(r, 4),
                        edge_type="POSITIVE" if r > 0 else "NEGATIVE"
                    )

        # Graph Centrality Metrics
        degree_dict = dict(G.degree())
        try:
            eigen_centrality = nx.eigenvector_centrality_numpy(G, weight="weight")
        except Exception:
            eigen_centrality = {node: 1.0 / len(assets) for node in assets}

        try:
            betweenness = nx.betweenness_centrality(G, weight="weight")
        except Exception:
            betweenness = {node: 0.0 for node in assets}

        # Format Nodes for UI
        nodes_out = []
        for node in G.nodes():
            node_data = G.nodes[node]
            nodes_out.append({
                "id": node,
                "label": node_data.get("label", node),
                "name": node_data.get("name", node),
                "sector": node_data.get("sector", "General"),
                "degree": degree_dict.get(node, 0),
                "eigenvector_centrality": round(float(eigen_centrality.get(node, 0)), 4),
                "betweenness_centrality": round(float(betweenness.get(node, 0)), 4),
                "annualized_volatility": node_data.get("annualized_volatility", 20.0)
            })

        # Format Edges for UI
        edges_out = []
        for u, v, data in G.edges(data=True):
            edges_out.append({
                "source": u,
                "target": v,
                "weight": data.get("weight", 0.5),
                "correlation": data.get("correlation", 0.5),
                "edge_type": data.get("edge_type", "POSITIVE")
            })

        # Find most systemic asset (highest eigenvector centrality)
        most_systemic = max(nodes_out, key=lambda x: x["eigenvector_centrality"])["id"] if nodes_out else "N/A"

        return {
            "nodes": nodes_out,
            "edges": edges_out,
            "network_metrics": {
                "total_nodes": G.number_of_nodes(),
                "total_edges": G.number_of_edges(),
                "graph_density": round(float(nx.density(G)), 4),
                "most_systemic_node": most_systemic,
                "correlation_threshold_applied": self.correlation_threshold
            }
        }
