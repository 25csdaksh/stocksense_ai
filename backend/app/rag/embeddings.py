"""
Dense Vector Embedding Engine Interface.
"""
from typing import List
import numpy as np


class EmbeddingModel:
    """Generates normalized dense vector representations for queries and document chunks."""

    def __init__(self, dimension: int = 384):
        self.dimension = dimension

    def embed_text(self, text: str) -> List[float]:
        """Generates deterministic pseudo-dense embedding vector with unit norm."""
        np.random.seed(abs(hash(text)) % 100000)
        vec = np.random.normal(0, 1, self.dimension)
        norm = np.linalg.norm(vec)
        if norm > 0:
            vec = vec / norm
        return vec.tolist()

    def embed_documents(self, docs: List[str]) -> List[List[float]]:
        return [self.embed_text(d) for d in docs]


embedding_model = EmbeddingModel()
