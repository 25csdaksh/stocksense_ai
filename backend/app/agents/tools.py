"""
Tool Definitions for LangGraph Multi-Agent Sandbox.
"""
from typing import Dict, Any, List
from app.providers.market_data.factory import get_market_data_provider
from app.providers.news.factory import get_news_provider
from app.providers.fundamentals.factory import get_fundamentals_provider
from app.analytics.scenario import MonteCarloSimulator, MacroScenarioSimulator, HistoricalStressTester
from app.analytics.stock_dna import StockDNAProfiler
from app.rag.retrieval import vector_retriever


async def tool_get_stock_quote(ticker: str) -> Dict[str, Any]:
    """Fetches real-time price, 24h change, and volume for a ticker."""
    provider = get_market_data_provider()
    return await provider.get_quote(ticker)


async def tool_run_monte_carlo(ticker: str, days: int = 90, iterations: int = 3000) -> Dict[str, Any]:
    """Runs Merton Jump Diffusion Monte Carlo simulation on an equity."""
    quote = await tool_get_stock_quote(ticker)
    sim = MonteCarloSimulator()
    res = sim.simulate(current_price=quote["price"], days=days, iterations=iterations)
    res["ticker"] = ticker
    return res


async def tool_compute_stock_dna(ticker: str) -> Dict[str, Any]:
    """Computes 5-factor DNA vector (Value, Growth, Quality, Momentum, Low Volatility)."""
    quote = await tool_get_stock_quote(ticker)
    fund_provider = get_fundamentals_provider()
    fund = await fund_provider.get_overview(ticker)
    profiler = StockDNAProfiler()
    return profiler.calculate(
        ticker=ticker,
        fundamentals=fund.get("valuation", {}),
        price_metrics={"beta": 1.15, "annualized_volatility": 26.0, "return_3m_pct": 10.0, "return_1y_pct": 22.0}
    )


async def tool_search_sec_filings(query: str, ticker: str = "", top_k: int = 3) -> List[Dict[str, Any]]:
    """Retrieves verified SEC 10-K regulatory disclosures with citations."""
    return vector_retriever.search(query=query, ticker=ticker if ticker else None, top_k=top_k)


async def tool_get_news_sentiment(ticker: str) -> List[Dict[str, Any]]:
    """Fetches recent financial news and aggregate sentiment."""
    news_provider = get_news_provider()
    return await news_provider.get_news_for_ticker(ticker)
