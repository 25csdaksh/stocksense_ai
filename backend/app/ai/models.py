"""
MarketMind AI — Advanced Multi-Agent Financial Research Models.
Phase 6.9: Strongly typed domain models for query understanding, research planning,
structured multi-pillar evidence, cross-validation, citations, and analytical reports.
"""
from datetime import datetime, timezone
from enum import Enum
from typing import Dict, Any, List, Optional, Union
from pydantic import BaseModel, Field, ConfigDict


# =========================================================================
# Domain Enums
# =========================================================================

class ResearchIntent(str, Enum):
    """Supported specialized research intents."""
    STOCK_RESEARCH = "STOCK_RESEARCH"
    STOCK_COMPARISON = "STOCK_COMPARISON"
    FUNDAMENTAL_ANALYSIS = "FUNDAMENTAL_ANALYSIS"
    TECHNICAL_ANALYSIS = "TECHNICAL_ANALYSIS"
    NEWS_ANALYSIS = "NEWS_ANALYSIS"
    ANOMALY_ANALYSIS = "ANOMALY_ANALYSIS"
    RISK_ANALYSIS = "RISK_ANALYSIS"
    PORTFOLIO_ANALYSIS = "PORTFOLIO_ANALYSIS"
    SCENARIO_ANALYSIS = "SCENARIO_ANALYSIS"
    HISTORICAL_ANALYSIS = "HISTORICAL_ANALYSIS"
    FINANCIAL_DOCUMENT_ANALYSIS = "FINANCIAL_DOCUMENT_ANALYSIS"
    MARKET_OVERVIEW = "MARKET_OVERVIEW"
    SECTOR_ANALYSIS = "SECTOR_ANALYSIS"
    GENERAL_FINANCIAL_RESEARCH = "GENERAL_FINANCIAL_RESEARCH"


class ResearchDepth(str, Enum):
    """Execution depth and agent scope."""
    QUICK = "QUICK"          # Market quote, technical snapshot, recent news
    STANDARD = "STANDARD"    # Market, technical, fundamentals, news, risk
    DEEP = "DEEP"            # All specialist agents, RAG, anomalies, scenarios, cross-validation


class TaskStatus(str, Enum):
    """Specialist agent task lifecycle state."""
    PENDING = "PENDING"
    RUNNING = "RUNNING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    SKIPPED = "SKIPPED"


class EvidenceProvenance(str, Enum):
    """Source data provenance and reliability tier."""
    LIVE = "LIVE"
    DEMO = "DEMO"
    STALE = "STALE"
    UNAVAILABLE = "UNAVAILABLE"
    CALCULATED = "CALCULATED"
    MODEL_DERIVED = "MODEL_DERIVED"


class ConfidenceLevel(str, Enum):
    """Deterministic analytical confidence classification."""
    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"
    INSUFFICIENT = "INSUFFICIENT"


class EdgeType(str, Enum):
    """Typed relationship edges in the Evidence Graph."""
    SUPPORTS = "SUPPORTS"
    CONTRADICTS = "CONTRADICTS"
    ASSOCIATED_WITH = "ASSOCIATED_WITH"
    DERIVED_FROM = "DERIVED_FROM"
    REFERENCES = "REFERENCES"
    TEMPORALLY_RELATED = "TEMPORALLY_RELATED"


# =========================================================================
# Research Planning & Task Models
# =========================================================================

class ResearchTask(BaseModel):
    """Individual specialist agent execution step."""
    task_id: str
    agent: str
    objective: str
    status: TaskStatus = TaskStatus.PENDING
    started_at: Optional[str] = None
    completed_at: Optional[str] = None
    error: Optional[str] = None


class ResearchPlan(BaseModel):
    """Structured execution blueprint created by the Supervisor Agent."""
    query: str
    intent: ResearchIntent = ResearchIntent.GENERAL_FINANCIAL_RESEARCH
    symbols: List[str] = Field(default_factory=list)
    date_range: Optional[str] = "6m"
    requested_metrics: List[str] = Field(default_factory=list)
    selected_agents: List[str] = Field(default_factory=list)
    required_tools: List[str] = Field(default_factory=list)
    research_depth: ResearchDepth = ResearchDepth.STANDARD
    tasks: List[ResearchTask] = Field(default_factory=list)
    created_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())


# =========================================================================
# Citation & Evidence Models
# =========================================================================

class Citation(BaseModel):
    """Factual citation anchoring research statements to verified source data."""
    citation_id: str
    source_type: str = "PROVIDER"  # PROVIDER, SEC_FILING, NEWS_ARTICLE, MODEL, DATABASE
    source_name: str
    source_url: Optional[str] = None
    published_at: Optional[str] = None
    retrieved_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    document_id: Optional[str] = None
    chunk_id: Optional[str] = None
    excerpt: Optional[str] = None


class ResearchEvidence(BaseModel):
    """Atomic structured evidence unit emitted by specialist agents."""
    model_config = ConfigDict(from_attributes=True)

    evidence_id: str
    category: str  # MARKET, FUNDAMENTAL, TECHNICAL, NEWS, RISK, ANOMALY, RAG, MACRO, COMPARISON
    symbol: Optional[str] = None
    metric: str
    value: Any
    source: str
    timestamp: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    provenance: EvidenceProvenance = EvidenceProvenance.DEMO
    confidence: float = Field(default=1.0, ge=0.0, le=1.0)
    citation: Optional[Citation] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)


# =========================================================================
# Evidence Graph Models
# =========================================================================

class EvidenceNode(BaseModel):
    id: str
    node_type: str  # Company, Stock, Metric, NewsArticle, Anomaly, TechnicalSignal, Document, RiskMetric
    label: str
    properties: Dict[str, Any] = Field(default_factory=dict)


class EvidenceEdge(BaseModel):
    source_id: str
    target_id: str
    edge_type: EdgeType = EdgeType.ASSOCIATED_WITH
    weight: float = 1.0
    description: Optional[str] = None


# =========================================================================
# Cross-Validation & Conflict Models
# =========================================================================

class EvidenceConflict(BaseModel):
    """Discrepancy detected across multiple data sources or timeframes."""
    conflict_id: str
    metric: str
    symbols: List[str] = Field(default_factory=list)
    conflicting_values: List[Dict[str, Any]] = Field(default_factory=list)
    resolution: str = "UNRESOLVED_DISCREPANCY"
    impact: str = "MEDIUM"


class CrossValidationReport(BaseModel):
    """Audit of evidence consistency, staleness, and provenance."""
    is_valid: bool = True
    total_evidence_count: int = 0
    conflicts_detected: List[EvidenceConflict] = Field(default_factory=list)
    stale_items_count: int = 0
    missing_fields: List[str] = Field(default_factory=list)
    provenance_breakdown: Dict[str, int] = Field(default_factory=dict)
    confidence_level: ConfidenceLevel = ConfidenceLevel.HIGH
    confidence_rationale: str = "High consistency across multi-source verified data."


# =========================================================================
# Research Report Models
# =========================================================================

class ResearchReport(BaseModel):
    """Unified comprehensive multi-agent financial research report."""
    report_id: str
    query: str
    generated_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    symbols: List[str] = Field(default_factory=list)
    time_range: Optional[str] = "6m"
    intent: ResearchIntent = ResearchIntent.GENERAL_FINANCIAL_RESEARCH
    research_depth: ResearchDepth = ResearchDepth.STANDARD
    
    # Analytical Report Sections
    executive_summary: str
    market_context: Optional[str] = None
    fundamental_analysis: Optional[str] = None
    technical_analysis: Optional[str] = None
    news_analysis: Optional[str] = None
    risk_analysis: Optional[str] = None
    anomaly_analysis: Optional[str] = None
    scenario_analysis: Optional[str] = None
    comparison_analysis: Optional[str] = None
    evidence_conflicts: List[EvidenceConflict] = Field(default_factory=list)
    unknowns: List[str] = Field(default_factory=list)
    research_conclusion: str
    
    # Audit & Provenance Metadata
    confidence_level: ConfidenceLevel = ConfidenceLevel.MEDIUM
    confidence_rationale: str = ""
    provenance_summary: Dict[str, str] = Field(default_factory=dict)
    citations: List[Citation] = Field(default_factory=list)
    limitations: List[str] = Field(default_factory=list)
