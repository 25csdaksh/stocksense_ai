"""
Market OHLCV Price History Model (TimescaleDB Hypertable).
"""
from datetime import datetime
from sqlalchemy import Column, String, Numeric, Boolean, DateTime, PrimaryKeyConstraint, Index
from core.database import Base


class MarketOHLCV(Base):
    __tablename__ = "market_ohlcv"

    time = Column(DateTime, nullable=False, primary_key=True)
    ticker = Column(String(16), nullable=False, primary_key=True, index=True)
    open = Column(Numeric(14, 4), nullable=False)
    high = Column(Numeric(14, 4), nullable=False)
    low = Column(Numeric(14, 4), nullable=False)
    close = Column(Numeric(14, 4), nullable=False)
    adjusted_close = Column(Numeric(14, 4), nullable=True)
    volume = Column(Numeric(20, 2), nullable=False)
    vwap = Column(Numeric(14, 4), nullable=True)
    is_synthetic = Column(Boolean, default=False)

    __table_args__ = (
        PrimaryKeyConstraint("time", "ticker"),
        Index("idx_ohlcv_ticker_time", "ticker", "time"),
    )
