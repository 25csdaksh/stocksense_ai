"""
Stock DNA Peer Clustering and Factor Similarity Search.
"""
from typing import Dict, Any, List
import numpy as np
from sklearn.cluster import KMeans
from sklearn.metrics.pairwise import cosine_similarity


class StockDNAClusterer:
    """
    Groups assets by their 5-factor DNA profiles (Value, Growth, Quality, Momentum, Low Volatility)
    and computes cosine similarity to identify true peer companies.
    """

    def __init__(self, n_clusters: int = 3, random_state: int = 42):
        self.n_clusters = n_clusters
        self.random_state = random_state

    def cluster_universe(
        self,
        dna_profiles: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Clusters a collection of stock DNA profiles and finds nearest peers.
        """
        if len(dna_profiles) < self.n_clusters:
            return {"clusters": {}, "peer_matrix": {}}

        tickers = [p["ticker"] for p in dna_profiles]
        feature_matrix = []
        for p in dna_profiles:
            scores = p["factor_scores"]
            feature_matrix.append([
                scores["value"],
                scores["growth"],
                scores["quality"],
                scores["momentum"],
                scores["low_volatility"]
            ])

        X = np.array(feature_matrix)

        # K-Means clustering
        kmeans = KMeans(n_clusters=self.n_clusters, random_state=self.random_state, n_init=10)
        cluster_labels = kmeans.fit_predict(X)

        # Cosine similarity matrix
        sim_matrix = cosine_similarity(X)

        clusters = {}
        for idx, ticker in enumerate(tickers):
            c_id = int(cluster_labels[idx])
            if c_id not in clusters:
                clusters[c_id] = []
            clusters[c_id].append(ticker)

        # Extract top 3 most similar peers for each ticker
        peer_recommendations = {}
        for i, ticker in enumerate(tickers):
            sim_scores = []
            for j, other_ticker in enumerate(tickers):
                if i != j:
                    sim_scores.append({
                        "ticker": other_ticker,
                        "similarity_score": round(float(sim_matrix[i, j]), 4)
                    })
            sim_scores.sort(key=lambda x: x["similarity_score"], reverse=True)
            peer_recommendations[ticker] = sim_scores[:3]

        return {
            "clusters": clusters,
            "peer_recommendations": peer_recommendations,
            "cluster_centers": kmeans.cluster_centers_.round(1).tolist()
        }
