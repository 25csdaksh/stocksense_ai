/**
 * MarketMind AI — Data Quality & Observability Types.
 * Phase 6.8: Type definitions for system health, provider telemetry,
 * 3-pillar data quality scoring, gap detection, and sanitized failure logging.
 */

export type QualityStatus = "HEALTHY" | "DEGRADED" | "STALE" | "INVALID" | "UNAVAILABLE" | "ERROR";

export type ProviderHealthStatus = "LIVE" | "DEMO" | "DEGRADED" | "DOWN" | "CONFIGURATION_REQUIRED" | "AUTHENTICATION_ERROR" | "RATE_LIMITED";

export type AlertSeverity = "INFO" | "WARNING" | "CRITICAL";

export type ErrorCategory =
  | "VALIDATION_ERROR"
  | "PROVIDER_ERROR"
  | "AUTHENTICATION_ERROR"
  | "RATE_LIMIT_ERROR"
  | "TIMEOUT_ERROR"
  | "NETWORK_ERROR"
  | "DATABASE_ERROR"
  | "CACHE_ERROR"
  | "VECTOR_DB_ERROR"
  | "AI_PROVIDER_ERROR"
  | "STALE_DATA"
  | "DATA_GAP"
  | "DUPLICATE_DATA"
  | "UNKNOWN_ERROR";

export interface QualityScoreBreakdown {
  freshness_score: number;
  completeness_score: number;
  validity_score: number;
  availability_score: number;
  consistency_score: number;
  continuity_score: number;
  overall_score: number;
}

export interface DataQualityReport {
  symbol?: string;
  dataset: string;
  status: QualityStatus;
  score: number;
  score_breakdown: QualityScoreBreakdown;
  freshness_seconds?: number;
  is_stale: boolean;
  data_source: string;
  data_status: string;
  total_records_checked: number;
  missing_fields: string[];
  validation_errors: string[];
  duplicate_count: number;
  gap_count: number;
  gaps_detected: Array<{
    from_timestamp?: string;
    to_timestamp?: string;
    gap_duration_hours?: number;
    gap_duration_minutes?: number;
    severity?: string;
  }>;
  provider_latency_ms?: number;
  last_updated: string;
}

export interface SymbolDataQualityReport {
  symbol: string;
  overall_status: QualityStatus;
  overall_score: number;
  market_data: DataQualityReport;
  fundamentals: DataQualityReport;
  news: DataQualityReport;
  inspected_at: string;
}

export interface LatencyMetrics {
  count: number;
  average_ms: number;
  p50_ms: number;
  p95_ms: number;
  p99_ms: number;
  max_ms: number;
}

export interface ProviderHealthReport {
  provider_name: string;
  market: string;
  status: ProviderHealthStatus;
  last_success?: string;
  last_failure?: string;
  request_count: number;
  success_count: number;
  failure_count: number;
  error_rate_pct: number;
  latency: LatencyMetrics;
  rate_limit_hits: number;
  authentication_status: string;
  data_freshness_sec?: number;
}

export interface ComponentHealth {
  name: string;
  status: QualityStatus;
  latency_ms?: number;
  details: Record<string, any>;
  last_checked: string;
}

export interface SystemHealthReport {
  status: QualityStatus;
  service: string;
  version: string;
  environment: string;
  uptime_seconds: number;
  components: Record<string, ComponentHealth>;
  providers: ProviderHealthReport[];
  timestamp: string;
}

export interface OperationalFailureRecord {
  id: string;
  timestamp: string;
  component: string;
  provider?: string;
  symbol?: string;
  error_type: ErrorCategory;
  severity: AlertSeverity;
  message: string;
}

export interface GlobalDataQualityReport {
  overall_status: QualityStatus;
  overall_score: number;
  markets: Record<string, number>;
  dataset_scores: Record<string, number>;
  providers_summary: Record<string, string>;
  system_dependencies: Record<string, string>;
  recent_failures: OperationalFailureRecord[];
  generated_at: string;
}
