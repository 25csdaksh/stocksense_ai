"""
MarketMind AI — Deterministic Data Quality Score Engine.
Phase 6.8: Mathematical evaluation of financial data integrity across 6 weighted dimensions:
- Freshness (25%)
- Completeness (20%)
- Validity (20%)
- Availability (15%)
- Consistency (10%)
- Continuity (10%)
"""
from typing import Dict, Any, List, Optional
from app.observability.models import (
    QualityScoreBreakdown,
    QualityStatus,
    DataQualityReport,
)


class DataQualityEngine:
    """Calculates non-financial data quality scores and health statuses."""

    # Documented Weight Distribution
    WEIGHT_FRESHNESS = 0.25
    WEIGHT_COMPLETENESS = 0.20
    WEIGHT_VALIDITY = 0.20
    WEIGHT_AVAILABILITY = 0.15
    WEIGHT_CONSISTENCY = 0.10
    WEIGHT_CONTINUITY = 0.10

    @classmethod
    def calculate_score(
        cls,
        freshness_score: float = 100.0,
        completeness_score: float = 100.0,
        validity_score: float = 100.0,
        availability_score: float = 100.0,
        consistency_score: float = 100.0,
        continuity_score: float = 100.0
    ) -> QualityScoreBreakdown:
        """
        Calculates the composite data quality index (0-100) strictly from input dimension scores.
        """
        f = max(0.0, min(100.0, freshness_score))
        comp = max(0.0, min(100.0, completeness_score))
        v = max(0.0, min(100.0, validity_score))
        a = max(0.0, min(100.0, availability_score))
        cons = max(0.0, min(100.0, consistency_score))
        cont = max(0.0, min(100.0, continuity_score))

        overall = (
            f * cls.WEIGHT_FRESHNESS +
            comp * cls.WEIGHT_COMPLETENESS +
            v * cls.WEIGHT_VALIDITY +
            a * cls.WEIGHT_AVAILABILITY +
            cons * cls.WEIGHT_CONSISTENCY +
            cont * cls.WEIGHT_CONTINUITY
        )

        return QualityScoreBreakdown(
            freshness_score=round(f, 2),
            completeness_score=round(comp, 2),
            validity_score=round(v, 2),
            availability_score=round(a, 2),
            consistency_score=round(cons, 2),
            continuity_score=round(cont, 2),
            overall_score=round(overall, 2)
        )

    @classmethod
    def derive_status_from_score(
        cls,
        score: float,
        is_invalid: bool = False,
        is_stale: bool = False,
        is_unavailable: bool = False
    ) -> QualityStatus:
        """Derives standard health status enum from numerical score and flags."""
        if is_invalid:
            return QualityStatus.INVALID
        if is_unavailable:
            return QualityStatus.UNAVAILABLE
        if is_stale:
            return QualityStatus.STALE
        if score >= 90.0:
            return QualityStatus.HEALTHY
        if score >= 65.0:
            return QualityStatus.DEGRADED
        return QualityStatus.ERROR


quality_engine = DataQualityEngine()
