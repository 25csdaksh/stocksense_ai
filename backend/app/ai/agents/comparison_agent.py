"""
MarketMind AI — Comparative Intelligence Specialist Agent.
Phase 6.9: Produces objective side-by-side comparative evidence matrices across valuation,
growth, momentum, and risk without declaring subjective "winners" or biased buy/sell advice.
"""
import uuid
from typing import List, Dict, Any, Optional
from datetime import datetime, timezone

from app.ai.models import (
    ResearchEvidence,
    EvidenceProvenance,
)
from app.core.logging import logger


class ComparativeResearchAgent:
    """Specialist agent aligning multi-ticker metrics into objective side-by-side comparison matrices."""

    async def run(
        self,
        symbols: List[str],
        market_evidence: List[ResearchEvidence],
        fundamental_evidence: List[ResearchEvidence],
        technical_evidence: List[ResearchEvidence],
        risk_evidence: List[ResearchEvidence]
    ) -> List[ResearchEvidence]:
        """Aligns multi-source evidence into comparative dimensions."""
        if len(symbols) < 2:
            return []

        evidence_list: List[ResearchEvidence] = []

        try:
            comparison_matrix: Dict[str, Dict[str, Any]] = {}

            for s in symbols:
                comparison_matrix[s] = {
                    "symbol": s,
                    "latest_price": None,
                    "pe_ratio": None,
                    "pb_ratio": None,
                    "operating_margin_pct": None,
                    "roe_pct": None,
                    "rsi_14": None,
                    "trend_regime": None,
                    "annualized_volatility_pct": None,
                    "max_drawdown_pct": None
                }

            # Map Market Evidence
            for ev in market_evidence:
                if ev.symbol in comparison_matrix and ev.metric == "latest_price" and isinstance(ev.value, dict):
                    comparison_matrix[ev.symbol]["latest_price"] = ev.value.get("price")

            # Map Fundamental Evidence
            for ev in fundamental_evidence:
                if ev.symbol in comparison_matrix:
                    if ev.metric == "valuation_ratios" and isinstance(ev.value, dict):
                        comparison_matrix[ev.symbol]["pe_ratio"] = ev.value.get("pe_ratio")
                        comparison_matrix[ev.symbol]["pb_ratio"] = ev.value.get("pb_ratio")
                    elif ev.metric == "profitability_and_margins" and isinstance(ev.value, dict):
                        comparison_matrix[ev.symbol]["operating_margin_pct"] = ev.value.get("operating_margin_pct")
                        comparison_matrix[ev.symbol]["roe_pct"] = ev.value.get("roe_pct")

            # Map Technical Evidence
            for ev in technical_evidence:
                if ev.symbol in comparison_matrix:
                    if ev.metric == "momentum_oscillators" and isinstance(ev.value, dict):
                        comparison_matrix[ev.symbol]["rsi_14"] = ev.value.get("rsi_14")
                    elif ev.metric == "trend_and_moving_averages" and isinstance(ev.value, dict):
                        comparison_matrix[ev.symbol]["trend_regime"] = ev.value.get("trend_regime")

            # Map Risk Evidence
            for ev in risk_evidence:
                if ev.symbol in comparison_matrix and ev.metric == "downside_risk_profile" and isinstance(ev.value, dict):
                    comparison_matrix[ev.symbol]["annualized_volatility_pct"] = ev.value.get("annualized_volatility_pct")
                    comparison_matrix[ev.symbol]["max_drawdown_pct"] = ev.value.get("max_drawdown_pct")

            evidence_list.append(
                ResearchEvidence(
                    evidence_id=f"ev_{uuid.uuid4().hex[:8]}",
                    category="COMPARISON",
                    symbol=None,
                    metric="side_by_side_comparison_matrix",
                    value={
                        "compared_symbols": symbols,
                        "metrics_matrix": list(comparison_matrix.values()),
                        "comparison_summary": f"Side-by-side multi-factor alignment across {len(symbols)} assets."
                    },
                    source="ComparativeAnalyticsEngine",
                    provenance=EvidenceProvenance.CALCULATED,
                    confidence=0.95
                )
            )

        except Exception as ex:
            logger.warning(f"ComparativeResearchAgent error: {ex}")

        return evidence_list


comparison_agent = ComparativeResearchAgent()
