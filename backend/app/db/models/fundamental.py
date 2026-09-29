"""
Company Fundamentals & Normalized Multi-Period Financial Statements Models.
"""
from typing import Optional, TYPE_CHECKING
from sqlalchemy import (
    Column, String, Float, Integer, DateTime, ForeignKey, JSON, Index
)
from sqlalchemy.orm import relationship
from app.db.base import Base, UUIDPrimaryKeyMixin, TimestampMixin, utc_now

if TYPE_CHECKING:
    from app.db.models.company import Company


class Fundamental(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    __tablename__ = "fundamentals"

    company_id = Column(String(36), ForeignKey("companies.id", ondelete="CASCADE"), nullable=False, index=True)
    fiscal_year = Column(Integer, nullable=False)
    fiscal_quarter = Column(Integer, nullable=True)

    # Valuation Multiples
    pe_ratio = Column(Float, nullable=True)
    forward_pe = Column(Float, nullable=True)
    pb_ratio = Column(Float, nullable=True)
    ev_ebitda = Column(Float, nullable=True)
    fcf_yield_pct = Column(Float, nullable=True)

    # Margins & Profitability
    gross_margin_pct = Column(Float, nullable=True)
    operating_margin_pct = Column(Float, nullable=True)
    net_margin_pct = Column(Float, nullable=True)
    roe_pct = Column(Float, nullable=True)
    roa_pct = Column(Float, nullable=True)

    # Financial Health & Leverage
    current_ratio = Column(Float, nullable=True)
    debt_to_equity = Column(Float, nullable=True)
    interest_coverage_ratio = Column(Float, nullable=True)
    altman_z_score = Column(Float, nullable=True)
    health_score = Column(String(20), default="HEALTHY", nullable=False)

    __table_args__ = (
        Index("ix_fundamentals_company_year", "company_id", "fiscal_year"),
    )

    # Relationship
    company = relationship("Company", back_populates="fundamentals")


class FinancialStatement(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    __tablename__ = "financial_statements"

    company_id = Column(String(36), ForeignKey("companies.id", ondelete="CASCADE"), nullable=False, index=True)
    statement_type = Column(String(30), nullable=False)  # income, balance_sheet, cash_flow
    fiscal_year = Column(Integer, nullable=False)
    fiscal_period = Column(String(10), default="FY", nullable=False)  # FY, Q1, Q2, Q3, Q4
    reported_date = Column(DateTime(timezone=True), default=utc_now, nullable=False)
    raw_data = Column(JSON, nullable=False)  # Flexible JSON/JSONB payload for line items

    __table_args__ = (
        Index("ix_financial_statements_comp_type_year", "company_id", "statement_type", "fiscal_year"),
    )

    # Relationship
    company = relationship("Company", back_populates="financial_statements")
