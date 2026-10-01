"""
MarketMind AI — Phase 6.10 Unit Tests: Alert Engine & Daily Portfolio Brief.
"""
import pytest
from app.ai.portfolio.models import (
    UserResearchContext,
    PortfolioHoldingContext,
    PortfolioUserContext,
    WatchlistContext,
    PortfolioRiskContext,
    PortfolioNewsContext,
    PortfolioAnomalyContext,
    ResearchMemoryContext,
    AlertRuleType,
)
from app.ai.portfolio.alert_engine import alert_engine
from app.ai.portfolio.copilot_engine import copilot_engine
from app.ai.portfolio.change_detector import change_detector


@pytest.mark.asyncio
async def test_alert_engine_rule_evaluation():
    holdings = [
        PortfolioHoldingContext(
            ticker="TCS.NS",
            quantity=100.0,
            average_cost=3000.0,
            current_price=3500.0,
            invested_value=300000.0,
            market_value=350000.0,
            absolute_pnl=50000.0,
            percentage_pnl=16.67,
            portfolio_weight_pct=35.0,  # Crosses 25% default rule
            volatility_pct=34.0         # Crosses 30% default rule
        )
    ]
    p_ctx = PortfolioUserContext(
        user_id="usr_alert_test",
        total_market_value=1000000.0,
        holdings=holdings,
        sector_allocations={"Technology": 35.0}
    )
    user_ctx = UserResearchContext(
        user_id="usr_alert_test",
        portfolio=p_ctx,
        watchlist=WatchlistContext(user_id="usr_alert_test"),
        memory=ResearchMemoryContext(user_id="usr_alert_test"),
        risk=PortfolioRiskContext(),
        news=PortfolioNewsContext(),
        anomaly=PortfolioAnomalyContext()
    )

    alerts = await alert_engine.evaluate_rules(
        user_id="usr_alert_test",
        user_context=user_ctx,
        db=None
    )

    assert len(alerts) >= 2
    types = [a.alert_type for a in alerts]
    assert "WEIGHT_THRESHOLD_CROSSED" in types
    assert "VOLATILITY_ELEVATED" in types

    # Check alert messages are factual without buy/sell advice
    for a in alerts:
        msg = a.message.upper()
        assert "SELL" not in msg
        assert "BUY" not in msg
        assert "NOW" not in msg


def test_copilot_daily_brief_generation():
    holdings = [
        PortfolioHoldingContext(
            ticker="RELIANCE.NS",
            quantity=50.0,
            average_cost=2800.0,
            current_price=3000.0,
            invested_value=140000.0,
            market_value=150000.0,
            absolute_pnl=10000.0,
            percentage_pnl=7.14,
            portfolio_weight_pct=100.0,
            volatility_pct=18.0
        )
    ]
    p_ctx = PortfolioUserContext(
        user_id="usr_daily_brief",
        total_market_value=150000.0,
        holdings=holdings,
        holdings_count=1,
        daily_pnl=1500.0,
        daily_pnl_pct=1.0,
        weighted_beta=1.1,
        herfindahl_index=10000.0
    )
    user_ctx = UserResearchContext(
        user_id="usr_daily_brief",
        portfolio=p_ctx,
        watchlist=WatchlistContext(user_id="usr_daily_brief"),
        memory=ResearchMemoryContext(user_id="usr_daily_brief"),
        risk=PortfolioRiskContext(weighted_beta=1.1, var_95_daily_pct=1.8),
        news=PortfolioNewsContext(),
        anomaly=PortfolioAnomalyContext()
    )

    changes = change_detector.detect_portfolio_internal_changes(holdings, p_ctx)
    brief = copilot_engine.generate_daily_brief(
        user_id="usr_daily_brief",
        user_ctx=user_ctx,
        change_report=changes
    )

    assert brief.user_id == "usr_daily_brief"
    assert brief.portfolio_summary["total_market_value"] == 150000.0
    assert len(brief.daily_movers) == 1
    assert brief.daily_movers[0]["symbol"] == "RELIANCE.NS"
    assert len(brief.limitations) >= 1
