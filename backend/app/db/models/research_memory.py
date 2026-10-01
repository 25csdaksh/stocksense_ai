"""
MarketMind AI — User Research Memory, Portfolio Alerts & Rules ORM Models.
Phase 6.10: User-isolated research memory, factual threshold alert rules, and audit events.
"""
from sqlalchemy import Column, String, Float, Boolean, Integer, Text, DateTime, ForeignKey, Index
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.types import JSON
from sqlalchemy.orm import relationship
from app.db.base import Base, UUIDPrimaryKeyMixin, TimestampMixin, utc_now


class UserResearchMemory(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    """User-scoped historical research memory for factual change tracking and recall."""
    __tablename__ = "user_research_memories"

    user_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    research_id = Column(String(64), nullable=False, index=True)
    query = Column(Text, nullable=False)
    symbols = Column(JSON, nullable=False, default=list)
    intent = Column(String(64), nullable=False, default="GENERAL_FINANCIAL_RESEARCH")
    execution_depth = Column(String(32), nullable=False, default="STANDARD")
    report_summary = Column(Text, nullable=True)
    evidence_count = Column(Integer, default=0, nullable=False)
    confidence_level = Column(String(32), default="MEDIUM", nullable=False)
    confidence_rationale = Column(Text, nullable=True)
    provenance_summary = Column(JSON, nullable=True, default=dict)
    key_metrics = Column(JSON, nullable=True, default=dict)
    cited_sources = Column(JSON, nullable=True, default=list)
    data_status = Column(String(32), default="DEMO", nullable=False)
    research_version = Column(String(32), default="6.10", nullable=False)

    __table_args__ = (
        Index("ix_research_memory_user_created", "user_id", "created_at"),
    )


class PortfolioAlert(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    """Factual threshold alert notifications generated for user holdings or market anomalies."""
    __tablename__ = "portfolio_alerts"

    user_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    portfolio_id = Column(String(36), ForeignKey("portfolios.id", ondelete="CASCADE"), nullable=True, index=True)
    symbol = Column(String(20), nullable=True, index=True)
    alert_type = Column(String(50), nullable=False)  # PRICE_MOVE, VOLATILITY_SPIKE, VOLUME_SURGE, WEIGHT_THRESHOLD, etc.
    title = Column(String(255), nullable=False)
    message = Column(Text, nullable=False)
    severity = Column(String(20), default="INFO", nullable=False)  # INFO, WARNING, CRITICAL
    trigger_metric = Column(String(50), nullable=True)
    trigger_value = Column(Float, nullable=True)
    threshold_value = Column(Float, nullable=True)
    provenance = Column(String(32), default="DEMO", nullable=False)
    is_read = Column(Boolean, default=False, nullable=False)

    __table_args__ = (
        Index("ix_portfolio_alerts_user_unread", "user_id", "is_read"),
    )


class AlertRule(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    """Configurable user alert rules evaluating portfolio and watchlist triggers."""
    __tablename__ = "alert_rules"

    user_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    portfolio_id = Column(String(36), ForeignKey("portfolios.id", ondelete="CASCADE"), nullable=True, index=True)
    symbol = Column(String(20), nullable=True)
    rule_type = Column(String(50), nullable=False)  # PRICE_MOVE_PCT, VOLATILITY_THRESHOLD, WEIGHT_THRESHOLD, etc.
    threshold = Column(Float, nullable=False)
    timeframe = Column(String(20), default="1d", nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)


class AlertEvent(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    """Immutable audit trail of fired alert rule events."""
    __tablename__ = "alert_events"

    rule_id = Column(String(36), ForeignKey("alert_rules.id", ondelete="CASCADE"), nullable=True, index=True)
    user_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    symbol = Column(String(20), nullable=True)
    trigger = Column(String(100), nullable=False)
    value = Column(Float, nullable=True)
    provenance = Column(String(32), default="DEMO", nullable=False)
    data_status = Column(String(32), default="DEMO", nullable=False)
    details = Column(JSON, nullable=True, default=dict)
