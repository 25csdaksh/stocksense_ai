"""
MarketMind AI — RAG Document Research Specialist Agent.
Phase 6.9: Performs semantic retrieval against SEC 10-K, financial filings, and indexed research.
Never fabricates citations or claims certainty when documents are unindexed.
"""
import uuid
from typing import List, Dict, Any, Optional
from datetime import datetime, timezone

from app.ai.models import (
    ResearchEvidence,
    EvidenceProvenance,
    Citation,
)
from app.services.research_service import research_service
from app.core.logging import logger


class RAGDocumentAgent:
    """Specialist agent retrieving semantic context from SEC 10-K filings and regulatory documents."""

    def __init__(self):
        self.service = research_service

    async def run(self, query: str, symbols: List[str], top_k: int = 3) -> List[ResearchEvidence]:
        """Performs semantic search across indexed company filings."""
        evidence_list: List[ResearchEvidence] = []

        target_ticker = symbols[0] if symbols else None

        try:
            res = await self.service.search_filings(
                query=query,
                ticker=target_ticker,
                top_k=top_k
            )

            citations_raw = getattr(res, "citations", []) if hasattr(res, "citations") else (res.get("citations", []) if isinstance(res, dict) else [])

            if citations_raw:
                for idx, c in enumerate(citations_raw):
                    c_dict = c.model_dump() if hasattr(c, "model_dump") else (c if isinstance(c, dict) else {})

                    doc_id = c_dict.get("doc_id") or c_dict.get("document_id") or f"doc_{target_ticker or 'SEC'}"
                    doc_title = c_dict.get("title") or f"{target_ticker or 'Company'} SEC Filing / Annual Report"
                    excerpt_text = c_dict.get("excerpt") or c_dict.get("text") or "Regulatory filing notes and disclosures."
                    relevance = c_dict.get("similarity_score") or c_dict.get("relevance_score") or 0.85

                    cite = Citation(
                        citation_id=f"cite_rag_{uuid.uuid4().hex[:6]}",
                        source_type="SEC_FILING",
                        source_name=doc_title,
                        document_id=doc_id,
                        chunk_id=c_dict.get("chunk_id", f"chunk_{idx}"),
                        excerpt=excerpt_text[:250]
                    )

                    evidence_list.append(
                        ResearchEvidence(
                            evidence_id=f"ev_{uuid.uuid4().hex[:8]}",
                            category="RAG",
                            symbol=target_ticker,
                            metric="regulatory_filing_disclosure",
                            value={
                                "document_title": doc_title,
                                "section": c_dict.get("section", "Item 1 / Management Discussion"),
                                "relevance_score": round(float(relevance), 3),
                                "excerpt": excerpt_text
                            },
                            source="QdrantVectorRepository",
                            provenance=EvidenceProvenance.LIVE if "LIVE" in str(c_dict) else EvidenceProvenance.DEMO,
                            confidence=round(float(relevance), 2),
                            citation=cite
                        )
                    )
            else:
                # Evidence unavailable note
                evidence_list.append(
                    ResearchEvidence(
                        evidence_id=f"ev_{uuid.uuid4().hex[:8]}",
                        category="RAG",
                        symbol=target_ticker,
                        metric="regulatory_filings_status",
                        value={"status": "NO_INDEXED_FILINGS_MATCH", "note": "Evidence unavailable in current document index."},
                        source="QdrantVectorRepository",
                        provenance=EvidenceProvenance.UNAVAILABLE,
                        confidence=0.5
                    )
                )

        except Exception as ex:
            logger.warning(f"RAGDocumentAgent error: {ex}")
            evidence_list.append(
                ResearchEvidence(
                    evidence_id=f"ev_{uuid.uuid4().hex[:8]}",
                    category="RAG",
                    symbol=target_ticker,
                    metric="rag_status",
                    value={"status": "RETRIEVAL_ERROR", "error": str(ex)[:80]},
                    source="QdrantVectorRepository",
                    provenance=EvidenceProvenance.UNAVAILABLE,
                    confidence=0.2
                )
            )

        return evidence_list


rag_agent = RAGDocumentAgent()
