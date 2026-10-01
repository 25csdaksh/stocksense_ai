"""
MarketMind AI — Phase 6.10 Unit Tests: Portfolio Context & Quantitative Analyzer.
"""
import pytest
from app.ai.portfolio.models import PortfolioHoldingContext
from app.ai.portfolio.portfolio_analyzer import portfolio_analyzer
from app.ai.portfolio.context_builder import user_context_builder
from app.ai.models import EvidenceProvenance


def test_portfolio_analyzer_metrics_calculation():
    holdings = [
        PortfolioHoldingContext(
            ticker="RELIANCE.NS",
            quantity=100.0,
            average_cost=2500.0,
            current_price=3000.0,
            invested_value=250000.0,
            market_value=300000.0,
            absolute_pnl=50000.0,
            percentage_pnl=20.0,
            portfolio_weight_pct=0.0,
            sector="Energy",
            beta=1.1,
            volatility_pct=20.0,
            max_drawdown_pct=15.0
        ),
        PortfolioHoldingContext(
            ticker="TCS.NS",
            quantity=50.0,
            average_cost=3500.0,
            current_price=4000.0,
            invested_value=175000.0,
            market_value=200000.0,
            absolute_pnl=25000.0,
            percentage_pnl=14.29,
            portfolio_weight_pct=0.0,
            sector="Technology",
            beta=0.9,
            volatility_pct=16.0,
            max_drawdown_pct=10.0
        )
    ]

    user_ctx, risk_ctx = portfolio_analyzer.calculate_portfolio_metrics(
        user_id="usr_test_analyzer",
        holdings=holdings,
        cash_balance=50000.0
    )

    # 1. Check totals
    assert user_ctx.total_market_value == 500000.0
    assert user_ctx.invested_capital == 425000.0
    assert user_ctx.absolute_pnl == 75000.0
    assert user_ctx.total_value == 550000.0
    assert user_ctx.holdings_count == 2

    # 2. Check weights & concentration
    assert holdings[0].portfolio_weight_pct == 60.0  # 300k / 500k
    assert holdings[1].portfolio_weight_pct == 40.0  # 200k / 500k
    assert user_ctx.top_holding_symbol == "RELIANCE.NS"
    assert user_ctx.top_holding_weight_pct == 60.0

    # Herfindahl Index: 60^2 + 40^2 = 3600 + 1600 = 5200
    assert user_ctx.herfindahl_index == 5200.0

    # Sector allocations
    assert user_ctx.sector_allocations["Energy"] == 60.0
    assert user_ctx.sector_allocations["Technology"] == 40.0

    # Weighted Beta: (0.6 * 1.1) + (0.4 * 0.9) = 0.66 + 0.36 = 1.02
    assert user_ctx.weighted_beta == 1.02

    # Risk context
    assert risk_ctx.weighted_beta == 1.02
    assert risk_ctx.var_95_daily_pct > 0.0
    assert len(risk_ctx.stress_scenarios) >= 3


def test_portfolio_analyzer_empty_holdings():
    user_ctx, risk_ctx = portfolio_analyzer.calculate_portfolio_metrics(
        user_id="usr_empty",
        holdings=[],
        cash_balance=10000.0
    )
    assert user_ctx.total_market_value == 0.0
    assert user_ctx.holdings_count == 0
    assert user_ctx.cash_balance == 10000.0
    assert user_ctx.herfindahl_index == 0.0


@pytest.mark.asyncio
async def test_user_context_builder_execution():
    ctx = await user_context_builder.build_user_context(
        user_id="usr_test_builder",
        db=None
    )
    assert ctx.user_id == "usr_test_builder"
    assert ctx.portfolio is not None
    assert ctx.watchlist is not None
    assert ctx.memory is not None
    assert ctx.risk is not None
    assert ctx.news is not None
    assert ctx.anomaly is not None
