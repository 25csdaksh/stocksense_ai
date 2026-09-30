"""
MarketMind AI — Unified Data Quality & Observability Models.
Phase 6.8: Complete domain models for data quality assessment, infrastructure telemetry,
provider health monitoring, gap detection, latency metrics, and operational failure auditing.
"""
from datetime import datetime, timezone
from enum import Enum
from typing import Dict, Any, List, Optional, Union
from pydantic import BaseModel, Field, ConfigDict


# =========================================================================
# Domain Enums
# =========================================================================

class QualityStatus(str, Enum):
    """Unified data quality and health status classification."""
    HEALTHY = "HEALTHY"        # Verified data integrity, active timestamps, zero gaps
    DEGRADED = "DEGRADED"      # Minor gaps, rate limited, or fallback demo data
    STALE = "STALE"            # Observation timestamp older than freshness SLA
    INVALID = "INVALID"        # Fails boundary constraints (e.g. low > high, negative price)
    UNAVAILABLE = "UNAVAILABLE"# Provider is unreachable or data unconfigured
    ERROR = "ERROR"            # Systematic failure / exceptions during processing


class ProviderHealthStatus(str, Enum):
    """External provider status indicator."""
    LIVE = "LIVE"
    DEMO = "DEMO"
    DEGRADED = "DEGRADED"
    DOWN = "DOWN"
    CONFIGURATION_REQUIRED = "CONFIGURATION_REQUIRED"
    AUTHENTICATION_ERROR = "AUTHENTICATION_ERROR"
    RATE_LIMITED = "RATE_LIMITED"


class AlertSeverity(str, Enum):
    """Operational alert and failure severity."""
    INFO = "INFO"
    WARNING = "WARNING"
    CRITICAL = "CRITICAL"


class ErrorCategory(str, Enum):
    """Standardized error taxonomy."""
    VALIDATION_ERROR = "VALIDATION_ERROR"
    PROVIDER_ERROR = "PROVIDER_ERROR"
    AUTHENTICATION_ERROR = "AUTHENTICATION_ERROR"
    RATE_LIMIT_ERROR = "RATE_LIMIT_ERROR"
    TIMEOUT_ERROR = "TIMEOUT_ERROR"
    NETWORK_ERROR = "NETWORK_ERROR"
    DATABASE_ERROR = "DATABASE_ERROR"
    CACHE_ERROR = "CACHE_ERROR"
    VECTOR_DB_ERROR = "VECTOR_DB_ERROR"
    AI_PROVIDER_ERROR = "AI_PROVIDER_ERROR"
    STALE_DATA = "STALE_DATA"
    DATA_GAP = "DATA_GAP"
    DUPLICATE_DATA = "DUPLICATE_DATA"
    UNKNOWN_ERROR = "UNKNOWN_ERROR"


# =========================================================================
# Data Quality Models
# =========================================================================

class QualityScoreBreakdown(BaseModel):
    """Documented deterministic score components."""
    freshness_score: float = Field(default=100.0, ge=0.0, le=100.0, description="Weight: 25%")
    completeness_score: float = Field(default=100.0, ge=0.0, le=100.0, description="Weight: 20%")
    validity_score: float = Field(default=100.0, ge=0.0, le=100.0, description="Weight: 20%")
    availability_score: float = Field(default=100.0, ge=0.0, le=100.0, description="Weight: 15%")
    consistency_score: float = Field(default=100.0, ge=0.0, le=100.0, description="Weight: 10%")
    continuity_score: float = Field(default=100.0, ge=0.0, le=100.0, description="Weight: 10%")
    overall_score: float = Field(default=100.0, ge=0.0, le=100.0)


class DataQualityReport(BaseModel):
    """Standard quality report for a dataset or asset."""
    model_config = ConfigDict(from_attributes=True)

    symbol: Optional[str] = None
    dataset: str = "market_data"  # market_data, fundamentals, news, overall
    status: QualityStatus = QualityStatus.HEALTHY
    score: float = Field(default=100.0, ge=0.0, le=100.0)
    score_breakdown: QualityScoreBreakdown = Field(default_factory=QualityScoreBreakdown)
    freshness_seconds: Optional[float] = None
    is_stale: bool = False
    data_source: str = "DEMO"
    data_status: str = "DEMO"
    total_records_checked: int = 0
    missing_fields: List[str] = Field(default_factory=list)
    validation_errors: List[str] = Field(default_factory=list)
    duplicate_count: int = 0
    gap_count: int = 0
    gaps_detected: List[Dict[str, Any]] = Field(default_factory=list)
    provider_latency_ms: Optional[float] = None
    last_updated: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())


class SymbolDataQualityReport(BaseModel):
    """Aggregated per-symbol data quality score covering all 3 pillars."""
    symbol: str
    overall_status: QualityStatus = QualityStatus.HEALTHY
    overall_score: float = Field(default=100.0, ge=0.0, le=100.0)
    market_data: DataQualityReport
    fundamentals: DataQualityReport
    news: DataQualityReport
    inspected_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())


# =========================================================================
# Provider Health & Latency Models
# =========================================================================

class LatencyMetrics(BaseModel):
    """Percentile latency metrics in milliseconds."""
    count: int = 0
    average_ms: float = 0.0
    p50_ms: float = 0.0
    p95_ms: float = 0.0
    p99_ms: float = 0.0
    max_ms: float = 0.0


class ProviderHealthReport(BaseModel):
    """Telemetry report for a single market data / news / fundamental provider."""
    provider_name: str
    market: str = "ALL"  # INDIA, US, GLOBAL
    status: ProviderHealthStatus = ProviderHealthStatus.DEMO
    last_success: Optional[str] = None
    last_failure: Optional[str] = None
    request_count: int = 0
    success_count: int = 0
    failure_count: int = 0
    error_rate_pct: float = 0.0
    latency: LatencyMetrics = Field(default_factory=LatencyMetrics)
    rate_limit_hits: int = 0
    authentication_status: str = "CONFIGURED_OR_DEMO"
    data_freshness_sec: Optional[float] = None


# =========================================================================
# Infrastructure Health Models
# =========================================================================

class ComponentHealth(BaseModel):
    name: str
    status: QualityStatus = QualityStatus.HEALTHY
    latency_ms: Optional[float] = None
    details: Dict[str, Any] = Field(default_factory=dict)
    last_checked: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())


class SystemHealthReport(BaseModel):
    """Comprehensive system observability status."""
    status: QualityStatus = QualityStatus.HEALTHY
    service: str = "MarketMind AI"
    version: str = "1.0.0"
    environment: str = "development"
    uptime_seconds: float = 0.0
    components: Dict[str, ComponentHealth] = Field(default_factory=dict)
    providers: List[ProviderHealthReport] = Field(default_factory=list)
    timestamp: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())


# =========================================================================
# Operational Failure & Alert Models
# =========================================================================

class OperationalFailureRecord(BaseModel):
    """Sanitized failure record logged for audit and dashboard inspection."""
    id: str
    timestamp: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    component: str
    provider: Optional[str] = None
    symbol: Optional[str] = None
    error_type: ErrorCategory = ErrorCategory.UNKNOWN_ERROR
    severity: AlertSeverity = AlertSeverity.WARNING
    message: str


class GlobalDataQualityReport(BaseModel):
    """Top-level platform data quality overview."""
    overall_status: QualityStatus = QualityStatus.HEALTHY
    overall_score: float = Field(default=100.0, ge=0.0, le=100.0)
    markets: Dict[str, float] = Field(default_factory=dict)
    dataset_scores: Dict[str, float] = Field(default_factory=dict)
    providers_summary: Dict[str, str] = Field(default_factory=dict)
    system_dependencies: Dict[str, str] = Field(default_factory=dict)
    recent_failures: List[OperationalFailureRecord] = Field(default_factory=list)
    generated_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
