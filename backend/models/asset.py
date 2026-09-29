"""
Asset ORM Model.
"""
import uuid
from datetime import datetime
from sqlalchemy import Column, String, Numeric, Boolean, DateTime
from sqlalchemy.dialects.postgresql import UUID
from core.database import Base


class Asset(Base):
    __tablename__ = "assets"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    ticker = Column(String(16), unique=True, nullable=False, index=True)
    name = Column(String(255), nullable=False)
    sector = Column(String(100), nullable=True)
    industry = Column(String(100), nullable=True)
    asset_type = Column(String(50), default="EQUITY")
    market_cap = Column(Numeric(20, 2), nullable=True)
    currency = Column(String(10), default="USD")
    beta = Column(Numeric(6, 4), default=1.0)
    pe_ratio = Column(Numeric(10, 4), nullable=True)
    pb_ratio = Column(Numeric(10, 4), nullable=True)
    dividend_yield = Column(Numeric(6, 4), default=0.0)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
