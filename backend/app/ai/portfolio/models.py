"""
MarketMind AI — Portfolio Copilot & Personal Research Memory Domain Models.
Phase 6.10: Strongly typed domain models for user portfolio context, holding intelligence,
concentration analysis, memory search, change detection, factual alerts, and daily briefs.
"""
from datetime import datetime, timezone
from enum import Enum
from typing import Dict, Any, List, Optional, Union
from pydantic import BaseModel, Field, ConfigDict
from app.ai.models import (
    ResearchDepth,
    ConfidenceLevel,
    EvidenceProvenance,
    Citation,
    ResearchEvidence,
    ResearchPlan,
)


# =========================================================================
# Domain Enums
# =========================================================================

class PortfolioCopilotMode(str, Enum):
    """Supported specialized copilot execution modes."""
    PORTFOLIO_OVERVIEW = "PORTFOLIO_OVERVIEW"
    HOLDING_RESEARCH = "HOLDING_RESEARCH"
    WATCHLIST_RESEARCH = "WATCHLIST_RESEARCH"
    CHANGE_ANALYSIS = "CHANGE_ANALYSIS"
    RISK_REVIEW = "RISK_REVIEW"
    NEWS_REVIEW = "NEWS_REVIEW"
    SCENARIO_REVIEW = "SCENARIO_REVIEW"
    WEEKLY_REVIEW = "WEEKLY_REVIEW"
    DAILY_BRIEF = "DAILY_BRIEF"


class AlertSeverity(str, Enum):
    """Factual alert severity classification."""
    INFO = "INFO"
    WARNING = "WARNING"
    CRITICAL = "CRITICAL"


class AlertRuleType(str, Enum):
    """Supported trigger types for portfolio and watchlist alerts."""
    PRICE_MOVE_PCT = "PRICE_MOVE_PCT"
    VOLATILITY_THRESHOLD = "VOLATILITY_THRESHOLD"
    VOLUME_SURGE = "VOLUME_SURGE"
    WEIGHT_THRESHOLD = "WEIGHT_THRESHOLD"
    SECTOR_EXPOSURE_THRESHOLD = "SECTOR_EXPOSURE_THRESHOLD"
    DRAWDOWN_THRESHOLD = "DRAWDOWN_THRESHOLD"
    ANOMALY_DETECTED = "ANOMALY_DETECTED"
    NEWS_SENTIMENT_SHIFT = "NEWS_SENTIMENT_SHIFT"
    STALE_DATA = "STALE_DATA"
    RESEARCH_CHANGE_DETECTED = "RESEARCH_CHANGE_DETECTED"


# =========================================================================
# Holding & Portfolio Context Models
# =========================================================================

class PortfolioHoldingContext(BaseModel):
    """Comprehensive factual snapshot for an individual portfolio holding."""
    model_config = ConfigDict(from_attributes=True)

    ticker: str
    exchange: str = "NSE"
    quantity: float
    average_cost: float
    current_price: float
    invested_value: float
    market_value: float
    absolute_pnl: float
    percentage_pnl: float
    portfolio_weight_pct: float
    sector: str = "General"
    beta: float = 1.0
    volatility_pct: Optional[float] = None
    max_drawdown_pct: Optional[float] = None
    var_95_daily_pct: Optional[float] = None
    correlation_cluster: Optional[str] = None
    latest_news_context: Optional[str] = None
    latest_anomaly_context: Optional[str] = None
    pe_ratio: Optional[float] = None
    rsi_14: Optional[float] = None
    data_freshness: str = "FRESH"
    provenance: EvidenceProvenance = EvidenceProvenance.DEMO
    data_status: str = "DEMO"


class PortfolioUserContext(BaseModel):
    """Aggregated portfolio intelligence strictly scoped to the authenticated user."""
    model_config = ConfigDict(from_attributes=True)

    user_id: str
    portfolio_id: Optional[str] = None
    name: str = "Primary Portfolio"
    total_market_value: float = 0.0
    invested_capital: float = 0.0
    cash_balance: float = 0.0
    total_value: float = 0.0
    absolute_pnl: float = 0.0
    percentage_pnl: float = 0.0
    daily_pnl: float = 0.0
    daily_pnl_pct: float = 0.0
    holdings: List[PortfolioHoldingContext] = Field(default_factory=list)
    holdings_count: int = 0
    
    # Concentration & Exposure Metrics
    sector_allocations: Dict[str, float] = Field(default_factory=dict)
    top_holding_symbol: Optional[str] = None
    top_holding_weight_pct: float = 0.0
    top3_exposure_pct: float = 0.0
    top5_exposure_pct: float = 0.0
    herfindahl_index: float = 0.0
    
    # Risk Metrics
    weighted_beta: float = 1.0
    annualized_volatility_pct: float = 0.0
    max_drawdown_pct: float = 0.0
    var_95_daily_pct: float = 0.0
    downside_deviation_pct: float = 0.0
    sharpe_ratio: float = 0.0
    sortino_ratio: float = 0.0
    tracking_error_pct: float = 0.0
    
    provenance: EvidenceProvenance = EvidenceProvenance.DEMO
    data_status: str = "DEMO"


# =========================================================================
# Watchlist Context Models
# =========================================================================

class WatchlistItemContext(BaseModel):
    """Contextual metrics for an asset tracked on user watchlist."""
    ticker: str
    added_at: str
    current_price: float
    change_pct: float
    target_price: Optional[float] = None
    notes: Optional[str] = None
    rsi_14: Optional[float] = None
    volatility_pct: Optional[float] = None
    pe_ratio: Optional[float] = None
    latest_sentiment: Optional[str] = None
    has_anomaly: bool = False
    data_freshness: str = "FRESH"
    provenance: EvidenceProvenance = EvidenceProvenance.DEMO


class WatchlistContext(BaseModel):
    """Watchlist intelligence and aggregated alerts for user watchlist."""
    user_id: str
    items: List[WatchlistItemContext] = Field(default_factory=list)
    total_items: int = 0
    news_summary: Optional[str] = None
    anomalies_detected: int = 0


# =========================================================================
# Portfolio Pillar Summaries (Risk, News, Anomalies)
# =========================================================================

class PortfolioRiskContext(BaseModel):
    """Detailed downside risk, factor sensitivity, and scenario exposures."""
    portfolio_volatility_pct: float = 0.0
    weighted_beta: float = 1.0
    var_95_daily_pct: float = 0.0
    max_drawdown_pct: float = 0.0
    downside_deviation_pct: float = 0.0
    sharpe_ratio: float = 0.0
    sortino_ratio: float = 0.0
    single_position_concentration: Dict[str, float] = Field(default_factory=dict)
    sector_concentration: Dict[str, float] = Field(default_factory=dict)
    top_holdings_exposure_pct: float = 0.0
    correlation_clusters: List[Dict[str, Any]] = Field(default_factory=list)
    stress_scenarios: Dict[str, Any] = Field(default_factory=dict)
    monte_carlo_summary: Dict[str, Any] = Field(default_factory=dict)
    provenance: EvidenceProvenance = EvidenceProvenance.CALCULATED


class PortfolioNewsContext(BaseModel):
    """Portfolio-level news aggregation, sentiment distribution, and key developments."""
    articles_count: int = 0
    dominant_sentiment: str = "NEUTRAL"
    sentiment_score: float = 0.0
    sentiment_distribution: Dict[str, int] = Field(default_factory=dict)
    holding_news_map: Dict[str, List[Dict[str, Any]]] = Field(default_factory=dict)
    sector_news_concentration: Dict[str, int] = Field(default_factory=dict)
    high_impact_articles: List[Dict[str, Any]] = Field(default_factory=list)
    provenance: EvidenceProvenance = EvidenceProvenance.MODEL_DERIVED


class PortfolioAnomalyContext(BaseModel):
    """Portfolio-wide statistical outliers, return spikes, and volume surge flags."""
    total_anomalies: int = 0
    holding_anomalies_map: Dict[str, List[Dict[str, Any]]] = Field(default_factory=dict)
    anomaly_types: List[str] = Field(default_factory=list)
    portfolio_anomaly_concentration: Dict[str, int] = Field(default_factory=dict)
    associative_summary: str = "No abnormal volatility or return surges observed across holdings."
    provenance: EvidenceProvenance = EvidenceProvenance.MODEL_DERIVED


# =========================================================================
# Research Memory & Context Models
# =========================================================================

class ResearchMemoryItem(BaseModel):
    """User-scoped snapshot of a previous research inquiry."""
    model_config = ConfigDict(from_attributes=True)

    research_id: str
    query: str
    symbols: List[str] = Field(default_factory=list)
    intent: str
    execution_depth: str = "STANDARD"
    created_at: str
    report_summary: Optional[str] = None
    evidence_count: int = 0
    confidence_level: str = "MEDIUM"
    confidence_rationale: Optional[str] = None
    provenance_summary: Dict[str, Any] = Field(default_factory=dict)
    key_metrics: Dict[str, Any] = Field(default_factory=dict)
    cited_sources: List[Dict[str, Any]] = Field(default_factory=list)
    data_status: str = "DEMO"
    research_version: str = "6.10"


class ResearchMemoryContext(BaseModel):
    """User's historical research context enabling memory recall and change detection."""
    user_id: str
    total_memories: int = 0
    recent_memories: List[ResearchMemoryItem] = Field(default_factory=list)
    target_symbol_memory: Optional[ResearchMemoryItem] = None


class UserResearchContext(BaseModel):
    """Unified user context bundle encapsulating portfolio, watchlist, and research history."""
    user_id: str
    portfolio: PortfolioUserContext
    watchlist: WatchlistContext
    memory: ResearchMemoryContext
    risk: PortfolioRiskContext
    news: PortfolioNewsContext
    anomaly: PortfolioAnomalyContext


# =========================================================================
# Change Detection & Comparison Models
# =========================================================================

class PortfolioChangeItem(BaseModel):
    """Factual change detected between historical research / prior state and current data."""
    metric: str
    symbol: Optional[str] = None
    previous_value: Any
    current_value: Any
    absolute_change: Optional[Union[float, str]] = None
    percentage_change: Optional[float] = None
    description: str
    previous_date: Optional[str] = None
    current_date: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    change_type: str = "METRIC_UPDATE"  # METRIC_UPDATE, WEIGHT_SHIFT, RISK_SHIFT, SENTIMENT_CHANGE


class PortfolioChangeReport(BaseModel):
    """Audit of deterministic changes since previous research sessions or daily snapshots."""
    total_changes: int = 0
    holding_changes: List[PortfolioChangeItem] = Field(default_factory=list)
    risk_changes: List[PortfolioChangeItem] = Field(default_factory=list)
    valuation_changes: List[PortfolioChangeItem] = Field(default_factory=list)
    research_changes: List[PortfolioChangeItem] = Field(default_factory=list)
    summary: str = "No material deviations detected relative to previous baseline."


# =========================================================================
# Daily Brief & Alert Models
# =========================================================================

class DailyPortfolioBrief(BaseModel):
    """Structured daily intelligence brief summarizing portfolio shifts, news, and anomalies."""
    date: str
    user_id: str
    portfolio_summary: Dict[str, Any]
    daily_movers: List[Dict[str, Any]] = Field(default_factory=list)
    top_news: List[Dict[str, Any]] = Field(default_factory=list)
    anomalies: List[Dict[str, Any]] = Field(default_factory=list)
    risk_status: Dict[str, Any] = Field(default_factory=dict)
    concentration_status: Dict[str, Any] = Field(default_factory=dict)
    watchlist_highlights: List[Dict[str, Any]] = Field(default_factory=list)
    changes_since_yesterday: List[PortfolioChangeItem] = Field(default_factory=list)
    limitations: List[str] = Field(default_factory=list)
    provenance_summary: Dict[str, str] = Field(default_factory=dict)


class PortfolioAlertRuleModel(BaseModel):
    """User-configured rule evaluating portfolio and watchlist thresholds."""
    model_config = ConfigDict(from_attributes=True)

    rule_id: str
    user_id: str
    portfolio_id: Optional[str] = None
    symbol: Optional[str] = None
    rule_type: str
    threshold: float
    timeframe: str = "1d"
    is_active: bool = True
    created_at: str


class PortfolioAlertEventModel(BaseModel):
    """Individual factual alert event notification."""
    model_config = ConfigDict(from_attributes=True)

    alert_id: str
    user_id: str
    portfolio_id: Optional[str] = None
    symbol: Optional[str] = None
    alert_type: str
    title: str
    message: str
    severity: str = "INFO"
    trigger_metric: Optional[str] = None
    trigger_value: Optional[float] = None
    threshold_value: Optional[float] = None
    provenance: str = "DEMO"
    is_read: bool = False
    created_at: str


# =========================================================================
# Copilot Query Request & Response Schemas
# =========================================================================

class PortfolioCopilotQueryRequest(BaseModel):
    """User prompt and copilot execution parameters."""
    query: str = Field(..., min_length=2)
    mode: PortfolioCopilotMode = PortfolioCopilotMode.PORTFOLIO_OVERVIEW
    depth: ResearchDepth = ResearchDepth.STANDARD
    symbols_override: Optional[List[str]] = None
    session_id: Optional[str] = "copilot_default_session"


class PortfolioCopilotQueryResponse(BaseModel):
    """Comprehensive factual portfolio copilot analysis and report."""
    query: str
    mode: str
    session_id: str
    research_plan: Dict[str, Any]
    user_context: PortfolioUserContext
    report: Dict[str, Any]
    changes: Optional[PortfolioChangeReport] = None
    risks: Optional[PortfolioRiskContext] = None
    scenarios: Optional[Dict[str, Any]] = None
    citations: List[Dict[str, Any]] = Field(default_factory=list)
    provenance: Dict[str, str] = Field(default_factory=dict)
    limitations: List[str] = Field(default_factory=list)
    guardrail_passed: bool = True
    cached: bool = False
