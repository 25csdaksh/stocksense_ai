"""
RAG Research, SEC 10-K Search & Document Citation Schemas.
"""
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field


class DocumentSearchRequest(BaseModel):
    query: str = Field(..., min_length=2)
    ticker: Optional[str] = None
    doc_type: Optional[str] = Field(default="ALL")
    top_k: int = Field(default=5, ge=1, le=20)


class CitationItem(BaseModel):
    id: str
    ticker: str
    title: str
    filing_type: str
    fiscal_year: int
    section: str
    page_number: int
    content_snippet: str
    relevance_score: float


class DocumentSearchResponse(BaseModel):
    query: str
    total_results: int
    citations: List[CitationItem]
    synthesis_summary: str
