"""
MarketMind AI — Phase 6.9 Unit Tests: Research Models & Evidence Graph.
"""
import pytest
from app.ai.models import (
    ResearchIntent,
    ResearchDepth,
    TaskStatus,
    EvidenceProvenance,
    ConfidenceLevel,
    EdgeType,
    ResearchTask,
    ResearchPlan,
    Citation,
    ResearchEvidence,
    EvidenceNode,
    EvidenceEdge,
    EvidenceConflict,
    CrossValidationReport,
    ResearchReport,
)
from app.ai.evidence.graph import EvidenceGraph


def test_research_intent_enum_coverage():
    assert len(ResearchIntent) == 14
    assert ResearchIntent.STOCK_RESEARCH == "STOCK_RESEARCH"
    assert ResearchIntent.STOCK_COMPARISON == "STOCK_COMPARISON"
    assert ResearchIntent.FUNDAMENTAL_ANALYSIS == "FUNDAMENTAL_ANALYSIS"
    assert ResearchIntent.TECHNICAL_ANALYSIS == "TECHNICAL_ANALYSIS"
    assert ResearchIntent.NEWS_ANALYSIS == "NEWS_ANALYSIS"
    assert ResearchIntent.ANOMALY_ANALYSIS == "ANOMALY_ANALYSIS"
    assert ResearchIntent.RISK_ANALYSIS == "RISK_ANALYSIS"
    assert ResearchIntent.PORTFOLIO_ANALYSIS == "PORTFOLIO_ANALYSIS"
    assert ResearchIntent.SCENARIO_ANALYSIS == "SCENARIO_ANALYSIS"
    assert ResearchIntent.HISTORICAL_ANALYSIS == "HISTORICAL_ANALYSIS"
    assert ResearchIntent.FINANCIAL_DOCUMENT_ANALYSIS == "FINANCIAL_DOCUMENT_ANALYSIS"
    assert ResearchIntent.MARKET_OVERVIEW == "MARKET_OVERVIEW"
    assert ResearchIntent.SECTOR_ANALYSIS == "SECTOR_ANALYSIS"
    assert ResearchIntent.GENERAL_FINANCIAL_RESEARCH == "GENERAL_FINANCIAL_RESEARCH"


def test_research_depth_and_provenance_enums():
    assert ResearchDepth.QUICK == "QUICK"
    assert ResearchDepth.STANDARD == "STANDARD"
    assert ResearchDepth.DEEP == "DEEP"

    assert EvidenceProvenance.LIVE == "LIVE"
    assert EvidenceProvenance.DEMO == "DEMO"
    assert EvidenceProvenance.STALE == "STALE"
    assert EvidenceProvenance.UNAVAILABLE == "UNAVAILABLE"
    assert EvidenceProvenance.CALCULATED == "CALCULATED"
    assert EvidenceProvenance.MODEL_DERIVED == "MODEL_DERIVED"


def test_citation_and_evidence_creation():
    cite = Citation(
        citation_id="cite_001",
        source_type="SEC_FILING",
        source_name="Form 10-K FY2024",
        source_url="https://sec.gov/edgar/123",
        document_id="doc_123",
        chunk_id="chunk_4"
    )
    assert cite.citation_id == "cite_001"
    assert cite.source_name == "Form 10-K FY2024"

    ev = ResearchEvidence(
        evidence_id="ev_001",
        category="FUNDAMENTAL",
        symbol="RELIANCE.NS",
        metric="pe_ratio",
        value=24.5,
        source="NSEIndia",
        provenance=EvidenceProvenance.LIVE,
        confidence=0.98,
        citation=cite
    )
    assert ev.category == "FUNDAMENTAL"
    assert ev.symbol == "RELIANCE.NS"
    assert ev.value == 24.5
    assert ev.citation is not None
    assert ev.citation.citation_id == "cite_001"


def test_evidence_graph_ingestion():
    graph = EvidenceGraph()

    ev1 = ResearchEvidence(
        evidence_id="ev_mkt_01",
        category="MARKET",
        symbol="TCS.NS",
        metric="latest_price",
        value={"price": 3850.0},
        source="ZerodhaKite",
        provenance=EvidenceProvenance.LIVE
    )
    ev2 = ResearchEvidence(
        evidence_id="ev_tech_01",
        category="TECHNICAL",
        symbol="TCS.NS",
        metric="rsi_14",
        value=58.2,
        source="AnalyticsEngine",
        provenance=EvidenceProvenance.CALCULATED
    )

    graph.ingest_evidence(ev1)
    graph.ingest_evidence(ev2)

    nodes = graph.get_nodes()
    edges = graph.get_edges()

    # Should contain TCS company node and 2 evidence nodes
    assert len(nodes) >= 3
    assert len(edges) >= 2

    graph_dict = graph.to_dict()
    assert graph_dict["total_nodes"] >= 3
    assert graph_dict["total_edges"] >= 2
