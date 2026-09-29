"""
Unit Tests for All 10 LangGraph Financial Research Agent Tools.
"""
import pytest
from app.agents.tools import (
    tool_get_stock_quote,
    tool_get_stock_history,
    tool_get_fundamentals,
    tool_get_news,
    tool_technical_analysis,
    tool_anomaly_analysis,
    tool_correlation_analysis,
    tool_scenario_analysis,
    tool_portfolio_analysis,
    tool_financial_document_search
)


@pytest.mark.asyncio
async def test_tool_get_stock_quote():
    res = await tool_get_stock_quote("AAPL")
    assert "price" in res
    assert "change_pct" in res
    assert res["ticker"] == "AAPL"


@pytest.mark.asyncio
async def test_tool_get_stock_history():
    res = await tool_get_stock_history("MSFT", timeframe="1m")
    assert "bars" in res
    assert len(res["bars"]) > 0


@pytest.mark.asyncio
async def test_tool_get_fundamentals():
    res = await tool_get_fundamentals("NVDA")
    assert "ticker" in res
    assert "valuation" in res


@pytest.mark.asyncio
async def test_tool_get_news():
    res = await tool_get_news("AAPL", limit=3)
    assert isinstance(res, (list, dict))
    assert len(res) > 0


@pytest.mark.asyncio
async def test_tool_technical_analysis():
    res = await tool_technical_analysis("AAPL")
    assert "rsi_14" in res
    assert "technical_bias" in res
    assert "sma_20" in res


@pytest.mark.asyncio
async def test_tool_anomaly_analysis():
    res = await tool_anomaly_analysis("NVDA")
    assert "anomalies_detected" in res or "ticker" in res


@pytest.mark.asyncio
async def test_tool_correlation_analysis():
    res = await tool_correlation_analysis()
    assert "assets" in res
    assert "matrix" in res


@pytest.mark.asyncio
async def test_tool_scenario_analysis():
    # Monte Carlo
    mc = await tool_scenario_analysis("AAPL", scenario_type="MONTE_CARLO", days=60, iterations=500)
    assert "expected_terminal_price_p50" in mc
    assert "value_at_risk_95_pct" in mc

    # Historical Stress
    stress = await tool_scenario_analysis("AAPL", scenario_type="HISTORICAL_STRESS")
    assert "scenario_results" in stress


@pytest.mark.asyncio
async def test_tool_portfolio_analysis():
    res = await tool_portfolio_analysis()
    assert "positions" in res or "total_value" in res or "portfolio" in res


@pytest.mark.asyncio
async def test_tool_financial_document_search():
    res = await tool_financial_document_search(query="Supply chain and wafers", ticker="NVDA", top_k=2)
    assert isinstance(res, list)
    assert len(res) > 0
    assert res[0]["ticker"] == "NVDA"
