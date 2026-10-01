"""
MarketMind AI — Fundamental Research Specialist Agent.
Phase 6.9: Extracts financial statements, profitability metrics, valuation multiples,
solvency ratios, and Altman Z-scores. Strictly preserves factual vs calculated provenance.
"""
import uuid
from typing import List, Dict, Any, Optional
from datetime import datetime, timezone

from app.ai.models import (
    ResearchEvidence,
    EvidenceProvenance,
    Citation,
)
from app.services.fundamentals_service import FundamentalsService
from app.providers.market_data.symbol_normalizer import normalize_symbol
from app.core.logging import logger


class FundamentalResearchAgent:
    """Specialist agent analyzing corporate financials, earnings, valuation, and balance sheet health."""

    def __init__(self):
        self.service = FundamentalsService()

    async def run(self, symbols: List[str]) -> List[ResearchEvidence]:
        """Collects structured fundamentals evidence for the target symbols."""
        evidence_list: List[ResearchEvidence] = []

        if not symbols:
            return evidence_list

        for raw_sym in symbols:
            try:
                norm = normalize_symbol(raw_sym)
                canonical = norm.canonical_symbol

                overview = await self.service.get_overview(canonical)
                profile = await self.service.get_company_profile(canonical)

                ov_dict = overview.model_dump() if overview else {}
                prof_dict = profile.model_dump() if profile else {}

                data_source = ov_dict.get("data_source", "FUNDAMENTALS_PROVIDER")
                data_status = ov_dict.get("data_status", "DEMO")
                prov_enum = EvidenceProvenance.LIVE if str(data_status).upper() == "LIVE" else EvidenceProvenance.DEMO

                cite = Citation(
                    citation_id=f"cite_{uuid.uuid4().hex[:6]}",
                    source_type="FINANCIAL_REPORT",
                    source_name=f"{data_source} - Corporate Financials",
                    retrieved_at=datetime.now(timezone.utc).isoformat()
                )

                # 1. Company Profile & Sector Context
                if prof_dict:
                    evidence_list.append(
                        ResearchEvidence(
                            evidence_id=f"ev_{uuid.uuid4().hex[:8]}",
                            category="FUNDAMENTAL",
                            symbol=canonical,
                            metric="company_profile",
                            value={
                                "name": prof_dict.get("company_name") or prof_dict.get("name"),
                                "sector": prof_dict.get("sector", "General"),
                                "industry": prof_dict.get("industry", "General"),
                                "exchange": prof_dict.get("exchange", "NSE"),
                                "currency": prof_dict.get("currency", "INR"),
                                "description": (prof_dict.get("description") or "")[:200] + "..." if prof_dict.get("description") else ""
                            },
                            source=data_source,
                            provenance=prov_enum,
                            confidence=1.0,
                            citation=cite
                        )
                    )

                # 2. Valuation & Financial Ratios
                ratios = ov_dict.get("ratios") or {}
                if ratios:
                    evidence_list.append(
                        ResearchEvidence(
                            evidence_id=f"ev_{uuid.uuid4().hex[:8]}",
                            category="FUNDAMENTAL",
                            symbol=canonical,
                            metric="valuation_ratios",
                            value={
                                "pe_ratio": ratios.get("pe_ratio"),
                                "pb_ratio": ratios.get("pb_ratio"),
                                "ev_to_ebitda": ratios.get("ev_to_ebitda"),
                                "dividend_yield_pct": ratios.get("dividend_yield_pct") or ratios.get("dividend_yield"),
                                "market_cap": ov_dict.get("market_cap"),
                            },
                            source=data_source,
                            provenance=prov_enum,
                            confidence=0.95,
                            citation=cite
                        )
                    )

                    # 3. Profitability & Efficiency Ratios
                    evidence_list.append(
                        ResearchEvidence(
                            evidence_id=f"ev_{uuid.uuid4().hex[:8]}",
                            category="FUNDAMENTAL",
                            symbol=canonical,
                            metric="profitability_and_margins",
                            value={
                                "operating_margin_pct": ratios.get("operating_margin_pct"),
                                "net_profit_margin_pct": ratios.get("net_profit_margin_pct"),
                                "roe_pct": ratios.get("roe_pct"),
                                "roa_pct": ratios.get("roa_pct"),
                                "eps": ratios.get("eps"),
                            },
                            source=data_source,
                            provenance=EvidenceProvenance.CALCULATED,
                            confidence=0.95,
                            citation=cite
                        )
                    )

                    # 4. Solvency & Balance Sheet Health
                    evidence_list.append(
                        ResearchEvidence(
                            evidence_id=f"ev_{uuid.uuid4().hex[:8]}",
                            category="FUNDAMENTAL",
                            symbol=canonical,
                            metric="solvency_and_health",
                            value={
                                "debt_to_equity": ratios.get("debt_to_equity"),
                                "current_ratio": ratios.get("current_ratio"),
                                "quick_ratio": ratios.get("quick_ratio"),
                                "altman_z_score": ratios.get("altman_z_score"),
                                "health_classification": (
                                    "SAFE_ZONE" if (ratios.get("altman_z_score") or 0) > 2.99
                                    else "GREY_ZONE" if (ratios.get("altman_z_score") or 0) > 1.81
                                    else "DISTRESS_RISK" if ratios.get("altman_z_score") is not None
                                    else "NOT_CALCULATED"
                                )
                            },
                            source=data_source,
                            provenance=EvidenceProvenance.CALCULATED,
                            confidence=0.90,
                            citation=cite
                        )
                    )

            except Exception as ex:
                logger.warning(f"FundamentalResearchAgent error for {raw_sym}: {ex}")
                evidence_list.append(
                    ResearchEvidence(
                        evidence_id=f"ev_{uuid.uuid4().hex[:8]}",
                        category="FUNDAMENTAL",
                        symbol=raw_sym,
                        metric="fundamentals_status",
                        value={"status": "UNAVAILABLE", "error": str(ex)[:80]},
                        source="FundamentalsProvider",
                        provenance=EvidenceProvenance.UNAVAILABLE,
                        confidence=0.2
                    )
                )

        return evidence_list


fundamental_agent = FundamentalResearchAgent()
