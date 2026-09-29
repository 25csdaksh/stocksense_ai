"""
Regulatory SEC Filings & Semantic RAG Research Chunk Models.
"""
from typing import List, Optional, TYPE_CHECKING
from sqlalchemy import (
    Column, String, Integer, Text, ForeignKey, Index
)
from sqlalchemy.orm import relationship
from app.db.base import Base, UUIDPrimaryKeyMixin, TimestampMixin

if TYPE_CHECKING:
    from app.db.models.company import Company


class ResearchDocument(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    __tablename__ = "research_documents"

    company_id = Column(String(36), ForeignKey("companies.id", ondelete="SET NULL"), nullable=True, index=True)
    ticker = Column(String(10), nullable=False, index=True)
    title = Column(String(255), nullable=False)
    filing_type = Column(String(20), default="10-K", nullable=False)  # 10-K, 10-Q, 8-K
    fiscal_year = Column(Integer, default=2024, nullable=False)
    file_path = Column(String(500), nullable=True)
    total_chunks = Column(Integer, default=0, nullable=False)

    # Relationships
    company = relationship("Company", back_populates="research_documents")
    chunks = relationship("ResearchChunk", back_populates="document", cascade="all, delete-orphan")


class ResearchChunk(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    __tablename__ = "research_chunks"

    document_id = Column(String(36), ForeignKey("research_documents.id", ondelete="CASCADE"), nullable=False, index=True)
    chunk_index = Column(Integer, nullable=False)
    section = Column(String(255), nullable=False)
    page_number = Column(Integer, default=1, nullable=False)
    content = Column(Text, nullable=False)
    vector_id = Column(String(100), nullable=True, index=True)  # Qdrant Point UUID reference
    embedding_model = Column(String(100), default="all-MiniLM-L6-v2", nullable=False)

    __table_args__ = (
        Index("ix_research_chunks_doc_chunk", "document_id", "chunk_index"),
    )

    # Relationship
    document = relationship("ResearchDocument", back_populates="chunks")
