"""
RAG SEC 10-K Filings & Research Chunks Repository.
"""
from typing import List, Dict, Any, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from app.db.repositories.base import BaseRepository
from app.db.models.research import ResearchDocument, ResearchChunk


class ResearchRepository(BaseRepository[ResearchDocument]):

    def __init__(self, session: AsyncSession):
        super().__init__(ResearchDocument, session)

    async def create_document_with_chunks(
        self,
        ticker: str,
        title: str,
        filing_type: str,
        fiscal_year: int,
        chunks: List[Dict[str, Any]],
        company_id: Optional[str] = None
    ) -> ResearchDocument:
        doc = ResearchDocument(
            ticker=ticker.strip().upper(),
            title=title,
            filing_type=filing_type,
            fiscal_year=fiscal_year,
            company_id=company_id,
            total_chunks=len(chunks)
        )
        self.session.add(doc)
        await self.session.flush()

        for idx, c in enumerate(chunks):
            chunk_obj = ResearchChunk(
                document_id=doc.id,
                chunk_index=idx,
                section=c.get("section", "Section"),
                page_number=c.get("page_number", 1),
                content=c.get("content", ""),
                vector_id=c.get("vector_id"),
                embedding_model=c.get("embedding_model", "all-MiniLM-L6-v2")
            )
            self.session.add(chunk_obj)

        await self.session.flush()
        return doc

    async def get_by_ticker(self, ticker: str) -> List[ResearchDocument]:
        stmt = (
            select(ResearchDocument)
            .where(ResearchDocument.ticker == ticker.strip().upper())
            .options(selectinload(ResearchDocument.chunks))
            .order_by(ResearchDocument.fiscal_year.desc())
        )
        res = await self.session.execute(stmt)
        return list(res.scalars().all())
