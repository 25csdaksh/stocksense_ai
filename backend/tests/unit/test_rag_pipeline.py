"""
Unit Tests for Complete Financial RAG Pipeline.
Verifies Document Cleaner, Semantic Chunker, Metadata Extraction, Context Builder, and Retrieval Ranking.
"""
import pytest
from app.rag.cleaner import document_cleaner
from app.rag.chunking import financial_chunker
from app.rag.context import rag_context_builder
from app.rag.retrieval import vector_retriever


def test_document_cleaner_removes_artifacts():
    dirty_text = """
    <html><body><p>Item 1A. Risk Factors</p></body></html>
    Page 45 of 120
    Table of Contents
    We operate in highly competitive semiconductor markets &amp; foundry ecosystems.
    """
    cleaned = document_cleaner.clean_text(dirty_text)
    assert "<html>" not in cleaned
    assert "Page 45" not in cleaned
    assert "Table of Contents" not in cleaned
    assert "semiconductor markets" in cleaned


def test_document_cleaner_section_extraction():
    filing_sample = """
    Item 1. Business
    We design accelerated computing platforms for generative AI and supercomputers.
    Item 1A. Risk Factors
    We rely heavily on single-source foundry suppliers for wafer manufacturing.
    Item 7. Management's Discussion
    Revenue grew 200% year-over-year driven by compute datacenter demand.
    """
    sections = document_cleaner.extract_sections(filing_sample)
    assert "Item 1. Business" in sections
    assert "Item 1A. Risk Factors" in sections
    assert "foundry suppliers" in sections["Item 1A. Risk Factors"]


def test_financial_document_chunker():
    sample_text = (
        "NVIDIA Corporation designs graphics processing units and data center accelerators. "
        "The Hopper architecture delivers substantial speedups for large language model inference. "
        "Global demand for accelerated computing has increased across hyperscale cloud providers."
    )
    chunks = financial_chunker.chunk_document(
        text=sample_text,
        ticker="NVDA",
        company_name="NVIDIA Corporation",
        doc_type="10-K",
        fiscal_year=2024,
        section_name="Item 1 Business",
        source_url="https://sec.gov/edgar/nvda-10k"
    )

    assert len(chunks) > 0
    c0 = chunks[0]
    assert c0["ticker"] == "NVDA"
    assert c0["company"] == "NVIDIA Corporation"
    assert c0["document_type"] == "10-K"
    assert c0["fiscal_year"] == 2024
    assert c0["section"] == "Item 1 Business"
    assert "content" in c0
    assert "content_snippet" in c0
    assert c0["page_number"] >= 1


def test_rag_context_builder():
    citations = [
        {
            "id": "sec_nvda_1",
            "ticker": "NVDA",
            "title": "NVIDIA 10-K 2024",
            "section": "Item 1A Risk Factors",
            "page_number": 34,
            "fiscal_year": 2024,
            "content_snippet": "We rely on TSMC foundries for wafer fabrication.",
            "relevance_score": 0.92
        }
    ]
    market_data = {"price": 125.50, "change_pct": 2.5, "week_52_low": 40.0, "week_52_high": 140.0}

    ctx = rag_context_builder.build_context(
        query="What are NVIDIA's manufacturing dependencies?",
        citations=citations,
        market_data=market_data
    )

    assert ctx["evidence_count"] == 1
    assert "[Source 1]" in ctx["formatted_evidence_text"]
    assert "TSMC" in ctx["formatted_evidence_text"]
    assert "$125.50" in ctx["market_summary"]
    assert len(ctx["sources"]) == 1


def test_vector_retriever_metadata_filtering():
    # Filter by ticker AAPL
    aapl_results = vector_retriever.search(query="services margin and app store", ticker="AAPL", top_k=2)
    assert len(aapl_results) > 0
    assert all(r["ticker"] == "AAPL" for r in aapl_results)

    # Filter by ticker NVDA
    nvda_results = vector_retriever.search(query="TSMC foundry wafer allocation", ticker="NVDA", top_k=2)
    assert len(nvda_results) > 0
    assert all(r["ticker"] == "NVDA" for r in nvda_results)
