"""
MarketMind AI — Phase 6.9 Unit Tests: Cross-Validator & Research Synthesizer.
"""
import pytest
from app.ai.models import (
    ResearchIntent,
    ResearchDepth,
    ResearchPlan,
    ResearchEvidence,
    EvidenceProvenance,
    ConfidenceLevel,
    Citation,
)
from app.ai.cross_validator import cross_validator
from app.ai.research_synthesizer import research_synthesizer


def test_cross_validator_empty_evidence():
    report = cross_validator.validate_evidence([])
    assert report.is_valid is False
    assert report.confidence_level == ConfidenceLevel.INSUFFICIENT


def test_cross_validator_conflict_detection():
    # Two conflicting price evidence items for the same symbol
    ev1 = ResearchEvidence(
        evidence_id="ev_01",
        category="MARKET",
        symbol="INFY.NS",
        metric="price",
        value=1500.0,
        source="ProviderA",
        provenance=EvidenceProvenance.LIVE
    )
    ev2 = ResearchEvidence(
        evidence_id="ev_02",
        category="MARKET",
        symbol="INFY.NS",
        metric="price",
        value=1800.0,  # 20% divergence
        source="ProviderB",
        provenance=EvidenceProvenance.LIVE
    )

    report = cross_validator.validate_evidence([ev1, ev2])
    assert len(report.conflicts_detected) == 1
    assert report.conflicts_detected[0].metric == "price"
    assert "INFY.NS" in report.conflicts_detected[0].symbols


def test_cross_validator_confidence_calculation():
    # Multi-pillar consistent evidence
    evidence = [
        ResearchEvidence(
            evidence_id=f"ev_{i}",
            category=["MARKET", "FUNDAMENTAL", "TECHNICAL", "NEWS"][i % 4],
            symbol="TCS.NS",
            metric=f"metric_{i}",
            value={"val": 100 + i},
            source="TestEngine",
            provenance=EvidenceProvenance.LIVE
        )
        for i in range(10)
    ]
    report = cross_validator.validate_evidence(evidence)
    assert report.confidence_level in [ConfidenceLevel.HIGH, ConfidenceLevel.MEDIUM]
    assert report.total_evidence_count == 10
    assert len(report.conflicts_detected) == 0


def test_research_synthesizer_guardrails_and_structure():
    plan = ResearchPlan(
        query="Analyze TCS.NS fundamentals and technical outlook",
        intent=ResearchIntent.STOCK_RESEARCH,
        symbols=["TCS.NS"],
        selected_agents=["market_agent", "fundamental_agent", "quant_agent"]
    )
    evidence = [
        ResearchEvidence(
            evidence_id="ev_01",
            category="MARKET",
            symbol="TCS.NS",
            metric="latest_price",
            value={"price": 3900.0, "change_pct": 1.2, "volume": 1200000, "currency": "INR"},
            source="NSE",
            provenance=EvidenceProvenance.LIVE,
            citation=Citation(citation_id="cite_01", source_name="NSE India")
        ),
        ResearchEvidence(
            evidence_id="ev_02",
            category="FUNDAMENTAL",
            symbol="TCS.NS",
            metric="valuation_ratios",
            value={"pe_ratio": 28.5, "pb_ratio": 12.1, "market_cap": "14T INR"},
            source="FundamentalsEngine",
            provenance=EvidenceProvenance.CALCULATED
        ),
        ResearchEvidence(
            evidence_id="ev_03",
            category="TECHNICAL",
            symbol="TCS.NS",
            metric="momentum_oscillators",
            value={"rsi_14": 56.4, "rsi_interpretation": "Neutral momentum band (30-70)", "macd_line": 12.0, "macd_signal": 10.0},
            source="AnalyticsEngine",
            provenance=EvidenceProvenance.CALCULATED
        )
    ]
    val_report = cross_validator.validate_evidence(evidence)
    report = research_synthesizer.synthesize_report(
        query="Analyze TCS.NS fundamentals and technical outlook",
        plan=plan,
        evidence_list=evidence,
        validation_report=val_report
    )

    # 1. Verify 12 core sections & fields
    assert report.report_id is not None
    assert report.executive_summary is not None
    assert report.market_context is not None
    assert report.fundamental_analysis is not None
    assert report.technical_analysis is not None
    assert report.research_conclusion is not None
    assert len(report.citations) >= 1
    assert len(report.limitations) >= 1
    assert report.provenance_summary is not None

    # 2. Strict Financial Safety: No buy/sell advice or guarantees
    all_text = f"{report.executive_summary} {report.research_conclusion}".upper()
    assert "BUY NOW" not in all_text
    assert "SELL NOW" not in all_text
    assert "GUARANTEED" not in all_text
