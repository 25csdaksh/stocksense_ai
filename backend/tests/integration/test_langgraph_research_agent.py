"""
Integration Tests for LangGraph Multi-Agent Research Agent Execution.
Verifies complete flow: User Query -> Intent & Entity -> Dynamic Tool Routing -> Context Building -> Grounded Synthesis.
"""
import pytest
from app.agents.graph import agent_graph_runner


@pytest.mark.asyncio
async def test_langgraph_scenario_simulation_flow():
    query = "Run a 90-day Merton Jump Diffusion Monte Carlo simulation on Apple with VaR and fan chart projections"
    res = await agent_graph_runner.execute(query=query, session_id="test_sim_session")

    assert res["intent"] == "SCENARIO_SIMULATION"
    assert res["ticker_focus"] == "AAPL"
    assert len(res["thought_steps"]) >= 2
    assert any(tc["tool"] == "run_merton_jump_diffusion" for tc in res["tool_calls"])
    assert len(res["ui_widgets"]) > 0
    assert res["ui_widgets"][0]["widget_type"] == "FAN_CHART"
    assert "Value-at-Risk" in res["answer"]
    assert res["guardrail_passed"] is True


@pytest.mark.asyncio
async def test_langgraph_stock_dna_factor_flow():
    query = "Compute the 5-factor Stock DNA radar profile and dominant persona for NVIDIA"
    res = await agent_graph_runner.execute(query=query, session_id="test_dna_session")

    assert res["intent"] == "STOCK_DNA"
    assert res["ticker_focus"] == "NVDA"
    assert len(res["ui_widgets"]) > 0
    assert res["ui_widgets"][0]["widget_type"] == "RADAR_DNA"
    assert "Dominant Persona" in res["answer"]


@pytest.mark.asyncio
async def test_langgraph_rag_sec_filing_search_flow():
    query = "Search NVIDIA 10-K regulatory risk factors regarding TSMC foundry wafers"
    res = await agent_graph_runner.execute(query=query, session_id="test_rag_session")

    assert res["intent"] == "RAG_SEARCH"
    assert res["ticker_focus"] == "NVDA"
    assert len(res["citations"]) > 0
    assert "TSMC" in res["citations"][0]["content_snippet"] or "TSMC" in res["answer"]
    assert "Regulatory Notice" in res["answer"]


@pytest.mark.asyncio
async def test_langgraph_technical_analysis_flow():
    query = "Provide RSI and technical momentum analysis for Microsoft"
    res = await agent_graph_runner.execute(query=query, session_id="test_tech_session")

    assert res["intent"] == "TECHNICAL_ANALYSIS"
    assert res["ticker_focus"] == "MSFT"
    assert "RSI" in res["answer"]


@pytest.mark.asyncio
async def test_langgraph_indian_market_entity_flow():
    query = "Analyze Reliance Industries stock quote and market cap in INR"
    res = await agent_graph_runner.execute(query=query, session_id="test_indian_session")

    assert "RELIANCE" in res["ticker_focus"]
    assert "₹" in res["answer"] or "INR" in res["answer"] or "Reliance" in res["answer"]
