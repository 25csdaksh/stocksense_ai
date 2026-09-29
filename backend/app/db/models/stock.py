"""
Stock Asset, TimescaleDB OHLCV Hypertable & Market Index ORM Models.
"""
from typing import List, Optional, TYPE_CHECKING
from sqlalchemy import (
    Column, String, Float, DateTime, ForeignKey, Index, BigInteger
)
from sqlalchemy.orm import relationship
from app.db.base import Base, UUIDPrimaryKeyMixin, TimestampMixin, utc_now

if TYPE_CHECKING:
    from app.db.models.company import Company
    from app.db.models.anomaly import Anomaly
    from app.db.models.scenario import ScenarioReport


class Stock(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    __tablename__ = "stocks"

    company_id = Column(String(36), ForeignKey("companies.id", ondelete="CASCADE"), nullable=False, index=True)
    ticker = Column(String(10), unique=True, index=True, nullable=False)
    exchange = Column(String(50), default="NASDAQ", nullable=False)
    asset_class = Column(String(50), default="EQUITY", nullable=False)
    beta = Column(Float, default=1.0, nullable=False)
    pe_ratio = Column(Float, nullable=True)
    pb_ratio = Column(Float, nullable=True)
    dividend_yield = Column(Float, nullable=True)
    market_cap = Column(Float, nullable=True)
    week_52_high = Column(Float, nullable=True)
    week_52_low = Column(Float, nullable=True)

    # Relationships
    company = relationship("Company", back_populates="stocks")
    ohlcv_bars = relationship("StockOHLCV", back_populates="stock", cascade="all, delete-orphan")
    anomalies = relationship("Anomaly", back_populates="stock", cascade="all, delete-orphan")
    scenario_reports = relationship("ScenarioReport", back_populates="stock")


class StockOHLCV(Base, UUIDPrimaryKeyMixin):
    """
    TimescaleDB Hypertable Target for High-Throughput Candlestick Storage.
    Indexed by stock_id, ticker, and timestamp.
    """
    __tablename__ = "stock_ohlcv"

    stock_id = Column(String(36), ForeignKey("stocks.id", ondelete="CASCADE"), nullable=False, index=True)
    ticker = Column(String(10), nullable=False, index=True)
    timestamp = Column(DateTime(timezone=True), nullable=False, index=True)
    open = Column(Float, nullable=False)
    high = Column(Float, nullable=False)
    low = Column(Float, nullable=False)
    close = Column(Float, nullable=False)
    adjusted_close = Column(Float, nullable=True)
    volume = Column(Float, nullable=False)
    interval = Column(String(10), default="1d", nullable=False)

    # Composite indexes for fast time-range filtering
    __table_args__ = (
        Index("ix_stock_ohlcv_stock_timestamp", "stock_id", "timestamp"),
        Index("ix_stock_ohlcv_ticker_timestamp", "ticker", "timestamp"),
    )

    # Relationship
    stock = relationship("Stock", back_populates="ohlcv_bars")


class MarketIndex(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    __tablename__ = "market_indices"

    symbol = Column(String(20), unique=True, index=True, nullable=False)
    name = Column(String(100), nullable=False)
    price = Column(Float, nullable=False)
    change = Column(Float, nullable=False)
    change_pct = Column(Float, nullable=False)
    timestamp = Column(DateTime(timezone=True), default=utc_now, nullable=False)
