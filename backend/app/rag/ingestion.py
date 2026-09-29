"""
Document Ingestion, Semantic Chunking & Metadata Tagging.
"""
from typing import List, Dict, Any
import re


class DocumentIngester:
    """Parses regulatory texts and creates chunked document units with metadata."""

    def __init__(self, chunk_size: int = 500, overlap: int = 50):
        self.chunk_size = chunk_size
        self.overlap = overlap

    def chunk_document(
        self,
        text: str,
        ticker: str,
        filing_type: str = "10-K",
        fiscal_year: int = 2024,
        section: str = "Item 1A. Risk Factors",
        start_page: int = 1
    ) -> List[Dict[str, Any]]:
        words = text.split()
        chunks = []
        i = 0
        idx = 0
        while i < len(words):
            chunk_words = words[i:i + self.chunk_size]
            chunk_str = " ".join(chunk_words)
            chunks.append({
                "id": f"{ticker.lower()}_{filing_type.lower()}_{fiscal_year}_{idx}",
                "ticker": ticker.upper(),
                "filing_type": filing_type,
                "fiscal_year": fiscal_year,
                "section": section,
                "page_number": start_page + (idx // 2),
                "content": chunk_str
            })
            idx += 1
            i += (self.chunk_size - self.overlap)
        return chunks
