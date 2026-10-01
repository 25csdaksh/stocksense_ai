"""
MarketMind AI — Supervisor & Router Agent.
Phase 6.9: Understands natural language queries, detects research intent across 14 categories,
extracts target entities/tickers, determines time horizons, and creates optimized execution plans.
"""
import re
import uuid
from typing import List, Dict, Any, Optional
from datetime import datetime, timezone

from app.ai.models import (
    ResearchIntent,
    ResearchDepth,
    ResearchPlan,
    ResearchTask,
    TaskStatus,
)
from app.providers.market_data.symbol_normalizer import (
    normalize_symbol,
    INDIAN_EQUITY_SYMBOLS,
    US_INDICES_MAP,
    INDIAN_INDICES_MAP
)

COMMON_STOP_WORDS = {
    "THE", "AND", "OR", "FOR", "WITH", "WHY", "WHAT", "HOW", "WHEN", "WHERE", "WHO",
    "ANALYZE", "ANALYSIS", "COMPARE", "VERSUS", "AGAINST", "STOCK", "STOCKS", "PRICE",
    "PRICES", "VALUATION", "GROWTH", "RISK", "RISKS", "TECHNICAL", "TECHNICALS",
    "FUNDAMENTAL", "FUNDAMENTALS", "NEWS", "HEADLINES", "RECENT", "PAST", "LATEST",
    "OVERVIEW", "DEEP", "DIVE", "STUDY", "EXPLAIN", "REPORT", "OUTLOOK", "BEHAVIOR",
    "INDICATORS", "TELL", "ME", "ABOUT", "THIS", "THAT", "FROM", "INTO", "UNDER",
    "ACROSS", "BETTER", "THAN", "SHOW", "SPIKE", "DROP", "FALL", "GAIN", "IS", "ARE",
    "WAS", "WERE", "CAN", "COULD", "SHOULD", "WOULD", "WILL", "DO", "DOES", "DID",
    "HAVE", "HAS", "HAD", "MY", "YOUR", "OUR", "ITS", "ALL", "SOME", "ANY", "EACH",
    "TREND", "TRENDS", "MOMENTUM", "DRAWDOWN", "VOLATILITY", "PORTFOLIO", "SCENARIO",
    "SUMMARY", "SUMMARIZE", "EXPOSURE", "EXPOSED", "SECTOR", "SECTORS", "MARKET", "MARKETS"
}

KNOWN_US_TICKERS = {
    "AAPL", "MSFT", "NVDA", "AMZN", "GOOGL", "GOOG", "META", "TSLA", "JPM", "BAC",
    "WMT", "AMD", "NFLX", "INTC", "DIS", "V", "MA", "SPY", "QQQ", "DIA", "IWM"
}


class SupervisorAgent:
    """Classifies user queries and formulates structured multi-agent research plans."""

    # Keywords for intent detection
    INTENT_KEYWORDS: List[tuple[ResearchIntent, List[str]]] = [
        (ResearchIntent.STOCK_COMPARISON, ["compare", "vs", "versus", "against", "better than", "relative to", "comparison"]),
        (ResearchIntent.ANOMALY_ANALYSIS, ["anomaly", "unusual", "spike", "outlier", "weird", "abnormal", "divergence", "jump", "flash"]),
        (ResearchIntent.FUNDAMENTAL_ANALYSIS, ["fundamental", "pe ratio", "pb ratio", "balance sheet", "revenue", "profit", "margin", "roe", "roa", "debt", "cash flow", "earnings", "valuation"]),
        (ResearchIntent.TECHNICAL_ANALYSIS, ["technical", "rsi", "macd", "moving average", "sma", "ema", "bollinger", "support", "resistance", "breakout", "trend", "momentum"]),
        (ResearchIntent.NEWS_ANALYSIS, ["news", "headline", "article", "sentiment", "event", "press release", "filing update"]),
        (ResearchIntent.RISK_ANALYSIS, ["risk", "drawdown", "var", "value at risk", "beta", "volatility", "tail risk", "exposure", "downside"]),
        (ResearchIntent.SCENARIO_ANALYSIS, ["scenario", "stress test", "monte carlo", "crash", "recession", "rate hike", "what if", "inflation spike"]),
        (ResearchIntent.PORTFOLIO_ANALYSIS, ["portfolio", "holdings", "allocation", "weight", "rebalance", "my stocks"]),
        (ResearchIntent.FINANCIAL_DOCUMENT_ANALYSIS, ["10-k", "10k", "10-q", "10q", "annual report", "sec filing", "regulatory filing", "financial statement notes"]),
        (ResearchIntent.SECTOR_ANALYSIS, ["sector", "industry", "banking sector", "it sector", "pharma sector", "auto sector", "energy sector"]),
        (ResearchIntent.MARKET_OVERVIEW, ["market overview", "market regime", "nifty", "sensex", "s&p 500", "nasdaq", "indices", "macro market"]),
        (ResearchIntent.HISTORICAL_ANALYSIS, ["historical", "history", "past 5 years", "all time high", "previous drawdown", "long term performance"]),
        (ResearchIntent.STOCK_RESEARCH, ["analyze", "research", "overview", "deep dive", "report on", "tell me about", "stock analysis"]),
    ]

    @classmethod
    def extract_symbols(cls, query: str) -> List[str]:
        """Extracts recognizable stock symbols and benchmark index tickers from query text."""
        symbols: List[str] = []

        # 1. Explicit symbols with suffix (.NS, .BO) or prefix (^)
        explicit_matches = re.findall(r"\b[A-Z0-9\^]+\.(?:NS|BO)\b|\^[A-Z0-9]+", query.upper())
        for em in explicit_matches:
            try:
                norm = normalize_symbol(em)
                if norm.canonical_symbol not in symbols:
                    symbols.append(norm.canonical_symbol)
            except Exception:
                pass

        # 2. Known Index Names (NIFTY, SENSEX, etc.)
        for idx_alias in INDIAN_INDICES_MAP.keys():
            if re.search(rf"\b{re.escape(idx_alias)}\b", query, re.IGNORECASE):
                try:
                    norm = normalize_symbol(idx_alias)
                    if norm.canonical_symbol not in symbols:
                        symbols.append(norm.canonical_symbol)
                except Exception:
                    pass

        # 3. Known Indian Equities dictionary
        words = re.findall(r"\b[A-Za-z0-9_]{2,15}\b", query)
        for w in words:
            upper_w = w.upper()
            if upper_w in COMMON_STOP_WORDS:
                continue
            if upper_w in INDIAN_EQUITY_SYMBOLS:
                canonical = f"{upper_w}.NS"
                if canonical not in symbols:
                    symbols.append(canonical)
            elif upper_w in KNOWN_US_TICKERS:
                if upper_w not in symbols:
                    symbols.append(upper_w)

        return symbols

    @classmethod
    def detect_intent(cls, query: str, symbols: List[str]) -> ResearchIntent:
        """Determines the primary analytical intent of the user prompt."""
        q_lower = query.lower()

        # If 2+ symbols detected and comparison terms present
        if len(symbols) >= 2 and any(k in q_lower for k in ["vs", "compare", "versus", "against", "better", "comparison"]):
            return ResearchIntent.STOCK_COMPARISON

        for intent, keywords in cls.INTENT_KEYWORDS:
            if any(k in q_lower for k in keywords):
                return intent

        if len(symbols) == 1:
            return ResearchIntent.STOCK_RESEARCH

        return ResearchIntent.GENERAL_FINANCIAL_RESEARCH

    @classmethod
    def determine_horizon(cls, query: str) -> str:
        """Determines the target timeframe from query."""
        q = query.lower()
        if "1 year" in q or "1y" in q or "12 month" in q:
            return "1y"
        if "5 year" in q or "5y" in q:
            return "5y"
        if "1 month" in q or "1m" in q or "30 day" in q:
            return "1m"
        if "3 month" in q or "3m" in q:
            return "3m"
        return "6m"

    @classmethod
    def create_plan(
        cls,
        query: str,
        depth: ResearchDepth = ResearchDepth.STANDARD,
        symbols_override: Optional[List[str]] = None
    ) -> ResearchPlan:
        """Formulates an optimized multi-agent execution plan."""
        symbols = symbols_override if symbols_override is not None else cls.extract_symbols(query)
        intent = cls.detect_intent(query, symbols)
        time_horizon = cls.determine_horizon(query)

        selected_agents: List[str] = []
        required_tools: List[str] = []
        tasks: List[ResearchTask] = []

        # Supervisor Task
        tasks.append(
            ResearchTask(
                task_id=f"task_{uuid.uuid4().hex[:6]}",
                agent="supervisor_agent",
                objective="Query parsing, intent detection, and entity routing",
                status=TaskStatus.COMPLETED
            )
        )

        # Agent selection based on intent and depth
        if intent == ResearchIntent.STOCK_COMPARISON:
            selected_agents = ["market_agent", "fundamental_agent", "quant_agent", "news_agent", "comparison_agent"]
            required_tools = ["get_quote", "get_history", "get_fundamentals", "get_news", "compare_metrics"]
        elif intent == ResearchIntent.FUNDAMENTAL_ANALYSIS:
            selected_agents = ["fundamental_agent", "market_agent", "rag_agent"]
            required_tools = ["get_fundamentals", "get_company_profile", "search_filings"]
        elif intent == ResearchIntent.TECHNICAL_ANALYSIS:
            selected_agents = ["quant_agent", "market_agent", "anomaly_agent"]
            required_tools = ["get_history", "calculate_indicators", "detect_anomalies"]
        elif intent == ResearchIntent.NEWS_ANALYSIS:
            selected_agents = ["news_agent", "market_agent"]
            required_tools = ["get_news", "get_sentiment_summary"]
        elif intent == ResearchIntent.ANOMALY_ANALYSIS:
            selected_agents = ["anomaly_agent", "market_agent", "news_agent"]
            required_tools = ["detect_anomalies", "get_history", "get_news"]
        elif intent == ResearchIntent.RISK_ANALYSIS:
            selected_agents = ["risk_agent", "quant_agent", "market_agent"]
            required_tools = ["calculate_risk_metrics", "calculate_var", "get_drawdown"]
        elif depth == ResearchDepth.QUICK:
            selected_agents = ["market_agent", "quant_agent", "news_agent"]
            required_tools = ["get_quote", "get_history", "get_news"]
        elif depth == ResearchDepth.DEEP:
            selected_agents = [
                "market_agent", "fundamental_agent", "quant_agent",
                "news_agent", "risk_agent", "anomaly_agent", "rag_agent", "context_agent"
            ]
            required_tools = [
                "get_quote", "get_history", "get_fundamentals", "get_news",
                "calculate_indicators", "detect_anomalies", "calculate_risk", "search_filings"
            ]
        else:  # STANDARD
            selected_agents = ["market_agent", "fundamental_agent", "quant_agent", "news_agent", "risk_agent"]
            required_tools = ["get_quote", "get_history", "get_fundamentals", "get_news", "calculate_indicators"]

        for agent in selected_agents:
            tasks.append(
                ResearchTask(
                    task_id=f"task_{uuid.uuid4().hex[:6]}",
                    agent=agent,
                    objective=f"Execute {agent.replace('_', ' ')} domain analysis for target entities",
                    status=TaskStatus.PENDING
                )
            )

        return ResearchPlan(
            query=query,
            intent=intent,
            symbols=symbols,
            date_range=time_horizon,
            selected_agents=selected_agents,
            required_tools=required_tools,
            research_depth=depth,
            tasks=tasks,
            created_at=datetime.now(timezone.utc).isoformat()
        )


supervisor_agent = SupervisorAgent()
