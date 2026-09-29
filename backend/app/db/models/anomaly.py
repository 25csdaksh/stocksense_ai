"""
Multivariate Market Anomaly & Outlier ORM Model.
"""
from typing import TYPE_CHECKING
from sqlalchemy import (
    Column, String, Float, Text, DateTime, ForeignKey, JSON, Index
)
from sqlalchemy.orm import relationship
from app.db.base import Base, UUIDPrimaryKeyMixin, TimestampMixin, utc_now

if TYPE_CHECKING:
    from app.db.models.stock import Stock


class Anomaly(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    __tablename__ = "anomalies"

    stock_id = Column(String(36), ForeignKey("stocks.id", ondelete="CASCADE"), nullable=False, index=True)
    ticker = Column(String(10), nullable=False, index=True)
    timestamp = Column(DateTime(timezone=True), default=utc_now, nullable=False, index=True)
    anomaly_type = Column(String(50), nullable=False)  # VOLATILITY_BURST, VOLUME_SPIKE, PRICE_GAP
    severity_score = Column(Float, nullable=False)
    isolation_score = Column(Float, nullable=True)
    summary = Column(Text, nullable=False)
    metrics = Column(JSON, nullable=False)

    __table_args__ = (
        Index("ix_anomalies_ticker_timestamp", "ticker", "timestamp"),
        Index("ix_anomalies_severity", "severity_score"),
    )

    # Relationship
    stock = relationship("Stock", back_populates="anomalies")
