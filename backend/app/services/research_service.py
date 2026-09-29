"""
RAG Research & Regulatory SEC 10-K Retrieval Service.
"""
from typing import Dict, Any, List, Optional
from app.rag.retrieval import vector_retriever
from app.rag.context import ContextBuilder
from app.utils.validators import validate_ticker


class ResearchService:

    def __init__(self):
        self.retriever = vector_retriever
        self.context_builder = ContextBuilder()

    async def search_filings(
        self,
        query: str,
        ticker: Optional[str] = None,
        doc_type: Optional[str] = "ALL",
        top_k: int = 5
    ) -> Dict[str, Any]:
        cleaned_ticker = validate_ticker(ticker) if ticker else None
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
