"""
MarketMind AI — Portfolio Copilot & Personal Research Memory Package.
Phase 6.10: Exposes context builder, portfolio analyzer, change detector, memory service, alert engine, and copilot engine.
"""
from app.ai.portfolio.models import (
    PortfolioCopilotMode,
    PortfolioHoldingContext,
    PortfolioUserContext,
    WatchlistItemContext,
    WatchlistContext,
    PortfolioRiskContext,
    PortfolioNewsContext,
    PortfolioAnomalyContext,
    ResearchMemoryItem,
    ResearchMemoryContext,
    UserResearchContext,
    PortfolioChangeItem,
    PortfolioChangeReport,
    DailyPortfolioBrief,
    PortfolioAlertRuleModel,
    PortfolioAlertEventModel,
    PortfolioCopilotQueryRequest,
    PortfolioCopilotQueryResponse,
)
from app.ai.portfolio.portfolio_analyzer import portfolio_analyzer, PortfolioAnalyzer
from app.ai.portfolio.context_builder import user_context_builder, UserContextBuilder
from app.ai.portfolio.change_detector import change_detector, PortfolioChangeDetector
from app.ai.portfolio.memory_service import memory_service, ResearchMemoryService
from app.ai.portfolio.alert_engine import alert_engine, PortfolioAlertEngine
from app.ai.portfolio.copilot_engine import copilot_engine, PortfolioCopilotEngine

__all__ = [
    "PortfolioCopilotMode",
    "PortfolioHoldingContext",
    "PortfolioUserContext",
    "WatchlistItemContext",
    "WatchlistContext",
    "PortfolioRiskContext",
    "PortfolioNewsContext",
    "PortfolioAnomalyContext",
    "ResearchMemoryItem",
    "ResearchMemoryContext",
    "UserResearchContext",
    "PortfolioChangeItem",
    "PortfolioChangeReport",
    "DailyPortfolioBrief",
    "PortfolioAlertRuleModel",
    "PortfolioAlertEventModel",
    "PortfolioCopilotQueryRequest",
    "PortfolioCopilotQueryResponse",
    "portfolio_analyzer",
    "PortfolioAnalyzer",
    "user_context_builder",
    "UserContextBuilder",
    "change_detector",
    "PortfolioChangeDetector",
    "memory_service",
    "ResearchMemoryService",
    "alert_engine",
    "PortfolioAlertEngine",
    "copilot_engine",
    "PortfolioCopilotEngine",
]
