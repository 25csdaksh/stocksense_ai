"""
Evaluation & Benchmarking Framework for Financial RAG & AI Multi-Agent Systems.
Provides metrics for faithfulness, answer relevance, citation precision, and tool routing accuracy.
"""
from typing import List, Dict, Any, Optional
import re


class AgentEvaluationSuite:
    """Evaluates agent responses, citation grounding, and tool execution precision."""

    @staticmethod
    def evaluate_faithfulness(answer: str, retrieved_contexts: List[str]) -> float:
        """
        Computes the ratio of factual claims in the answer that are substantiated by the retrieved context.
        Returns a score between 0.0 and 1.0.
        """
        if not retrieved_contexts or not answer:
            return 1.0 if not answer else 0.5

        combined_context = " ".join(retrieved_contexts).lower()
        sentences = [s.strip() for s in re.split(r"[.\n]", answer) if len(s.strip()) > 15]

        if not sentences:
            return 1.0

        grounded_count = 0
        for sent in sentences:
            words = [w for w in re.findall(r"\w+", sent.lower()) if len(w) > 3]
            if not words:
                grounded_count += 1
                continue
            match_ratio = sum(1 for w in words if w in combined_context) / len(words)
            if match_ratio >= 0.40:
                grounded_count += 1

        return round(min(1.0, grounded_count / len(sentences)), 4)

    @staticmethod
    def evaluate_citation_precision(citations: List[Dict[str, Any]], expected_tickers: List[str]) -> float:
        """Evaluates whether retrieved citations correspond accurately to the target entities."""
        if not citations:
            return 1.0 if not expected_tickers else 0.0

        target_set = {t.upper() for t in expected_tickers}
        matching = sum(1 for c in citations if c.get("ticker", "").upper() in target_set)
        return round(matching / len(citations), 4)

    @staticmethod
    def evaluate_tool_selection(intent: str, executed_tools: List[str]) -> Dict[str, Any]:
        """Evaluates whether the agent invoked the optimal tools for the detected intent."""
        expected_tool_mapping = {
            "SCENARIO_SIMULATION": ["get_stock_quote", "run_merton_jump_diffusion", "scenario_analysis"],
            "STOCK_DNA": ["get_stock_quote", "compute_stock_dna"],
            "RAG_SEARCH": ["search_sec_filings", "financial_document_search"],
            "TECHNICAL_ANALYSIS": ["get_stock_quote", "technical_analysis"],
            "MARKET_INTELLIGENCE": ["get_stock_quote"]
        }

        expected = expected_tool_mapping.get(intent, ["get_stock_quote"])
        matched = [t for t in executed_tools if any(e in t for e in expected)]

        return {
            "intent": intent,
            "executed_tools": executed_tools,
            "expected_tool_types": expected,
            "precision_score": round(len(matched) / max(1, len(executed_tools)), 2),
            "is_valid": len(matched) > 0
        }


agent_evaluator = AgentEvaluationSuite()
