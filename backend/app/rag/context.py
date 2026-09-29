"""
RAG Context Builder & Citation Synthesizer.
Formats retrieved regulatory disclosures, financial metadata, and assumptions into structured context for LLM generation.
"""
from typing import List, Dict, Any, Optional


class RAGContextBuilder:
    """Builds grounded prompt contexts from vector search hits and structured market metrics."""

    @staticmethod
    def build_context(
        query: str,
        citations: List[Dict[str, Any]],
        market_data: Optional[Dict[str, Any]] = None,
        fundamentals: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Assembles structured prompt context with explicit source grounding."""
        formatted_evidence = []
        source_records = []

        for idx, cit in enumerate(citations, 1):
            source_id = f"[Source {idx}]"
            title = cit.get("title", f"{cit.get('ticker', 'ASSET')} SEC Disclosure")
            section = cit.get("section", "Item 1A")
            page = cit.get("page_number", 1)
            year = cit.get("fiscal_year", 2024)
            snippet = cit.get("content_snippet", cit.get("content", ""))
            relevance = cit.get("relevance_score", 0.0)

            formatted_evidence.append(
                f"{source_id} {title} | {section} (p. {page}, FY{year}) [Score: {relevance:.2f}]:\n"
                f'"{snippet}"\n'
            )

            source_records.append({
                "source_id": source_id,
                "ticker": cit.get("ticker"),
                "title": title,
                "section": section,
                "page_number": page,
                "fiscal_year": year,
                "relevance_score": relevance,
                "filing_type": cit.get("document_type", cit.get("filing_type", "10-K"))
            })

        evidence_text = "\n".join(formatted_evidence) if formatted_evidence else "No direct regulatory filing matches found."

        market_summary = ""
        if market_data:
            market_summary = (
                f"\nSpot Price: ${market_data.get('price', 0):.2f} "
                f"({market_data.get('change_pct', 0):+.2f}%), "
                f"52-Week Range: ${market_data.get('week_52_low', 0):.2f} - ${market_data.get('week_52_high', 0):.2f}\n"
            )

        context_payload = {
            "query": query,
            "evidence_count": len(citations),
            "formatted_evidence_text": evidence_text,
            "market_summary": market_summary,
            "sources": source_records,
            "grounding_instructions": (
                "Ground all factual statements strictly on the retrieved source excerpts above. "
                "Include bracketed citations (e.g., [Source 1]) for all factual assertions. "
                "If data is missing or uncertain, explicitly state the limitation without hallucinating."
            )
        }

        return context_payload

    @staticmethod
    def build_rag_prompt(query: str, citations: List[Dict[str, Any]]) -> str:
        ctx = RAGContextBuilder.build_context(query, citations)
        return f"User Question: {query}\n\nEvidence:\n{ctx['formatted_evidence_text']}\n\nInstructions: {ctx['grounding_instructions']}"


ContextBuilder = RAGContextBuilder
rag_context_builder = RAGContextBuilder()
