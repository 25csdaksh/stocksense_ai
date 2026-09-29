"""
Qdrant Vector Integration & Embeddings Unit Tests.
"""
import pytest
from app.db.vector import QdrantClientService, DocumentEmbeddingService, VectorRepository


def test_document_embedding_service():
    embedder = DocumentEmbeddingService()
    text = "NVIDIA manufactures Hopper HGX GPU architectures for generative AI."
    vec = embedder.embed_text(text)

    assert isinstance(vec, list)
    assert len(vec) == 384
    assert any(v != 0 for v in vec)

    batch_vecs = embedder.embed_batch([
        "Apple iPhone and Services revenue",
        "Microsoft Azure cloud computing infrastructure"
    ])
    assert len(batch_vecs) == 2
    assert len(batch_vecs[0]) == 384
    assert len(batch_vecs[1]) == 384


def test_vector_repository_indexing_and_search():
    repo = VectorRepository()
    repo.initialize()

    sample_chunks = [
        {
            "id": "chk_nvda_tsmc_1",
            "ticker": "NVDA",
            "section": "Item 1A Risk Factors",
            "page_number": 34,
            "title": "NVIDIA Form 10-K",
            "content": "We rely heavily on TSMC foundries for wafer fabrication and advanced CoWoS packaging."
        },
        {
            "id": "chk_aapl_services_2",
            "ticker": "AAPL",
            "section": "Item 7 MD&A",
            "page_number": 45,
            "title": "Apple Form 10-K",
            "content": "Services gross margin reached 74% with 2.2 billion active devices worldwide."
        }
    ]

    indexed_count = repo.upsert_chunks(sample_chunks)
    assert indexed_count == 2

    # Query for semiconductor fabrication
    results = repo.search_similar(query="TSMC foundry advanced packaging", ticker="NVDA", top_k=2)
    assert len(results) > 0
    top_hit = results[0]
    assert top_hit["ticker"] == "NVDA"
    assert top_hit["id"] == "chk_nvda_tsmc_1"
    assert "relevance_score" in top_hit
    assert isinstance(top_hit["relevance_score"], (int, float))
    assert -1.0 <= top_hit["relevance_score"] <= 1.0
