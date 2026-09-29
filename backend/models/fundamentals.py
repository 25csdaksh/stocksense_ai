"""
Company Fundamentals Model.
"""
import uuid
from datetime import datetime, date
from sqlalchemy import Column, String, Numeric, Date, DateTime, UniqueConstraint, ForeignKey
from core.database import Base


class CompanyFundamentals(Base):
    __tablename__ = "company_fundamentals"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    ticker = Column(String(16), ForeignKey("assets.ticker", ondelete="CASCADE"), nullable=False, index=True)
    fiscal_period = Column(String(20), nullable=False)  # e.g., '2024-Q3', '2023-FY'
    period_end_date = Column(Date, nullable=False)
    revenue = Column(Numeric(20, 2), nullable=True)
    gross_profit = Column(Numeric(20, 2), nullable=True)
    operating_income = Column(Numeric(20, 2), nullable=True)
    net_income = Column(Numeric(20, 2), nullable=True)
    free_cash_flow = Column(Numeric(20, 2), nullable=True)
    total_assets = Column(Numeric(20, 2), nullable=True)
    total_liabilities = Column(Numeric(20, 2), nullable=True)
    pe_ratio = Column(Numeric(10, 4), nullable=True)
    pb_ratio = Column(Numeric(10, 4), nullable=True)
    debt_to_equity = Column(Numeric(10, 4), nullable=True)
    roe = Column(Numeric(10, 4), nullable=True)
    roa = Column(Numeric(10, 4), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    __table_args__ = (
        UniqueConstraint("ticker", "fiscal_period", name="uq_ticker_fiscal_period"),
    )
