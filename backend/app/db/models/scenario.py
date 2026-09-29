"""
Stochastic & Historical Scenario Simulation Report ORM Model.
"""
from typing import Optional, TYPE_CHECKING
from sqlalchemy import (
    Column, String, ForeignKey, JSON, Index
)
from sqlalchemy.orm import relationship
from app.db.base import Base, UUIDPrimaryKeyMixin, TimestampMixin

if TYPE_CHECKING:
    from app.db.models.stock import Stock


class ScenarioReport(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    __tablename__ = "scenario_reports"

    stock_id = Column(String(36), ForeignKey("stocks.id", ondelete="SET NULL"), nullable=True, index=True)
    ticker = Column(String(10), nullable=False, index=True)
    scenario_type = Column(String(50), nullable=False)  # MONTE_CARLO, HISTORICAL_STRESS, MACRO_SHOCK
    parameters = Column(JSON, nullable=False)
    results = Column(JSON, nullable=False)

    __table_args__ = (
        Index("ix_scenario_reports_ticker_type", "ticker", "scenario_type"),
    )

    # Relationship
    stock = relationship("Stock", back_populates="scenario_reports")
