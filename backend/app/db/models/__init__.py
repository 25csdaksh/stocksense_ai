"""
ORM Models Registry for MarketMind AI Database Layer.
Exports all 19 relational & time-series models for Alembic migrations and Repository queries.
"""
from app.db.base import Base
from app.db.models.user import User
from app.db.models.company import Sector, Company
from app.db.models.stock import Stock, StockOHLCV, MarketIndex
from app.db.models.fundamental import Fundamental, FinancialStatement
from app.db.models.news import News
from app.db.models.anomaly import Anomaly
from app.db.models.scenario import ScenarioReport
from app.db.models.portfolio import Portfolio, Position, Transaction, Watchlist
from app.db.models.ai import ChatSession, AIQuery
from app.db.models.research import ResearchDocument, ResearchChunk
from app.db.models.research_memory import UserResearchMemory, PortfolioAlert, AlertRule, AlertEvent

__all__ = [
    "Base",
    "User",
    "Sector",
    "Company",
    "Stock",
    "StockOHLCV",
    "MarketIndex",
    "Fundamental",
    "FinancialStatement",
    "News",
    "Anomaly",
    "ScenarioReport",
    "Portfolio",
    "Position",
    "Transaction",
    "Watchlist",
    "ChatSession",
    "AIQuery",
    "ResearchDocument",
    "ResearchChunk",
    "UserResearchMemory",
    "PortfolioAlert",
    "AlertRule",
    "AlertEvent",
]

