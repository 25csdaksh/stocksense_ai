"""
Financial News & Real-Time Sentiment ORM Model.
Phase 6.7: Enhanced ORM model supporting multi-market news, event classifications,
categories, impact parameters, provenance, and deduplication hashes.
"""
from typing import Optional, TYPE_CHECKING
from sqlalchemy import (
    Column, String, Float, Text, DateTime, ForeignKey, Index
)
from sqlalchemy.orm import relationship
from app.db.base import Base, UUIDPrimaryKeyMixin, TimestampMixin, utc_now

if TYPE_CHECKING:
    from app.db.models.company import Company


class News(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    __tablename__ = "news"

    company_id = Column(String(36), ForeignKey("companies.id", ondelete="SET NULL"), nullable=True, index=True)
    ticker = Column(String(20), nullable=True, index=True)
    title = Column(String(255), nullable=False)
    summary = Column(Text, nullable=False)
    source = Column(String(100), nullable=False)
    url = Column(String(500), nullable=True)
    published_at = Column(DateTime(timezone=True), default=utc_now, nullable=False, index=True)
    sentiment_label = Column(String(20), default="NEUTRAL", nullable=False)  # BULLISH, BEARISH, NEUTRAL, POSITIVE, NEGATIVE
    sentiment_score = Column(Float, default=0.0, nullable=False)
    impact_score = Column(Float, default=0.5, nullable=False)

    # Phase 6.7 Extensions
    category = Column(String(50), default="MARKET", nullable=True, index=True)
    event_type = Column(String(50), default="OTHER", nullable=True, index=True)
    impact_direction = Column(String(20), default="NEUTRAL", nullable=True)
    impact_horizon = Column(String(20), default="SHORT_TERM", nullable=True)
    impact_scope = Column(String(20), default="STOCK", nullable=True)
    relevance_score = Column(Float, default=0.8, nullable=True)
    data_source = Column(String(50), default="DEMO", nullable=True)
    data_status = Column(String(20), default="DEMO", nullable=True)
    content_hash = Column(String(64), nullable=True, index=True)
    sector = Column(String(100), nullable=True, index=True)

    __table_args__ = (
        Index("ix_news_ticker_published", "ticker", "published_at"),
        Index("ix_news_sector_published", "sector", "published_at"),
        Index("ix_news_category_published", "category", "published_at"),
    )

    # Relationship
    company = relationship("Company", back_populates="news_articles")
