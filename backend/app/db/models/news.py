"""
Financial News & Real-Time Sentiment ORM Model.
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
    ticker = Column(String(10), nullable=True, index=True)
    title = Column(String(255), nullable=False)
    summary = Column(Text, nullable=False)
    source = Column(String(100), nullable=False)
    url = Column(String(500), nullable=True)
    published_at = Column(DateTime(timezone=True), default=utc_now, nullable=False, index=True)
    sentiment_label = Column(String(20), default="NEUTRAL", nullable=False)  # BULLISH, BEARISH, NEUTRAL
    sentiment_score = Column(Float, default=0.0, nullable=False)
    impact_score = Column(Float, default=0.5, nullable=False)

    __table_args__ = (
        Index("ix_news_ticker_published", "ticker", "published_at"),
    )

    # Relationship
    company = relationship("Company", back_populates="news_articles")
