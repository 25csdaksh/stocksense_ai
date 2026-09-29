"""
Sector & Company Directory ORM Models.
"""
from typing import List, Optional, TYPE_CHECKING
from sqlalchemy import Column, String, Float, Text, ForeignKey
from sqlalchemy.orm import relationship
from app.db.base import Base, UUIDPrimaryKeyMixin, TimestampMixin

if TYPE_CHECKING:
    from app.db.models.stock import Stock
    from app.db.models.fundamental import Fundamental, FinancialStatement
    from app.db.models.news import News
    from app.db.models.research import ResearchDocument


class Sector(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    __tablename__ = "sectors"

    name = Column(String(100), unique=True, index=True, nullable=False)
    code = Column(String(20), unique=True, index=True, nullable=False)
    description = Column(Text, nullable=True)
    performance_pct = Column(Float, default=0.0, nullable=False)
    momentum_score = Column(Float, default=50.0, nullable=False)
    market_cap_weight = Column(Float, default=0.0, nullable=False)

    # Relationships
    companies = relationship("Company", back_populates="sector", cascade="all, delete-orphan")


class Company(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    __tablename__ = "companies"

    sector_id = Column(String(36), ForeignKey("sectors.id", ondelete="CASCADE"), nullable=False, index=True)
    name = Column(String(150), nullable=False)
    ticker = Column(String(10), unique=True, index=True, nullable=False)
    cik = Column(String(20), nullable=True)
    description = Column(Text, nullable=True)
    country = Column(String(50), default="US", nullable=False)
    website = Column(String(255), nullable=True)

    # Relationships
    sector = relationship("Sector", back_populates="companies")
    stocks = relationship("Stock", back_populates="company", cascade="all, delete-orphan")
    fundamentals = relationship("Fundamental", back_populates="company", cascade="all, delete-orphan")
    financial_statements = relationship("FinancialStatement", back_populates="company", cascade="all, delete-orphan")
    news_articles = relationship("News", back_populates="company")
    research_documents = relationship("ResearchDocument", back_populates="company")
