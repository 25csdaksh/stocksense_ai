"""
MarketMind AI — Research Evidence Cross-Validation Engine.
Phase 6.9: Audits multi-agent evidence consistency, detects conflicting data values,
evaluates freshness SLAs, and calculates deterministic analytical confidence levels.
"""
import uuid
from typing import List, Dict, Any, Optional
from datetime import datetime, timezone

from app.ai.models import (
    ResearchEvidence,
    EvidenceConflict,
    CrossValidationReport,
    ConfidenceLevel,
    EvidenceProvenance,
)
from app.observability.freshness_service import freshness_service


class EvidenceCrossValidator:
    """Audits evidence items for consistency, conflicts, freshness, and provenance."""

    @classmethod
    def validate_evidence(cls, evidence_list: List[ResearchEvidence]) -> CrossValidationReport:
        """Runs multi-dimensional cross-checks across all collected research evidence."""
        if not evidence_list:
            return CrossValidationReport(
                is_valid=False,
                total_evidence_count=0,
                conflicts_detected=[],
                stale_items_count=0,
                missing_fields=["ALL_EVIDENCE"],
                provenance_breakdown={},
                confidence_level=ConfidenceLevel.INSUFFICIENT,
                confidence_rationale="No research evidence could be collected for this query."
            )

        conflicts: List[EvidenceConflict] = []
        stale_count = 0
        missing_fields: List[str] = []
        prov_counts: Dict[str, int] = {}

        # 1. Track Provenance Distribution
        for ev in evidence_list:
            p_val = ev.provenance.value
            prov_counts[p_val] = prov_counts.get(p_val, 0) + 1

            if not ev.timestamp:
                missing_fields.append(f"{ev.category}.timestamp")

            # Check Freshness
            dataset_name = "quotes" if ev.category in ["MARKET", "TECHNICAL"] else "news" if ev.category == "NEWS" else "fundamentals"
            is_stale, _, _ = freshness_service.evaluate_freshness(
                dataset=dataset_name,
                timestamp_str=ev.timestamp,
                data_status="LIVE" if ev.provenance == EvidenceProvenance.LIVE else "DEMO"
            )
            if is_stale and ev.provenance not in [EvidenceProvenance.CALCULATED, EvidenceProvenance.MODEL_DERIVED]:
                stale_count += 1

        # 2. Check for metric discrepancies on the same symbol
        symbol_metric_map: Dict[str, List[ResearchEvidence]] = {}
        for ev in evidence_list:
            if ev.symbol and ev.metric:
                key = f"{ev.symbol}:{ev.metric}"
                symbol_metric_map.setdefault(key, []).append(ev)

        for key, ev_group in symbol_metric_map.items():
            if len(ev_group) > 1:
                # Compare scalar values if numeric
                vals = [e.value for e in ev_group if isinstance(e.value, (int, float))]
                if len(vals) > 1 and max(vals) - min(vals) > (min(vals) * 0.15):
                    sym, met = key.split(":", 1)
                    conflicts.append(
                        EvidenceConflict(
                            conflict_id=f"conf_{uuid.uuid4().hex[:6]}",
                            metric=met,
                            symbols=[sym],
                            conflicting_values=[
                                {"source": e.source, "value": e.value, "timestamp": e.timestamp}
                                for e in ev_group
                            ],
                            resolution="UNRESOLVED_DISCREPANCY: Sources diverge by >15%",
                            impact="HIGH"
                        )
                    )

        # 3. Determine Deterministic Confidence Level
        total_count = len(evidence_list)
        categories = {e.category for e in evidence_list}
        has_critical_categories = "MARKET" in categories or "FUNDAMENTAL" in categories

        if total_count >= 8 and len(categories) >= 3 and len(conflicts) == 0 and stale_count <= 2:
            conf_level = ConfidenceLevel.HIGH
            rationale = f"Robust multi-pillar alignment across {len(categories)} categories ({total_count} evidence items) with zero conflicts."
        elif total_count >= 4 and has_critical_categories:
            conf_level = ConfidenceLevel.MEDIUM
            rationale = f"Adequate evidence base across {len(categories)} categories; {'minor staleness detected' if stale_count > 0 else 'consistent signals'}."
        elif total_count >= 2:
            conf_level = ConfidenceLevel.LOW
            rationale = f"Limited evidence coverage ({total_count} items); interpret findings as directional."
        else:
            conf_level = ConfidenceLevel.INSUFFICIENT
            rationale = "Insufficient evidence to form reliable analytical conclusions."

        return CrossValidationReport(
            is_valid=(len(conflicts) == 0),
            total_evidence_count=total_count,
            conflicts_detected=conflicts,
            stale_items_count=stale_count,
            missing_fields=missing_fields,
            provenance_breakdown=prov_counts,
            confidence_level=conf_level,
            confidence_rationale=rationale
        )


cross_validator = EvidenceCrossValidator()
