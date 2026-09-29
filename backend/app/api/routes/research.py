"""
RAG SEC 10-K Research & Vector Retrieval API Routes.
"""
from typing import List, Dict, Any
from fastapi import APIRouter
from app.schemas.research import DocumentSearchRequest, DocumentSearchResponse, CitationItem
from app.services.research_service import research_service

router = APIRouter(prefix="/research", tags=["RAG Document Intelligence"])


@router.post("/query", response_model=DocumentSearchResponse)
async def query_regulatory_documents(req: DocumentSearchRequest):
    """Executes semantic and lexical retrieval against indexed SEC 10-K filings with source citations."""
    return await research_service.search_filings(
        query=req.query,
        ticker=req.ticker,
        doc_type=req.doc_type,
        top_k=req.top_k
    )


@router.get("/filings/{symbol}", response_model=List[CitationItem])
async def get_ticker_filings(symbol: str):
    """Retrieves all indexed regulatory filing sections for a specific company ticker."""
    return await research_service.get_filings_by_ticker(symbol)
