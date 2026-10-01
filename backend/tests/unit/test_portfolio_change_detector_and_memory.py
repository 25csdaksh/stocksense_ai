"""
MarketMind AI — Phase 6.10 Unit Tests: Change Detector & Personal Research Memory.
"""
import pytest
from app.ai.portfolio.models import (
    ResearchMemoryItem,
    PortfolioHoldingContext,
    PortfolioUserContext,
)
from app.ai.portfolio.change_detector import change_detector
from app.ai.portfolio.memory_service import memory_service


def test_change_detector_price_and_valuation_shift():
    memory = ResearchMemoryItem(
        research_id="res_prev_01",
        query="Research INFY fundamentals and price",
        symbols=["INFY.NS"],
        intent="FUNDAMENTAL_ANALYSIS",
        created_at="2026-08-01T10:00:00Z",
        key_metrics={"INFY.NS_price": 1400.0, "INFY.NS_pe": 24.0, "INFY.NS_volatility": 18.0}
    )

    current_holdings = [
        PortfolioHoldingContext(
            ticker="INFY.NS",
            quantity=100.0,
            average_cost=1400.0,
            current_price=1600.0,  # +14.29% price jump
            invested_value=140000.0,
            market_value=160000.0,
            absolute_pnl=20000.0,
            percentage_pnl=14.29,
            portfolio_weight_pct=20.0,
            pe_ratio=27.5,        # P/E multiple expansion
            volatility_pct=21.5    # Volatility increase
        )
    ]

    current_portfolio = PortfolioUserContext(
        user_id="usr_test_change",
        total_market_value=800000.0,
        holdings=current_holdings
    )

    report = change_detector.compare_memory_vs_current(
        memory=memory,
        current_holdings=current_holdings,
        current_portfolio=current_portfolio
    )

    assert report.total_changes >= 3
    metrics = [c.metric for c in report.holding_changes + report.valuation_changes + report.risk_changes]
    assert "price" in metrics
    assert "pe_ratio" in metrics
    assert "volatility_pct" in metrics

    # Check descriptions are factual
    for ch in report.holding_changes:
        assert "INFY.NS" in ch.description
        assert "shifted" in ch.description or "moved" in ch.description


def test_change_detector_internal_threshold_shifts():
    holdings = [
        PortfolioHoldingContext(
            ticker="NVDA",
            quantity=50.0,
            average_cost=400.0,
            current_price=800.0,
            invested_value=20000.0,
            market_value=40000.0,
            absolute_pnl=20000.0,
            percentage_pnl=100.0,
            portfolio_weight_pct=45.0,  # >25% threshold
            volatility_pct=35.0         # >30% threshold
        )
    ]
    portfolio = PortfolioUserContext(
        user_id="usr_nvda",
        total_market_value=100000.0,
        holdings=holdings
    )

    report = change_detector.detect_portfolio_internal_changes(holdings, portfolio)
    assert report.total_changes >= 2
    types = [c.change_type for c in report.holding_changes + report.risk_changes]
    assert "WEIGHT_SHIFT" in types
    assert "RISK_SHIFT" in types


@pytest.mark.asyncio
async def test_memory_service_record_and_query():
    user_id = "usr_memory_unit_test_99"
    res_id = "res_unit_test_mem_001"

    item = await memory_service.record_research_session(
        user_id=user_id,
        research_id=res_id,
        query="Examine RELIANCE debt and capital expenditure",
        symbols=["RELIANCE.NS"],
        intent="STOCK_RESEARCH",
        depth="STANDARD",
        report_summary="Reliance maintains solid operating cash flows.",
        evidence_count=12,
        confidence_level="HIGH",
        key_metrics={"debt_to_equity": 0.42, "current_price": 2980.0},
        db=None
    )

    assert item.research_id == res_id
    assert item.symbols == ["RELIANCE.NS"]
    assert item.key_metrics["debt_to_equity"] == 0.42

    # Verify Redis isolated cache
    cached_mem = await memory_service.get_memory_by_id(user_id=user_id, research_id=res_id, db=None)
    assert cached_mem is not None
    assert cached_mem.research_id == res_id
