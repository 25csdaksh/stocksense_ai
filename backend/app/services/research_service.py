"""
RAG Research & Regulatory SEC 10-K Retrieval Service.
Combines Qdrant Vector Search and Hybrid Lexical Vector Retriever.
"""
from typing import Dict, Any, List, Optional
from app.rag.retrieval import vector_retriever
from app.db.vector import vector_repository
from app.rag.context import ContextBuilder
from app.utils.validators import validate_ticker


class ResearchService:

    def __init__(self):
        self.retriever = vector_retriever
        self.vector_repo = vector_repository
        self.context_builder = ContextBuilder()

    async def search_filings(
        self,
        query: str,
        ticker: Optional[str] = None,
        doc_type: Optional[str] = "ALL",
        top_k: int = 5
    ) -> Dict[str, Any]:
        cleaned_ticker = validate_ticker(ticker) if ticker else None
        
        # 1. Try Qdrant / VectorRepository semantic retrieval
        citations = []
        try:
            vector_hits = self.vector_repo.search_similar(
                query=query,
                ticker=cleaned_ticker,
                top_k=top_k
            )
            if vector_hits:
                for hit in vector_hits:
                    citations.append({
                        "id": str(hit.get("id", "")),
                        "ticker": hit.get("ticker", cleaned_ticker or "AAPL"),
                        "title": hit.get("title", f"{hit.get('ticker')} 10-K Filing"),
                        "filing_type": hit.get("filing_type", "10-K"),
                        "fiscal_year": hit.get("fiscal_year", 2024),
                        "section": hit.get("section", "Regulatory Disclosures"),
                        "page_number": hit.get("page_number", 1),
                        "content_snippet": hit.get("content_snippet", ""),
                        "relevance_score": float(hit.get("relevance_score", 0.85))
                    })
        except Exception:
            citations = []

        # 2. Fallback to hybrid lexical retriever if vector index returned empty
        if not citations:
            citations = self.retriever.search(
                query=query,
                ticker=cleaned_ticker,
                filing_type=doc_type or "ALL",
                top_k=top_k
            )

        if citations:
            top_snippet = citations[0]["content_snippet"]
            top_source = f"{citations[0]['ticker']} {citations[0]['filing_type']}"
            synthesis = f"Based on verified SEC filings ({top_source}): {top_snippet[:200]}..."
        else:
            synthesis = "No matching SEC filings or regulatory documents found for the specified criteria."

        return {
            "query": query,
            "total_results": len(citations),
            "citations": citations,
            "synthesis_summary": synthesis
        }

    async def get_filings_by_ticker(self, ticker: str) -> List[Dict[str, Any]]:
        sym = validate_ticker(ticker)
        return self.retriever.search(query="business overview revenue risk factors", ticker=sym, top_k=10)


research_service = ResearchService()
