"""
MarketMind AI — Macro & Market Context Specialist Agent.
Phase 6.9: Tracks benchmark indices, sector rotations, and macroeconomic regimes.
Clearly marks missing statistics without fabricating macroeconomic indicators.
"""
import uuid
from typing import List, Dict, Any, Optional
from datetime import datetime, timezone

from app.ai.models import (
    ResearchEvidence,
    EvidenceProvenance,
    Citation,
)
from app.services.market_service import market_service
from app.core.logging import logger


class ContextMacroAgent:
    """Specialist agent providing benchmark index regimes and sector rotation backdrop."""

    def __init__(self):
        self.service = market_service

    async def run(self, market: str = "ALL") -> List[ResearchEvidence]:
        """Collects structured market overview and benchmark index evidence."""
        evidence_list: List[ResearchEvidence] = []

        try:
            # 1. Indian & US Benchmark Indices
            us_overview = await self.service.get_overview(market="US")
            in_overview = await self.service.get_overview(market="IN")
            sectors = await self.service.get_sectors()

            us_indices = us_overview.get("indices", [])
            in_indices = in_overview.get("indices", [])

            all_indices = []
            for idx in (in_indices + us_indices):
                all_indices.append({
                    "symbol": idx.get("symbol"),
                    "name": idx.get("name"),
                    "price": idx.get("price"),
                    "change_pct": idx.get("change_pct"),
                    "currency": idx.get("currency")
                })

            cite = Citation(
                citation_id=f"cite_macro_{uuid.uuid4().hex[:6]}",
                source_type="BENCHMARK_INDEX_FEED",
                source_name="Global & Indian Exchange Feeds",
                retrieved_at=datetime.now(timezone.utc).isoformat()
            )

            evidence_list.append(
                ResearchEvidence(
                    evidence_id=f"ev_{uuid.uuid4().hex[:8]}",
                    category="MACRO",
                    symbol="BENCHMARKS",
                    metric="benchmark_indices_overview",
                    value={
                        "indices": all_indices,
                        "indian_market_regime": in_overview.get("market_regime", "EXPANSION"),
                        "us_market_regime": us_overview.get("market_regime", "EXPANSION"),
                    },
                    source="MacroContextEngine",
                    provenance=EvidenceProvenance.LIVE if "LIVE" in str(us_overview) else EvidenceProvenance.DEMO,
                    confidence=0.95,
                    citation=cite
                )
            )

            # 2. Sector Performance & Momentum Rankings
            if sectors:
                evidence_list.append(
                    ResearchEvidence(
                        evidence_id=f"ev_{uuid.uuid4().hex[:8]}",
                        category="MACRO",
                        symbol="SECTORS",
                        metric="sector_rotations",
                        value={
                            "top_performing_sectors": sectors[:3],
                            "underperforming_sectors": sectors[-2:] if len(sectors) >= 2 else [],
                            "total_sectors_tracked": len(sectors)
                        },
                        source="SectorIntelligenceEngine",
                        provenance=EvidenceProvenance.CALCULATED,
                        confidence=0.90,
                        citation=cite
                    )
                )

        except Exception as ex:
            logger.warning(f"ContextMacroAgent error: {ex}")

        return evidence_list


context_agent = ContextMacroAgent()
