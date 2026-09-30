"""
Complete Tool Suite for MarketMind AI LangGraph Research Agent Sandbox.
Phase 6.6: Implements specialized financial and quantitative analysis tools
including structured company fundamentals, multi-period statements, and factual reasoning.
"""
from typing import Dict, Any, List, Optional
from app.providers.market_data.factory import get_market_data_provider
from app.providers.news.factory import get_news_provider
from app.providers.fundamentals.factory import get_fundamentals_provider
from app.services.fundamentals_service import fundamentals_service
from app.analytics.technical import TechnicalAnalyzer
from app.analytics.anomaly import MarketAnomalyDetector
from app.analytics.correlation import CorrelationEngine
from app.analytics.scenario import MonteCarloSimulator, MacroScenarioSimulator, HistoricalStressTester
from app.analytics.stock_dna import StockDNAProfiler
from app.services.portfolio_service import portfolio_service
from app.rag.retrieval import vector_retriever


# 1. Spot Quote Tool
async def tool_get_stock_quote(ticker: str) -> Dict[str, Any]:
    """Fetches real-time price, change percentage, market cap, and 52-week bounds."""
    provider = get_market_data_provider(ticker)
    return await provider.get_quote(ticker)


# 2. Historical OHLCV Tool
async def tool_get_stock_history(ticker: str, timeframe: str = "6m", interval: str = "1d") -> Dict[str, Any]:
    """Retrieves historical OHLCV candlestick time series."""
    provider = get_market_data_provider(ticker)
    return await provider.get_history(ticker, timeframe=timeframe, interval=interval)


# 3. Fundamentals & Valuation Tool
async def tool_get_fundamentals(ticker: str) -> Dict[str, Any]:
    """Retrieves valuation multiples (P/E, P/B, EV/EBITDA), margins, and financial health scores."""
    overview = await fundamentals_service.get_overview(ticker)
    if overview:
        return overview.model_dump()
    fund_provider = get_fundamentals_provider(ticker)
    return await fund_provider.get_overview(ticker)


# 3b. Structured Fundamental Analysis Tool (Distinguishes FACT, CALCULATION, ASSUMPTION, UNAVAILABLE)
async def tool_get_fundamental_analysis(ticker: str) -> Dict[str, Any]:
    """
    Retrieves deep structured fundamental analysis strictly separating:
    - FACTS: reported revenue, net income, assets, liabilities, currency
    - CALCULATIONS: computed margins, ROE, ROA, Altman Z-Score, Debt/Equity
    - ASSUMPTIONS: tax rate, normalized growth rates
    - UNAVAILABLE: fields that could not be verified
    - PROVENANCE: provider and data status (DEMO/LIVE)
    """
    overview = await fundamentals_service.get_overview(ticker)
    profile = await fundamentals_service.get_company_profile(ticker)

    facts = {}
    if profile:
        facts["company_name"] = profile.name
        facts["legal_name"] = profile.legal_name
        facts["exchange"] = profile.exchange
        facts["sector"] = profile.sector
        facts["industry"] = profile.industry
        facts["country"] = profile.country
        facts["currency"] = profile.currency
        facts["market_cap"] = profile.market_cap

    if overview.latest_income:
        facts["latest_revenue"] = overview.latest_income.revenue
        facts["latest_net_income"] = overview.latest_income.net_income
        facts["latest_operating_income"] = overview.latest_income.operating_income
        facts["latest_eps"] = overview.latest_income.eps

    if overview.latest_balance:
        facts["total_assets"] = overview.latest_balance.total_assets
        facts["total_liabilities"] = overview.latest_balance.total_liabilities
        facts["total_equity"] = overview.latest_balance.total_equity
        facts["cash_and_equivalents"] = overview.latest_balance.cash_and_equivalents
        facts["total_debt"] = overview.latest_balance.total_debt

    calculations = {
        "pe_ratio": overview.valuation.pe_ratio,
        "forward_pe": overview.valuation.forward_pe,
        "pb_ratio": overview.valuation.pb_ratio,
        "ev_ebitda": overview.valuation.ev_ebitda,
        "gross_margin_pct": overview.profitability.gross_margin_pct,
        "operating_margin_pct": overview.profitability.operating_margin_pct,
        "net_margin_pct": overview.profitability.net_margin_pct,
        "roe_pct": overview.profitability.roe_pct,
        "roa_pct": overview.profitability.roa_pct,
        "debt_to_equity": overview.financial_health.debt_to_equity,
        "altman_z_score": overview.financial_health.altman_z_score,
        "health_score": overview.financial_health.health_score,
    }

    unavailable = [k for k, v in calculations.items() if v is None]

    return {
        "ticker": ticker,
        "facts": facts,
        "calculations": {k: v for k, v in calculations.items() if v is not None},
        "assumptions": {
            "effective_tax_rate_normalized": "25.0%",
            "forward_earnings_growth_discount": "12.0%",
        },
        "unavailable_fields": unavailable,
        "data_provenance": {
            "source": overview.data_source.value,
            "status": overview.data_status.value,
            "last_updated": overview.updated_at,
        }
    }


# 3c. Financial Statements Tool
async def tool_get_financial_statements(
    ticker: str,
    statement_type: str = "income",
    period_type: str = "annual"
) -> Dict[str, Any]:
    """Retrieves multi-period financial statements (income, balance_sheet, cash_flow)."""
    statements = await fundamentals_service.get_statements(
        ticker,
        statement_type=statement_type,
        period_type=period_type
    )
    return statements.model_dump()


# 4. News & Sentiment Tool
async def tool_get_news(ticker: str, limit: int = 5) -> List[Dict[str, Any]]:
    """Fetches recent financial news headlines and sentiment analysis."""
    news_provider = get_news_provider(ticker)
    return await news_provider.get_news_for_ticker(ticker, limit=limit)


# 4b. Structured AI News Context Tool (Distinguishes FACT, CLASSIFICATION, ANALYSIS, UNKNOWN)
async def tool_get_news_context(ticker: str, limit: int = 5) -> Dict[str, Any]:
    """
    Retrieves rich factual news context separating:
    - FACTS: reported headlines, publication timestamps, sources, verified URLs
    - CLASSIFICATION: event types (EARNINGS, M_AND_A, etc.) and category labels
    - ANALYSIS: computed sentiment polarity scores (-1.0 to 1.0) and estimated impact horizons
    - PROVENANCE: feed source and verification status (DEMO/LIVE)
    """
    from app.services.news_service import news_service
    data = await news_service.get_news_for_ticker(ticker, limit=limit)
    items = data.get("news_items", [])

    facts = [
        {
            "headline": i.get("headline") or i.get("title"),
            "source": i.get("source"),
            "published_at": i.get("published_at"),
            "url": i.get("url"),
        }
        for i in items
    ]

    classifications = [
        {
            "headline": i.get("headline") or i.get("title"),
            "category": i.get("category", "MARKET"),
            "event_type": i.get("event_type", "OTHER"),
        }
        for i in items
    ]

    analysis = {
        "overall_sentiment": data.get("overall_sentiment", "NEUTRAL"),
        "average_sentiment_score": data.get("average_sentiment_score", 0.0),
        "article_scores": [
            {
                "headline": i.get("headline") or i.get("title"),
                "sentiment_label": i.get("sentiment_label", "NEUTRAL"),
                "sentiment_score": i.get("sentiment_score", 0.0),
                "impact_score": i.get("impact_score", 0.5),
                "impact_horizon": i.get("impact_horizon", "SHORT_TERM"),
            }
            for i in items
        ]
    }

    return {
        "ticker": ticker,
        "facts": facts,
        "classifications": classifications,
        "analysis": analysis,
        "data_provenance": {
            "source": items[0].get("data_source", "DEMO") if items else "DEMO",
            "status": items[0].get("data_status", "DEMO") if items else "DEMO",
        }
    }


# 4c. Structured AI News Brief Tool
async def tool_get_ai_news_brief(ticker: str) -> Dict[str, Any]:
    """
    Generates a structured factual executive summary for research:
    - Market Context
    - Key Company Developments
    - Potential Catalysts & Risks
    - Document & News Citations
    """
    context = await tool_get_news_context(ticker, limit=5)
    facts = context.get("facts", [])
    analysis = context.get("analysis", {})

    catalysts = []
    risks = []
    for art in analysis.get("article_scores", []):
        score = art.get("sentiment_score", 0.0)
        if score > 0.20:
            catalysts.append(f"Positive momentum: {art.get('headline')} (Score: +{score:.2f})")
        elif score < -0.20:
            risks.append(f"Downside headwind: {art.get('headline')} (Score: {score:.2f})")

    return {
        "ticker": ticker,
        "market_context": f"Active coverage for {ticker} across recent financial intelligence dispatches.",
        "key_company_news": [f["headline"] for f in facts[:3]],
        "potential_catalysts": catalysts or ["No immediate positive catalysts detected in recent headlines."],
        "potential_risks": risks or ["No acute downside risk warnings detected in current feed."],
        "overall_sentiment_bias": analysis.get("overall_sentiment", "NEUTRAL"),
        "citations": [f["source"] for f in facts if f.get("source")]
    }



# 5. Technical Indicators Tool
async def tool_technical_analysis(ticker: str) -> Dict[str, Any]:
    """Computes SMA-20/50, EMA-20, RSI-14, MACD, Bollinger Bands, ATR, and realized volatility."""
    history = await tool_get_stock_history(ticker, timeframe="6m", interval="1d")
    analyzer = TechnicalAnalyzer()
    return analyzer.calculate_all(history.get("bars", []), ticker=ticker)


# 6. Anomaly & Stress Detection Tool
async def tool_anomaly_analysis(ticker: str) -> Dict[str, Any]:
    """Runs Isolation Forest multivariate anomaly scoring, volume spikes, and GARCH volatility."""
    history = await tool_get_stock_history(ticker, timeframe="6m", interval="1d")
    detector = MarketAnomalyDetector()
    return detector.analyze_ticker(ticker, history.get("bars", []))


# 7. Correlation Analysis Tool
async def tool_correlation_analysis(method: str = "pearson") -> Dict[str, Any]:
    """Computes cross-asset rolling return correlation matrix and highlights top correlated pairs."""
    engine = CorrelationEngine()
    return await engine.compute_matrix(method=method)


# 8. Scenario & Stress Simulation Tool
async def tool_scenario_analysis(
    ticker: str,
    scenario_type: str = "MONTE_CARLO",
    days: int = 90,
    iterations: int = 3000
) -> Dict[str, Any]:
    """Executes stochastic Merton Jump Diffusion Monte Carlo or crisis stress simulation."""
    quote = await tool_get_stock_quote(ticker)
    curr_p = quote.get("price", 100.0)

    if scenario_type.upper() == "HISTORICAL_STRESS":
        tester = HistoricalStressTester()
        return tester.stress_test(ticker=ticker, current_price=curr_p)
    elif scenario_type.upper() == "MACRO_SHOCK":
        sim = MacroScenarioSimulator()
        return sim.simulate(ticker=ticker, rate_shock_bps=100.0, oil_shock_pct=20.0)
    else:
        sim = MonteCarloSimulator()
        res = sim.simulate(current_price=curr_p, days=days, iterations=iterations)
        res["ticker"] = ticker
        return res


# 9. Portfolio Risk & Holdings Tool
async def tool_portfolio_analysis() -> Dict[str, Any]:
    """Analyzes current portfolio holdings, market value, weighted beta, and daily 95% VaR."""
    return await portfolio_service.get_portfolio_summary()


# 10. Regulatory SEC Document Search Tool
async def tool_financial_document_search(query: str, ticker: Optional[str] = None, top_k: int = 3) -> List[Dict[str, Any]]:
    """Retrieves verified SEC 10-K regulatory disclosures with grounded source citations."""
    return vector_retriever.search(query=query, ticker=ticker if ticker else None, top_k=top_k)


# Alias mapping for backward compatibility
tool_run_monte_carlo = tool_scenario_analysis
tool_search_sec_filings = tool_financial_document_search
tool_get_news_sentiment = tool_get_news
