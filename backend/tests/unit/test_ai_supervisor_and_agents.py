"""
MarketMind AI — Phase 6.9 Unit Tests: Supervisor and Specialist Agents.
"""
import pytest
from app.ai.models import (
    ResearchIntent,
    ResearchDepth,
    EvidenceProvenance,
)
from app.ai.agents.supervisor_agent import supervisor_agent
from app.ai.agents.market_agent import market_agent
from app.ai.agents.fundamental_agent import fundamental_agent
from app.ai.agents.news_agent import news_agent
from app.ai.agents.quant_agent import quant_agent
from app.ai.agents.risk_agent import risk_agent
from app.ai.agents.anomaly_agent import anomaly_agent
from app.ai.agents.rag_agent import rag_agent
from app.ai.agents.comparison_agent import comparison_agent
from app.ai.agents.context_agent import context_agent


def test_supervisor_symbol_extraction():
    symbols = supervisor_agent.extract_symbols("Analyze RELIANCE.NS and TCS.NS relative performance")
    assert "RELIANCE.NS" in symbols
    assert "TCS.NS" in symbols

    us_symbols = supervisor_agent.extract_symbols("Compare AAPL vs MSFT valuation")
    assert "AAPL" in us_symbols
    assert "MSFT" in us_symbols


def test_supervisor_intent_classification():
    # Comparison
    plan_comp = supervisor_agent.create_plan("Compare RELIANCE.NS and TCS.NS valuation and momentum")
    assert plan_comp.intent == ResearchIntent.STOCK_COMPARISON
    assert "comparison_agent" in plan_comp.selected_agents

    # Fundamental
    plan_fund = supervisor_agent.create_plan("What is the P/E ratio and balance sheet health of INFY.NS?")
    assert plan_fund.intent == ResearchIntent.FUNDAMENTAL_ANALYSIS
    assert "fundamental_agent" in plan_fund.selected_agents

    # Technical
    plan_tech = supervisor_agent.create_plan("Calculate RSI and MACD for AAPL")
    assert plan_tech.intent == ResearchIntent.TECHNICAL_ANALYSIS
    assert "quant_agent" in plan_tech.selected_agents

    # Anomaly
    plan_anom = supervisor_agent.create_plan("Why did HDFCBANK.NS experience an unusual price spike?")
    assert plan_anom.intent == ResearchIntent.ANOMALY_ANALYSIS
    assert "anomaly_agent" in plan_anom.selected_agents

    # Risk
    plan_risk = supervisor_agent.create_plan("What is the maximum drawdown and VaR for ICICIBANK.NS?")
    assert plan_risk.intent == ResearchIntent.RISK_ANALYSIS
    assert "risk_agent" in plan_risk.selected_agents


def test_supervisor_depth_levels():
    plan_quick = supervisor_agent.create_plan("Overview of AAPL", depth=ResearchDepth.QUICK)
    assert plan_quick.research_depth == ResearchDepth.QUICK
    assert len(plan_quick.selected_agents) <= 4

    plan_deep = supervisor_agent.create_plan("Comprehensive study of AAPL", depth=ResearchDepth.DEEP)
    assert plan_deep.research_depth == ResearchDepth.DEEP
    assert len(plan_deep.selected_agents) >= 6


@pytest.mark.asyncio
async def test_market_agent_execution():
    evidence = await market_agent.run(symbols=["RELIANCE.NS"], timeframe="3m")
    assert len(evidence) >= 1
    price_ev = [e for e in evidence if e.metric == "latest_price"]
    assert len(price_ev) == 1
    assert price_ev[0].symbol == "RELIANCE.NS"
    assert "price" in price_ev[0].value
    assert price_ev[0].provenance in [EvidenceProvenance.LIVE, EvidenceProvenance.DEMO]


@pytest.mark.asyncio
async def test_fundamental_agent_execution():
    evidence = await fundamental_agent.run(symbols=["TCS.NS"])
    assert len(evidence) >= 1
    categories = {e.category for e in evidence}
    assert "FUNDAMENTAL" in categories
    metrics = {e.metric for e in evidence}
    assert any("ratios" in m or "company_profile" in m for m in metrics)


@pytest.mark.asyncio
async def test_news_agent_execution():
    evidence = await news_agent.run(symbols=["INFY.NS"], limit=3)
    assert len(evidence) >= 1
    news_ev = [e for e in evidence if e.category == "NEWS"]
    assert len(news_ev) >= 1


@pytest.mark.asyncio
async def test_quant_agent_execution():
    evidence = await quant_agent.run(symbols=["RELIANCE.NS"], timeframe="6m")
    assert len(evidence) >= 1
    tech_metrics = [e.metric for e in evidence]
    assert "trend_and_moving_averages" in tech_metrics
    assert "momentum_oscillators" in tech_metrics


@pytest.mark.asyncio
async def test_risk_agent_execution():
    evidence = await risk_agent.run(symbols=["RELIANCE.NS"], timeframe="6m")
    assert len(evidence) >= 1
    risk_ev = [e for e in evidence if e.metric == "downside_risk_profile"]
    assert len(risk_ev) == 1
    val = risk_ev[0].value
    assert "annualized_volatility_pct" in val
    assert "max_drawdown_pct" in val
    assert "var_95_daily_pct" in val


@pytest.mark.asyncio
async def test_anomaly_agent_associative_phrasing():
    evidence = await anomaly_agent.run(symbols=["RELIANCE.NS"], timeframe="6m")
    assert len(evidence) >= 1
    anom_ev = [e for e in evidence if e.metric == "detected_market_anomalies"]
    assert len(anom_ev) == 1
    val = anom_ev[0].value
    assert "analysis_note" in val
    note = val["analysis_note"]
    # Check that note does not assert causation blindly
    assert "caused by" not in note.lower()


@pytest.mark.asyncio
async def test_rag_agent_execution():
    evidence = await rag_agent.run(query="Supply chain risks", symbols=["AAPL"])
    assert len(evidence) >= 1
    rag_items = [e for e in evidence if e.category == "RAG"]
    assert len(rag_items) >= 1


@pytest.mark.asyncio
async def test_comparison_agent_execution():
    mkt_ev = await market_agent.run(symbols=["RELIANCE.NS", "TCS.NS"])
    fund_ev = await fundamental_agent.run(symbols=["RELIANCE.NS", "TCS.NS"])
    quant_ev = await quant_agent.run(symbols=["RELIANCE.NS", "TCS.NS"])
    risk_ev = await risk_agent.run(symbols=["RELIANCE.NS", "TCS.NS"])

    comp_evidence = await comparison_agent.run(
        symbols=["RELIANCE.NS", "TCS.NS"],
        market_evidence=mkt_ev,
        fundamental_evidence=fund_ev,
        technical_evidence=quant_ev,
        risk_evidence=risk_ev
    )
    assert len(comp_evidence) == 1
    matrix_val = comp_evidence[0].value
    assert "metrics_matrix" in matrix_val
    assert len(matrix_val["metrics_matrix"]) == 2


@pytest.mark.asyncio
async def test_context_agent_execution():
    evidence = await context_agent.run()
    assert len(evidence) >= 1
    macro_items = [e for e in evidence if e.category == "MACRO"]
    assert len(macro_items) >= 1
