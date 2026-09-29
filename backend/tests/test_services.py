"""
Service Layer Integration & Business Logic Tests.
"""
import pytest
from app.services.market_service import market_service
from app.services.stock_service import stock_service
from app.services.fundamentals_service import fundamentals_service
from app.services.news_service import news_service
from app.services.portfolio_service import portfolio_service
from app.services.research_service import research_service
from app.services.scenario_service import scenario_service
from app.services.analytics_service import analytics_service


@pytest.mark.asyncio
async def test_market_service_overview():
    overview = await market_service.get_overview()
    assert "indices" in overview
    assert "top_gainers" in overview
    assert "market_regime" in overview
    assert len(overview["indices"]) > 0


@pytest.mark.asyncio
async def test_stock_service_quote_and_history():
    quote = await stock_service.get_quote("AAPL")
    assert quote["ticker"] == "AAPL"
    assert quote["price"] > 0

    hist = await stock_service.get_history("AAPL", timeframe="1m", interval="1d")
    assert hist["ticker"] == "AAPL"
    assert len(hist["bars"]) > 0


@pytest.mark.asyncio
async def test_fundamentals_service():
    funda = await fundamentals_service.get_overview("NVDA")
    assert funda["ticker"] == "NVDA"
    assert "valuation" in funda
    assert "profitability" in funda

    stmts = await fundamentals_service.get_statements("NVDA", statement_type="income")
    assert stmts["ticker"] == "NVDA"
    assert len(stmts["periods"]) > 0


@pytest.mark.asyncio
async def test_news_service():
    news = await news_service.get_news_for_ticker("MSFT")
    assert news["ticker"] == "MSFT"
    assert "overall_sentiment" in news
    assert len(news["news_items"]) > 0


@pytest.mark.asyncio
async def test_portfolio_service():
    summary = await portfolio_service.get_portfolio_summary()
    assert "total_value" in summary
    assert "positions" in summary
    assert summary["positions_count"] > 0

    # Add transaction
    tx = await portfolio_service.add_transaction("AAPL", shares=10, price=180.0, tx_type="BUY")
    assert tx["status"] == "SUCCESS"

    # Watchlist
    await portfolio_service.add_to_watchlist("TSLA", target_price=300.0, notes="Test note")
    wl = await portfolio_service.get_watchlist()
    assert any(w["ticker"] == "TSLA" for w in wl)

    removed = await portfolio_service.remove_from_watchlist("TSLA")
    assert removed is True


@pytest.mark.asyncio
async def test_research_service():
    res = await research_service.search_filings(query="TSMC foundry CoWoS packaging", ticker="NVDA")
    assert res["total_results"] > 0
    assert "synthesis_summary" in res
    assert len(res["citations"]) > 0


@pytest.mark.asyncio
async def test_analytics_service_dna():
    dna = await analytics_service.get_stock_dna("AAPL")
    assert dna["ticker"] == "AAPL"
    assert "factor_scores" in dna
    assert "radar_data" in dna
    assert len(dna["radar_data"]) == 5
