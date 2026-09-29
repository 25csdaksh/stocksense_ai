"""
Qdrant Vector Database Integration & Document Embeddings Service.
Features graceful in-memory fallback if Qdrant server is offline.
"""
from typing import List, Dict, Any, Optional
import numpy as np
from app.core.config import settings
from app.core.logging import logger
from app.rag.embeddings import embedding_model

try:
    from qdrant_client import QdrantClient
    from qdrant_client.models import Distance, VectorParams, PointStruct, Filter, FieldCondition, MatchValue
except ImportError:
    QdrantClient = None


class QdrantClientService:
    """Manages Qdrant vector database connection pool and collection lifecycle."""

    def __init__(self):
        self.client: Optional[Any] = None
        self.is_connected: bool = False
        self.collection_name = settings.QDRANT_COLLECTION_NAME
        self.vector_size = 384  # standard for all-MiniLM-L6-v2 embeddings

    def connect(self):
        if QdrantClient is None:
            logger.info("qdrant-client not installed. Using in-memory vector index.")
            return

        try:
            self.client = QdrantClient(
                host=settings.QDRANT_HOST,
                port=settings.QDRANT_PORT,
                api_key=settings.QDRANT_API_KEY if settings.QDRANT_API_KEY else None,
                timeout=2.0
            )
            # Test connection
            self.client.get_collections()
            self.is_connected = True
            logger.info(f"Connected to Qdrant vector database at {settings.QDRANT_HOST}:{settings.QDRANT_PORT}")
            self._ensure_collection()
        except Exception as err:
            logger.warning(f"Qdrant vector database offline ({err}). In-memory vector index will be used.")
            self.client = None
            self.is_connected = False

    def _ensure_collection(self):
        if not self.is_connected or not self.client:
            return
        try:
            collections = [c.name for c in self.client.get_collections().collections]
            if self.collection_name not in collections:
                self.client.create_collection(
                    collection_name=self.collection_name,
                    vectors_config=VectorParams(size=self.vector_size, distance=Distance.COSINE)
                )
                logger.info(f"Created Qdrant collection '{self.collection_name}' (size={self.vector_size}, distance=COSINE).")
        except Exception as err:
            logger.warning(f"Failed to ensure Qdrant collection: {err}")


class DocumentEmbeddingService:
    """Generates dense vector embeddings for financial texts and SEC 10-K sections."""

    def __init__(self):
        self.model = embedding_model

    def embed_text(self, text: str) -> List[float]:
        return self.model.embed_query(text)

    def embed_batch(self, texts: List[str]) -> List[List[float]]:
        return self.model.embed_documents(texts)


class VectorRepository:
    """Repository for indexing and searching regulatory SEC document vectors."""

    def __init__(self):
        self.qdrant_service = QdrantClientService()
        self.embedding_service = DocumentEmbeddingService()
        self._in_memory_vectors: List[Dict[str, Any]] = []

    def initialize(self):
        self.qdrant_service.connect()

    def upsert_chunks(self, chunks: List[Dict[str, Any]]) -> int:
        """
        Embeds and indexes document chunks.
        chunks schema: [{'id': str, 'content': str, 'ticker': str, 'section': str, ...}]
        """
        if not chunks:
            return 0

        texts = [c["content"] for c in chunks]
        vectors = self.embedding_service.embed_batch(texts)

        if self.qdrant_service.is_connected and self.qdrant_service.client:
            try:
                points = [
                    PointStruct(
                        id=c["id"],
                        vector=vectors[i],
                        payload={
                            "ticker": c.get("ticker", "AAPL"),
                            "section": c.get("section", ""),
                            "page_number": c.get("page_number", 1),
                            "content_snippet": c["content"][:300],
                            "title": c.get("title", ""),
                            "fiscal_year": c.get("fiscal_year", 2024)
                        }
                    )
                    for i, c in enumerate(chunks)
                ]
                self.qdrant_service.client.upsert(
                    collection_name=self.qdrant_service.collection_name,
                    points=points
                )
                return len(points)
            except Exception as err:
                logger.warning(f"Qdrant upsert failed ({err}), falling back to in-memory store.")

        # Fallback in-memory indexing
        for i, c in enumerate(chunks):
            self._in_memory_vectors.append({
                "id": c["id"],
                "vector": vectors[i],
                "payload": {
                    "ticker": c.get("ticker", "AAPL"),
                    "section": c.get("section", ""),
                    "page_number": c.get("page_number", 1),
                    "content_snippet": c["content"],
                    "title": c.get("title", ""),
                    "fiscal_year": c.get("fiscal_year", 2024)
                }
            })
        return len(chunks)

    def search_similar(
        self,
        query: str,
        ticker: Optional[str] = None,
        top_k: int = 5
    ) -> List[Dict[str, Any]]:
        query_vector = self.embedding_service.embed_text(query)

        if self.qdrant_service.is_connected and self.qdrant_service.client:
            try:
                query_filter = None
                if ticker:
                    query_filter = Filter(
                        must=[FieldCondition(key="ticker", match=MatchValue(value=ticker.upper()))]
                    )

                results = self.qdrant_service.client.search(
                    collection_name=self.qdrant_service.collection_name,
                    query_vector=query_vector,
                    query_filter=query_filter,
                    limit=top_k
                )

                return [
                    {
                        "id": r.id,
                        "relevance_score": round(float(r.score), 4),
                        **r.payload
                    }
                    for r in results
                ]
            except Exception as err:
                logger.warning(f"Qdrant search failed ({err}), using in-memory vector cosine similarity.")

        # In-memory cosine search fallback
        candidates = self._in_memory_vectors
        if ticker:
            candidates = [c for c in candidates if c["payload"].get("ticker") == ticker.upper()]

        if not candidates:
            return []

        q_vec = np.array(query_vector)
        q_norm = np.linalg.norm(q_vec) + 1e-9

        scored = []
        for c in candidates:
            c_vec = np.array(c["vector"])
            c_norm = np.linalg.norm(c_vec) + 1e-9
            cos_sim = float(np.dot(q_vec, c_vec) / (q_norm * c_norm))
            scored.append({
                "id": c["id"],
                "relevance_score": round(cos_sim, 4),
                **c["payload"]
            })

        scored.sort(key=lambda x: x["relevance_score"], reverse=True)
        return scored[:top_k]


vector_repository = VectorRepository()
