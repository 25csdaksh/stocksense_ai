/**
 * MarketMind AI — Portfolio Copilot & Personal Research Memory Frontend Types.
 * Phase 6.10: Type definitions for copilot modes, user context, change detection, alerts, and daily brief.
 */

export type PortfolioCopilotMode =
  | "PORTFOLIO_OVERVIEW"
  | "HOLDING_RESEARCH"
  | "WATCHLIST_RESEARCH"
  | "CHANGE_ANALYSIS"
  | "RISK_REVIEW"
  | "NEWS_REVIEW"
  | "SCENARIO_REVIEW"
  | "WEEKLY_REVIEW"
  | "DAILY_BRIEF";

export interface PortfolioHoldingContext {
  ticker: string;
  exchange: string;
  quantity: number;
  average_cost: number;
  current_price: number;
  invested_value: number;
  market_value: number;
  absolute_pnl: number;
  percentage_pnl: number;
  portfolio_weight_pct: number;
  sector: string;
  beta: number;
  volatility_pct?: number | null;
  max_drawdown_pct?: number | null;
  var_95_daily_pct?: number | null;
  correlation_cluster?: string | null;
  latest_news_context?: string | null;
  latest_anomaly_context?: string | null;
  pe_ratio?: number | null;
  rsi_14?: number | null;
  data_freshness: string;
  provenance: string;
  data_status: string;
}

export interface PortfolioUserContext {
  user_id: string;
  portfolio_id?: string | null;
  name: string;
  total_market_value: number;
  invested_capital: number;
  cash_balance: number;
  total_value: number;
  absolute_pnl: number;
  percentage_pnl: number;
  daily_pnl: number;
  daily_pnl_pct: number;
  holdings: PortfolioHoldingContext[];
  holdings_count: number;
  sector_allocations: Record<string, number>;
  top_holding_symbol?: string | null;
  top_holding_weight_pct: number;
  top3_exposure_pct: number;
  top5_exposure_pct: number;
  herfindahl_index: number;
  weighted_beta: number;
  annualized_volatility_pct: number;
  max_drawdown_pct: number;
  var_95_daily_pct: number;
  downside_deviation_pct: number;
  sharpe_ratio: number;
  sortino_ratio: number;
  tracking_error_pct: number;
  provenance: string;
  data_status: string;
}

export interface WatchlistItemContext {
  ticker: string;
  added_at: string;
  current_price: number;
  change_pct: number;
  target_price?: number | null;
  notes?: string | null;
  rsi_14?: number | null;
  volatility_pct?: number | null;
  pe_ratio?: number | null;
  latest_sentiment?: string | null;
  has_anomaly?: boolean;
  data_freshness: string;
  provenance: string;
}

export interface WatchlistContext {
  user_id: string;
  items: WatchlistItemContext[];
  total_items: number;
  news_summary?: string | null;
  anomalies_detected: number;
}

export interface PortfolioRiskContext {
  portfolio_volatility_pct: number;
  weighted_beta: number;
  var_95_daily_pct: number;
  max_drawdown_pct: number;
  downside_deviation_pct: number;
  sharpe_ratio: number;
  sortino_ratio: number;
  single_position_concentration: Record<string, number>;
  sector_concentration: Record<string, number>;
  top_holdings_exposure_pct: number;
  correlation_clusters: Array<{
    cluster_name: string;
    symbols: string[];
    aggregate_weight_pct: number;
    avg_inter_correlation: number;
  }>;
  stress_scenarios: Record<
    string,
    {
      name: string;
      projected_drawdown_pct: number;
      status: string;
    }
  >;
  monte_carlo_summary: {
    simulations_count?: number;
    confidence_interval_95?: { lower_pnl_pct: number; upper_pnl_pct: number };
    median_return_pct?: number;
    methodology?: string;
    status?: string;
  };
  provenance: string;
}

export interface PortfolioNewsContext {
  articles_count: number;
  dominant_sentiment: string;
  sentiment_score: number;
  sentiment_distribution: Record<string, number>;
  holding_news_map: Record<string, Array<Record<string, any>>>;
  high_impact_articles: Array<Record<string, any>>;
  provenance: string;
}

export interface PortfolioAnomalyContext {
  total_anomalies: number;
  holding_anomalies_map: Record<string, Array<Record<string, any>>>;
  anomaly_types: string[];
  portfolio_anomaly_concentration: Record<string, number>;
  associative_summary: string;
  provenance: string;
}

export interface ResearchMemoryItem {
  research_id: string;
  query: string;
  symbols: string[];
  intent: string;
  execution_depth: string;
  created_at: string;
  report_summary?: string | null;
  evidence_count: number;
  confidence_level: string;
  confidence_rationale?: string | null;
  provenance_summary: Record<string, any>;
  key_metrics: Record<string, any>;
  cited_sources: Array<Record<string, any>>;
  data_status: string;
  research_version: string;
}

export interface ResearchMemoryContext {
  user_id: string;
  total_memories: number;
  recent_memories: ResearchMemoryItem[];
  target_symbol_memory?: ResearchMemoryItem | null;
}

export interface PortfolioChangeItem {
  metric: string;
  symbol?: string | null;
  previous_value: any;
  current_value: any;
  absolute_change?: number | string | null;
  percentage_change?: number | null;
  description: string;
  previous_date?: string | null;
  current_date: string;
  change_type: string;
}

export interface PortfolioChangeReport {
  total_changes: number;
  holding_changes: PortfolioChangeItem[];
  risk_changes: PortfolioChangeItem[];
  valuation_changes: PortfolioChangeItem[];
  research_changes: PortfolioChangeItem[];
  summary: string;
}

export interface DailyPortfolioBrief {
  date: string;
  user_id: string;
  portfolio_summary: {
    total_market_value: number;
    daily_pnl: number;
    daily_pnl_pct: number;
    holdings_count: number;
    weighted_beta: number;
    annualized_volatility_pct: number;
    top_sector: string;
  };
  daily_movers: Array<{
    symbol: string;
    price: number;
    weight_pct: number;
    pnl_pct: number;
  }>;
  top_news: Array<Record<string, any>>;
  anomalies: string[];
  risk_status: {
    volatility_status: string;
    var_95_daily_pct: number;
    max_drawdown_pct: number;
  };
  concentration_status: {
    herfindahl_index: number;
    top3_exposure_pct: number;
    top_holding: string;
  };
  watchlist_highlights: Array<{
    symbol: string;
    price: number;
    change_pct: number;
  }>;
  changes_since_yesterday: PortfolioChangeItem[];
  limitations: string[];
  provenance_summary: Record<string, string>;
}

export interface PortfolioAlertRule {
  rule_id: string;
  user_id: string;
  portfolio_id?: string | null;
  symbol?: string | null;
  rule_type: string;
  threshold: number;
  timeframe: string;
  is_active: boolean;
  created_at: string;
}

export interface PortfolioAlertEvent {
  alert_id: string;
  user_id: string;
  portfolio_id?: string | null;
  symbol?: string | null;
  alert_type: string;
  title: string;
  message: string;
  severity: "INFO" | "WARNING" | "CRITICAL";
  trigger_metric?: string | null;
  trigger_value?: number | null;
  threshold_value?: number | null;
  provenance: string;
  is_read: boolean;
  created_at: string;
}

export interface PortfolioCopilotResponse {
  query: string;
  mode: string;
  session_id: string;
  research_plan: Record<string, any>;
  user_context: PortfolioUserContext;
  report: {
    title?: string;
    executive_summary?: string;
    portfolio_exposure?: string;
    risk_profile?: string;
    news_intelligence?: string;
    anomalies?: string;
    changes_and_alerts?: string;
    conclusion?: string;
  };
  changes?: PortfolioChangeReport | null;
  risks?: PortfolioRiskContext | null;
  scenarios?: Record<string, any> | null;
  citations: Array<{
    citation_id: string;
    source_type: string;
    source_name: string;
    retrieved_at: string;
  }>;
  provenance: Record<string, string>;
  limitations: string[];
  guardrail_passed: boolean;
  cached: boolean;
  answer?: string;
  thought_steps?: Array<{ step: number; agent: string; message: string }>;
}
