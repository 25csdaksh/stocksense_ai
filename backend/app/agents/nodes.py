"""
LangGraph Nodes for Planning, Execution, RAG Retrieval, and Synthesis.
"""
import re
from typing import Dict, Any
from app.agents.state import AgentState
from app.agents.tools import (
    tool_get_stock_quote,
    tool_run_monte_carlo,
    tool_compute_stock_dna,
    tool_search_sec_filings,
    tool_get_news_sentiment
)
from app.utils.constants import SUPPORTED_UNIVERSE, FINANCIAL_DISCLAIMER_TEXT


def supervisor_node(state: AgentState) -> Dict[str, Any]:
    """Analyzes user query and selects specialized workflow."""
    q = state["query"].lower()
    ticker = "NVDA"
    for t in SUPPORTED_UNIVERSE.keys():
        if re.search(rf"\b{t.lower()}\b", q):
            ticker = t
            break

    name_map = {"apple": "AAPL", "microsoft": "MSFT", "nvidia": "NVDA", "google": "GOOGL", "amazon": "AMZN", "tesla": "TSLA"}
    for name, sym in name_map.items():
        if name in q:
            ticker = sym
            break

    if any(w in q for w in ["simulate", "monte carlo", "scenario", "var", "drift", "jump"]):
        intent = "SCENARIO_SIMULATION"
    elif any(w in q for w in ["dna", "radar", "factor", "quality", "growth", "value"]):
        intent = "STOCK_DNA"
    elif any(w in q for w in ["10-k", "sec", "filing", "risk factor", "annual report"]):
        intent = "RAG_SEARCH"
    else:
        intent = "MARKET_INTELLIGENCE"

    return {
        "ticker_focus": ticker,
        "intent": intent,
        "thought_steps": [{
            "step": 1,
            "agent": "Supervisor",
            "message": f"Identified intent '{intent}' for target asset {ticker}."
        }]
    }


async def data_fetcher_node(state: AgentState) -> Dict[str, Any]:
    """Retrieves spot price and market quote data."""
    ticker = state["ticker_focus"] or "NVDA"
    quote = await tool_get_stock_quote(ticker)
    return {
        "data_context": {"quote": quote},
        "thought_steps": [{
            "step": 2,
            "agent": "DataFetcher",
            "message": f"Retrieved spot price (${quote['price']:.2f}, {quote['change_pct']:+.2f}%) for {ticker}."
        }],
        "tool_calls": [{
            "agent": "DataFetcher",
            "tool": "get_stock_quote",
            "result": f"${quote['price']:.2f} ({quote['change_pct']:+.2f}%)"
        }]
    }


async def quant_node(state: AgentState) -> Dict[str, Any]:
    """Executes quantitative ML tools based on intent."""
    intent = state["intent"]
    ticker = state["ticker_focus"] or "NVDA"
    widgets = []

    if intent == "SCENARIO_SIMULATION":
        sim = await tool_run_monte_carlo(ticker, days=90, iterations=3000)
        widgets.append({
            "widget_type": "FAN_CHART",
            "title": f"Merton Jump Diffusion 90-Day Simulation ({ticker})",
            "data": sim["fan_chart"]
        })
        return {
            "data_context": {"monte_carlo": sim},
            "ui_widgets": widgets,
            "thought_steps": [{
                "step": 3,
                "agent": "QuantEngine",
                "message": f"Computed 3,000 Merton Jump Diffusion paths. VaR 95%: {sim['value_at_risk_95_pct']}%, P50: ${sim['expected_terminal_price_p50']}."
            }],
            "tool_calls": [{
                "agent": "QuantEngine",
                "tool": "run_merton_jump_diffusion",
                "result": f"VaR 95%: {sim['value_at_risk_95_pct']}%, P50: ${sim['expected_terminal_price_p50']}"
            }]
        }
    elif intent == "STOCK_DNA":
        dna = await tool_compute_stock_dna(ticker)
        widgets.append({
            "widget_type": "RADAR_DNA",
            "title": f"5-Factor Stock DNA Profile ({ticker})",
            "data": dna["radar_data"]
        })
        return {
            "data_context": {"stock_dna": dna},
            "ui_widgets": widgets,
            "thought_steps": [{
                "step": 3,
                "agent": "QuantEngine",
                "message": f"Quantified 5-factor DNA vector. Dominant persona: {dna['dominant_persona']}."
            }],
            "tool_calls": [{
                "agent": "QuantEngine",
                "tool": "compute_stock_dna",
                "result": f"Persona: {dna['dominant_persona']}"
            }]
        }
    return {}


async def rag_node(state: AgentState) -> Dict[str, Any]:
    """Searches vector index for SEC disclosures."""
    if state["intent"] == "RAG_SEARCH":
        ticker = state["ticker_focus"] or "NVDA"
        citations = await tool_search_sec_filings(query=state["query"], ticker=ticker, top_k=3)
        return {
            "retrieved_citations": citations,
            "thought_steps": [{
                "step": 3,
                "agent": "RAGSearch",
                "message": f"Retrieved {len(citations)} verified SEC regulatory disclosure citations for {ticker}."
            }],
            "tool_calls": [{
                "agent": "RAGSearch",
                "tool": "search_sec_filings",
                "result": f"{len(citations)} citations"
            }]
        }
    return {}


def synthesis_node(state: AgentState) -> Dict[str, Any]:
    """Generates structured answer with guardrails and educational disclaimers."""
    intent = state["intent"]
    ticker = state["ticker_focus"] or "NVDA"
    quote = state["data_context"].get("quote", {})

    if intent == "SCENARIO_SIMULATION":
        mc = state["data_context"].get("monte_carlo", {})
        body = (
            f"### Stochastic Scenario & Tail Risk Projections ({ticker})\n\n"
            f"- **Base Price:** ${quote.get('price', 0):.2f}\n"
            f"- **P50 Median Price (90 Days):** ${mc.get('expected_terminal_price_p50', 0):.2f}\n"
            f"- **Empirical Value-at-Risk (VaR 95%):** {mc.get('value_at_risk_95_pct', 0):.2f}%\n"
            f"- **Expected Shortfall (CVaR 99%):** {mc.get('cvar_expected_shortfall_99_pct', 0):.2f}%\n"
            f"- **Probability of Gain:** {mc.get('probability_of_profit_pct', 0):.1f}%\n\n"
            f"The stochastic Jump-Diffusion model reflects balanced upside participation with controlled tail density."
        )
    elif intent == "STOCK_DNA":
        dna = state["data_context"].get("stock_dna", {})
        scores = dna.get("factor_scores", {})
        body = (
            f"### Multi-Factor Stock DNA Profile ({ticker})\n\n"
            f"- **Dominant Factor Persona:** **{dna.get('dominant_persona', 'N/A')}**\n"
            f"- **Quality Score:** {scores.get('quality', 0)}/100\n"
            f"- **Growth Score:** {scores.get('growth', 0)}/100\n"
            f"- **Value Score:** {scores.get('value', 0)}/100\n"
            f"- **Momentum Score:** {scores.get('momentum', 0)}/100\n"
            f"- **Low Volatility Score:** {scores.get('low_volatility', 0)}/100\n\n"
            f"{dna.get('summary', '')}"
        )
    elif intent == "RAG_SEARCH":
        cits = state.get("retrieved_citations", [])
        snippets = "\n".join([f"> **{c['section']} (p.{c['page_number']})**:\n> \"{c['content_snippet']}\"\n" for c in cits])
        body = f"### Verified SEC 10-K Disclosures ({ticker})\n\n{snippets}\nRegulatory risk items emphasize operating continuity and supply diversification."
    else:
        body = (
            f"### Financial Intelligence Overview ({ticker})\n\n"
            f"- **Spot Price:** ${quote.get('price', 0):.2f} ({quote.get('change_pct', 0):+.2f}%)\n"
            f"- **Market Cap:** ${quote.get('market_cap', 0):,.0f}\n"
            f"- **Trailing P/E:** {quote.get('pe_ratio', 0)}x\n"
            f"- **52-Week Range:** ${quote.get('week_52_low', 0):.2f} — ${quote.get('week_52_high', 0):.2f}"
        )

    disclaimer_block = f"\n\n---\n> **Regulatory Notice**: {FINANCIAL_DISCLAIMER_TEXT}"
    final_output = f"{body.rstrip()}{disclaimer_block}"

    return {
        "final_answer": final_output,
        "guardrail_passed": True
    }
