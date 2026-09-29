"""
Detected Anomaly, Simulation Run, and Financial News ORM Models.
"""
import uuid
from datetime import datetime
from sqlalchemy import Column, String, Numeric, DateTime, JSON, Text, ForeignKey
from core.database import Base


class DetectedAnomaly(Base):
    __tablename__ = "detected_anomalies"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    timestamp = Column(DateTime, nullable=False, index=True)
    ticker = Column(String(16), ForeignKey("assets.ticker", ondelete="CASCADE"), nullable=False, index=True)
    anomaly_type = Column(String(50), nullable=False)
    severity_score = Column(Numeric(5, 4), nullable=False)
    z_score = Column(Numeric(8, 4), nullable=True)
    isolation_forest_score = Column(Numeric(8, 4), nullable=True)
    summary = Column(Text, nullable=False)
    context_data = Column(JSON, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)


class ScenarioSimulation(Base):
    __tablename__ = "scenario_simulations"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    title = Column(String(255), nullable=False)
    scenario_type = Column(String(50), nullable=False)
    target_tickers = Column(JSON, nullable=False)
    parameters = Column(JSON, nullable=False)
    results_summary = Column(JSON, nullable=False)
    generated_at = Column(DateTime, default=datetime.utcnow)


class FinancialNews(Base):
    __tablename__ = "financial_news"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    ticker = Column(String(16), nullable=False, index=True)
    title = Column(String(500), nullable=False)
    summary = Column(Text, nullable=True)
    source = Column(String(100), nullable=False)
    url = Column(String(500), nullable=True)
    published_at = Column(DateTime, nullable=False, index=True)
    sentiment_label = Column(String(20), default="NEUTRAL")  # BULLISH, BEARISH, NEUTRAL
    sentiment_score = Column(Numeric(5, 4), default=0.0)     # -1.0 to +1.0
    impact_score = Column(Numeric(5, 4), default=0.5)        # 0.0 to 1.0
    created_at = Column(DateTime, default=datetime.utcnow)
