"""
MarketMind AI — Phase 6.10 Unit Tests: Portfolio Copilot Domain Models & Enums.
"""
import pytest
from app.ai.portfolio.models import (
    PortfolioCopilotMode,
    AlertSeverity,
    AlertRuleType,
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
from app.ai.models import EvidenceProvenance


def test_copilot_mode_enum_values():
    modes = [m.value for m in PortfolioCopilotMode]
    assert "PORTFOLIO_OVERVIEW" in modes
    assert "HOLDING_RESEARCH" in modes
    assert "WATCHLIST_RESEARCH" in modes
    assert "CHANGE_ANALYSIS" in modes
    assert "RISK_REVIEW" in modes
    assert "NEWS_REVIEW" in modes
    assert "SCENARIO_REVIEW" in modes
    assert "WEEKLY_REVIEW" in modes
    assert "DAILY_BRIEF" in modes
    assert len(modes) == 9


def test_portfolio_holding_context_validation():
    holding = PortfolioHoldingContext(
        ticker="RELIANCE.NS",
        quantity=50.0,
        average_cost=2800.0,
        current_price=2950.0,
        invested_value=140000.0,
        market_value=147500.0,
        absolute_pnl=7500.0,
        percentage_pnl=5.36,
        portfolio_weight_pct=25.0,
        sector="Energy",
        beta=1.1,
        volatility_pct=18.5,
        max_drawdown_pct=12.4,
        var_95_daily_pct=1.8,
        data_freshness="FRESH",
        provenance=EvidenceProvenance.LIVE
    )
    assert holding.ticker == "RELIANCE.NS"
    assert holding.absolute_pnl == 7500.0
    assert holding.provenance == EvidenceProvenance.LIVE


def test_portfolio_user_context_initialization():
    ctx = PortfolioUserContext(
        user_id="usr_test_01",
        name="Growth Portfolio",
        total_market_value=500000.0,
        invested_capital=450000.0,
        cash_balance=50000.0,
        total_value=550000.0,
        absolute_pnl=50000.0,
        percentage_pnl=11.11,
        daily_pnl=2500.0,
        daily_pnl_pct=0.5,
        holdings=[],
        holdings_count=0,
        sector_allocations={"Technology": 60.0, "Financials": 40.0},
        top3_exposure_pct=75.0,
        top5_exposure_pct=100.0,
        herfindahl_index=3200.0,
        weighted_beta=1.15,
        annualized_volatility_pct=21.4,
        max_drawdown_pct=16.8,
        var_95_daily_pct=2.1,
        sharpe_ratio=1.2,
        sortino_ratio=1.6
    )
    assert ctx.total_value == 550000.0
    assert ctx.herfindahl_index == 3200.0
    assert ctx.sector_allocations["Technology"] == 60.0


def test_research_memory_item_schema():
    mem = ResearchMemoryItem(
        research_id="res_test_101",
        query="Analyze TCS valuation and dividend history",
        symbols=["TCS.NS"],
        intent="FUNDAMENTAL_ANALYSIS",
        execution_depth="STANDARD",
        created_at="2026-09-15T10:00:00Z",
        report_summary="TCS demonstrates robust cash flow generation and healthy margins.",
        evidence_count=8,
        confidence_level="HIGH",
        confidence_rationale="Verified multi-pillar statements",
        key_metrics={"pe_ratio": 28.5, "roe_pct": 38.2},
        data_status="DEMO"
    )
    assert mem.research_id == "res_test_101"
    assert mem.symbols == ["TCS.NS"]
    assert mem.key_metrics["pe_ratio"] == 28.5


def test_change_item_schema():
    change = PortfolioChangeItem(
        metric="portfolio_weight_pct",
        symbol="INFY.NS",
        previous_value=15.0,
        current_value=22.5,
        absolute_change=7.5,
        percentage_change=50.0,
        description="INFY weight increased from 15.0% to 22.5%.",
        change_type="WEIGHT_SHIFT"
    )
    assert change.metric == "portfolio_weight_pct"
    assert change.absolute_change == 7.5
