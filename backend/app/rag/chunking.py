"""
Semantic Financial Document Chunker.
Splits regulatory filings, annual reports, and research documents into overlapping semantic chunks with rich metadata.
"""
from typing import List, Dict, Any, Optional
import uuid
from app.rag.cleaner import document_cleaner


class FinancialDocumentChunker:
    """Chunks structured regulatory and financial documents preserving section context."""

    def __init__(self, chunk_size: int = 500, chunk_overlap: int = 100):
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap

    def chunk_document(
        self,
        text: str,
        ticker: str,
        company_name: str,
        doc_type: str = "10-K",
        fiscal_year: int = 2024,
        section_name: str = "General",
        source_url: Optional[str] = None,
        filing_date: Optional[str] = "2024-02-15"
    ) -> List[Dict[str, Any]]:
        cleaned_text = document_cleaner.clean_text(text)
        if not cleaned_text:
            return []

        words = cleaned_text.split()
        chunks = []
        start = 0
        chunk_idx = 1

        while start < len(words):
            end = min(start + self.chunk_size, len(words))
            chunk_words = words[start:end]
            chunk_content = " ".join(chunk_words)

            chunk_id = f"chk_{ticker.lower()}_{fiscal_year}_{section_name[:6].lower().replace(' ', '_')}_{chunk_idx}"
            
            chunks.append({
                "id": chunk_id,
                "document_id": f"doc_{ticker.lower()}_{doc_type.lower()}_{fiscal_year}",
                "ticker": ticker.upper(),
                "company": company_name,
                "document_type": doc_type,
                "fiscal_year": fiscal_year,
                "section": section_name,
                "chunk_index": chunk_idx,
                "content": chunk_content,
                "content_snippet": chunk_content[:250] + ("..." if len(chunk_content) > 250 else ""),
                "page_number": max(1, (chunk_idx // 2) + 1),
                "source": source_url or f"SEC EDGAR {doc_type} Filing",
                "filing_date": filing_date
            })

            chunk_idx += 1
            if end == len(words):
                break
            start += (self.chunk_size - self.chunk_overlap)

        return chunks


financial_chunker = FinancialDocumentChunker()
