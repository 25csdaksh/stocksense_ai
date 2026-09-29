"""
Repositories Registry for MarketMind AI.
"""
from app.db.repositories.base import BaseRepository
from app.db.repositories.user_repository import UserRepository
from app.db.repositories.company_repository import CompanyRepository
from app.db.repositories.stock_repository import StockRepository
from app.db.repositories.market_data_repository import MarketDataRepository
from app.db.repositories.fundamental_repository import FundamentalRepository
from app.db.repositories.news_repository import NewsRepository
from app.db.repositories.portfolio_repository import PortfolioRepository
from app.db.repositories.watchlist_repository import WatchlistRepository
from app.db.repositories.scenario_repository import ScenarioRepository
from app.db.repositories.research_repository import ResearchRepository
from app.db.repositories.ai_query_repository import AIQueryRepository

__all__ = [
    "BaseRepository",
    "UserRepository",
    "CompanyRepository",
    "StockRepository",
    "MarketDataRepository",
    "FundamentalRepository",
    "NewsRepository",
    "PortfolioRepository",
    "WatchlistRepository",
    "ScenarioRepository",
    "ResearchRepository",
    "AIQueryRepository",
]
