"""
Unit Tests for AI Safety Guardrails, Anti-Hallucination & RAG Evaluation.
"""
import pytest
from app.agents.guardrails import financial_guardrails
from app.agents.evaluation import agent_evaluator
from app.utils.constants import FINANCIAL_DISCLAIMER_TEXT


def test_guardrails_soften_prohibited_trading_directives():
    raw_response = (
        "This is a guaranteed return and a risk-free trade! "
        "You must buy this now before it doubles in value."
    )
    sanitized, passed, warnings = financial_guardrails.inspect_and_sanitize(
        answer=raw_response,
        data_context={},
        citations=[]
    )

    assert "risk-free" not in sanitized.lower()
    assert "buy this now" not in sanitized.lower()
    assert len(warnings) > 0
    assert FINANCIAL_DISCLAIMER_TEXT in sanitized


def test_guardrails_remove_ungrounded_citations():
    raw_response = (
        "According to [Source 1], revenue increased by 20%. "
        "Furthermore, [Source 99] claims margins will reach 90%."
    )
    citations = [
        {"id": "sec_1", "ticker": "AAPL", "content_snippet": "Revenue increased by 20%"}
    ]

    sanitized, passed, warnings = financial_guardrails.inspect_and_sanitize(
        answer=raw_response,
        data_context={},
        citations=citations
    )

    assert "[Source 1]" in sanitized
    assert "[Source 99]" not in sanitized


def test_evaluation_faithfulness_metric():
    contexts = [
        "NVIDIA Compute & Networking revenue increased 217% to $47.4 billion driven by Hopper HGX datacenter demand.",
        "Datacenter customers transitioned from CPU architectures to accelerated GPU computing."
    ]
    grounded_answer = "NVIDIA's Compute and Networking segment generated $47.4 billion in revenue, growing 217%."
    hallucinated_answer = "NVIDIA acquired AMD for $100 billion in cash and stock to dominate quantum computing."

    grounded_score = agent_evaluator.evaluate_faithfulness(grounded_answer, contexts)
    hallucinated_score = agent_evaluator.evaluate_faithfulness(hallucinated_answer, contexts)

    assert grounded_score >= 0.70
    assert hallucinated_score < 0.40


def test_evaluation_tool_selection_precision():
    eval_sim = agent_evaluator.evaluate_tool_selection(
        intent="SCENARIO_SIMULATION",
        executed_tools=["get_stock_quote", "run_merton_jump_diffusion"]
    )
    assert eval_sim["precision_score"] == 1.0
    assert eval_sim["is_valid"] is True

    eval_rag = agent_evaluator.evaluate_tool_selection(
        intent="RAG_SEARCH",
        executed_tools=["search_sec_filings"]
    )
    assert eval_rag["is_valid"] is True
