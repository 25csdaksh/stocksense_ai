"""
User Portfolio, Position, Transaction & Watchlist ORM Models.
"""
from typing import List, Optional, TYPE_CHECKING
from sqlalchemy import (
    Column, String, Float, DateTime, ForeignKey, UniqueConstraint, Index, Text
)
from sqlalchemy.orm import relationship
from app.db.base import Base, UUIDPrimaryKeyMixin, TimestampMixin, utc_now

if TYPE_CHECKING:
    from app.db.models.user import User


class Portfolio(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    __tablename__ = "portfolios"

    user_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    name = Column(String(100), default="Primary Portfolio", nullable=False)
    description = Column(String(255), nullable=True)
    total_value = Column(Float, default=0.0, nullable=False)
    cash_balance = Column(Float, default=100000.0, nullable=False)
    weighted_beta = Column(Float, default=1.0, nullable=False)
    daily_var_95_pct = Column(Float, default=0.0, nullable=False)

    # Relationships
    user = relationship("User", back_populates="portfolios")
    positions = relationship("Position", back_populates="portfolio", cascade="all, delete-orphan")
    transactions = relationship("Transaction", back_populates="portfolio", cascade="all, delete-orphan")


class Position(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    __tablename__ = "positions"

    portfolio_id = Column(String(36), ForeignKey("portfolios.id", ondelete="CASCADE"), nullable=False, index=True)
    ticker = Column(String(10), nullable=False, index=True)
    shares = Column(Float, nullable=False)
    avg_cost = Column(Float, nullable=False)
    sector = Column(String(100), default="Information Technology", nullable=False)
    beta = Column(Float, default=1.0, nullable=False)

    __table_args__ = (
        UniqueConstraint("portfolio_id", "ticker", name="uq_position_portfolio_ticker"),
    )

    # Relationship
    portfolio = relationship("Portfolio", back_populates="positions")


class Transaction(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    __tablename__ = "transactions"

    portfolio_id = Column(String(36), ForeignKey("portfolios.id", ondelete="CASCADE"), nullable=False, index=True)
    ticker = Column(String(10), nullable=False, index=True)
    shares = Column(Float, nullable=False)
    price = Column(Float, nullable=False)
    transaction_type = Column(String(10), nullable=False)  # BUY, SELL
    executed_at = Column(DateTime(timezone=True), default=utc_now, nullable=False, index=True)

    # Relationship
    portfolio = relationship("Portfolio", back_populates="transactions")


class Watchlist(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    __tablename__ = "watchlists"

    user_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    ticker = Column(String(10), nullable=False, index=True)
    target_price = Column(Float, nullable=True)
    notes = Column(Text, nullable=True)
    added_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)

    __table_args__ = (
        UniqueConstraint("user_id", "ticker", name="uq_watchlist_user_ticker"),
    )

    # Relationship
    user = relationship("User", back_populates="watchlists")
