"""
Integration Tests: Qdrant Vector Embeddings, Point Indexing & Ticker Filtered Search.
"""
import pytest
from app.db.vector import vector_repository, DocumentEmbeddingService


def test_qdrant_vector_embeddings_and_search_integration():
    embedder = DocumentEmbeddingService()
    vec = embedder.embed_text("Blackwell Ultra AI datacenter server deployment")
    assert len(vec) == 384

    # Index sample SEC regulatory chunks
    chunks = [
        {
            "id": "nvda_blackwell_001",
            "ticker": "NVDA",
            "title": "NVIDIA Form 10-K",
            "section": "Item 7 MD&A",
            "page_number": 24,
            "content": "Blackwell architecture delivers accelerated computing for large language models."
        },
        {
            "id": "msft_azure_002",
            "ticker": "MSFT",
            "title": "Microsoft Form 10-K",
            "section": "Item 7 MD&A",
            "page_number": 31,
            "content": "Azure cloud services revenue grew 29% driven by AI copilot infrastructure."
        }
    ]
    indexed = vector_repository.upsert_chunks(chunks)
    assert indexed == 2

    # Query with ticker filter
    nvda_hits = vector_repository.search_similar("accelerated computing LLM", ticker="NVDA", top_k=2)
    assert len(nvda_hits) > 0
    assert nvda_hits[0]["ticker"] == "NVDA"
