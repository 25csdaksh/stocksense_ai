// Common / Core Types
export type Currency = 'INR' | 'USD';

export interface PaginatedResponse<T> {
  items: T[];
  total: number;
  page: number;
  page_size: number;
  pages: number;
}

export interface ApiError {
  detail: string;
  code?: string;
  status?: number;
}

// User & Authentication Types
export interface User {
  id: string;
  email: string;
  username: string;
  full_name?: string | null;
  is_active: boolean;
  is_verified?: boolean;
  created_at: string;
  updated_at?: string;
}

export interface AuthTokens {
  access_token: string;
  token_type: string;
  expires_in?: number;
}

export interface LoginPayload {
  username: string; // Accepts email or username
  password: string;
}

export interface RegisterPayload {
  email: string;
  username: string;
  password: string;
  full_name?: string;
}

// Stock & Market Types
export interface Stock {
  id: string;
  ticker: string;
  name: string;
  exchange: string; // NSE, BSE, NASDAQ, NYSE
  sector?: string | null;
  industry?: string | null;
  country: string;
  currency: Currency;
  is_active: boolean;
  is_demo?: boolean;
  created_at: string;
}

export interface StockQuote {
  ticker: string;
  name?: string;
  price: number;
  change: number;
  change_percent?: number;
  change_pct?: number;
  open: number;
  high: number;
  low: number;
  previous_close: number;
  volume: number;
  average_volume?: number;
  market_cap?: number;
  pe_ratio?: number | null;
  week_52_high?: number;
  week_52_low?: number;
  currency?: Currency;
  timestamp?: string;
  is_demo?: boolean;
  is_synthetic?: boolean;
}


export interface OHLCV {
  timestamp: string;
  open: number;
  high: number;
  low: number;
  close: number;
  volume: number;
}

export interface StockHistoryResponse {
  ticker: string;
  interval: string;
  currency: Currency;
  data: OHLCV[];
  is_demo?: boolean;
}

export interface MarketIndex {
  ticker: string;
  name: string;
  exchange: string;
  price: number;
  change: number;
  change_percent: number;
  currency: Currency;
  timestamp: string;
}

export interface MarketStatus {
  market: 'NSE' | 'BSE' | 'US';
  is_open: boolean;
  next_open?: string;
  next_close?: string;
  timezone: string;
  indices: MarketIndex[];
}

// Fundamentals Types
export interface ValuationMetrics {
  pe_ratio: number | null;
  pb_ratio: number | null;
  ps_ratio: number | null;
  ev_to_ebitda: number | null;
  peg_ratio: number | null;
  dividend_yield: number | null;
}

export interface ProfitabilityMetrics {
  gross_margin: number | null;
  operating_margin: number | null;
  net_margin: number | null;
  roe: number | null;
  roa: number | null;
  roic: number | null;
}

export interface FinancialHealthMetrics {
  current_ratio: number | null;
  quick_ratio: number | null;
  debt_to_equity: number | null;
  interest_coverage: number | null;
  altman_z_score?: number | null;
  piotroski_f_score?: number | null;
}

export interface FundamentalsData {
  ticker: string;
  company_name: string;
  valuation: ValuationMetrics;
  profitability: ProfitabilityMetrics;
  health: FinancialHealthMetrics;
  market_cap: number;
  enterprise_value: number;
  currency: Currency;
  period: string;
  is_demo?: boolean;
}

// News & Sentiment Types
export interface NewsArticle {
  id: string;
  ticker?: string;
  title: string;
  summary: string;
  source: string;
  url?: string;
  published_at: string;
  sentiment_score: number; // -1.0 to 1.0
  sentiment_label: 'POSITIVE' | 'NEUTRAL' | 'NEGATIVE' | 'BULLISH' | 'BEARISH';
  related_tickers?: string[];
  impact_score?: number;
}

export interface NewsSentimentSummary {
  ticker: string;
  overall_sentiment: string;
  average_sentiment_score: number;
  news_items: NewsArticle[];
}


// Anomaly Detection Types
export type AnomalySeverity = 'LOW' | 'MEDIUM' | 'HIGH' | 'CRITICAL';
export type AnomalyType = 'PRICE_SPIKE' | 'VOLUME_SURGE' | 'VOLATILITY_BURST' | 'CORRELATION_BREAK' | 'MULTIVARIATE_ISOLATION';

export interface AnomalyItem {
  id?: string;
  ticker: string;
  timestamp: string;
  anomaly_type: AnomalyType | string;
  severity?: AnomalySeverity;
  severity_score: number;
  isolation_score?: number | null;
  score?: number;
  price_at_detection?: number;
  z_score?: number;
  summary: string;
  metrics: Record<string, any>;
  supporting_metrics?: Record<string, number | string>;
  description?: string;
}

// Technical Analysis Types
export interface TechnicalIndicators {
  ticker: string;
  sma_20: number;
  sma_50: number;
  ema_20: number;
  rsi_14: number;
  macd: {
    macd?: number;
    signal?: number;
    histogram?: number;
    macd_line?: number;
    signal_line?: number;
  };
  bollinger_bands: {
    upper: number;
    middle: number;
    lower: number;
    bandwidth?: number;
  };
  atr_14: number;
  realized_volatility_20d_pct: number;
  technical_bias: "BULLISH" | "BEARISH" | "NEUTRAL" | string;
}

export type TechnicalAnalyticsResponse = TechnicalIndicators;

// Correlation & Stock DNA Types
export interface CorrelationPair {
  asset_a: string;
  asset_b: string;
  correlation: number;
}

export interface CorrelationMatrixResponse {
  assets: string[];
  matrix: number[][];
  method: string;
  top_pairs: CorrelationPair[];
  observations?: number;
}

export interface StockDNARadarItem {
  factor: string;
  score: number;
  fullMark?: number;
}

export interface StockDNAResponse {
  ticker: string;
  factor_scores: Record<string, number>;
  radar_data: StockDNARadarItem[];
  dominant_persona: string;
  summary: string;
}

export interface StockDNA {
  ticker: string;
  name?: string;
  factors: {
    value: number;       // 0-100
    growth: number;      // 0-100
    quality: number;     // 0-100
    momentum: number;    // 0-100
    volatility: number;  // 0-100
  };
  composite_score?: number;
  factor_deciles?: Record<string, number>;
  style_box?: string;
}

export interface FundamentalValuation {
  pe_ratio?: number | null;
  forward_pe?: number | null;
  pb_ratio?: number | null;
  ev_ebitda?: number | null;
  fcf_yield_pct?: number | null;
}

export interface FundamentalProfitability {
  gross_margin_pct?: number | null;
  operating_margin_pct?: number | null;
  net_margin_pct?: number | null;
  roe_pct?: number | null;
  roa_pct?: number | null;
}

export interface FundamentalHealth {
  current_ratio?: number | null;
  debt_to_equity?: number | null;
  interest_coverage_ratio?: number | null;
  altman_z_score?: number | null;
  health_score?: string;
}

export interface FundamentalOverviewResponse {
  ticker: string;
  name: string;
  sector: string;
  valuation: FundamentalValuation;
  profitability: FundamentalProfitability;
  financial_health: FundamentalHealth;
}

export interface TickerAnomalyResponse {
  ticker: string;
  anomalies: AnomalyItem[];
  volatility_regime?: {
    current_volatility_pct?: number;
    garch_forecast_5d?: number[];
    volatility_regime?: string;
    long_term_mean_vol_pct?: number;
  };
  volume_spike?: {
    is_spike?: boolean;
    volume_ratio?: number;
    z_score?: number;
  };
}

// Scenario Simulation Types
export interface ScenarioSimulationRequest {
  ticker: string;
  days_ahead: number;
  simulations: number;
  drift_override?: number;
  volatility_override?: number;
  crisis_replay?: '2008_GFC' | '2020_COVID' | '2022_TECH_SELLOFF' | null;
  macro_shock?: {
    interest_rate_hike_bps?: number;
    oil_price_spike_pct?: number;
    inr_depreciation_pct?: number;
  };
}

export interface SimulationQuantiles {
  day: number;
  p05: number;
  p25: number;
  p50: number;
  p75: number;
  p95: number;
}

export interface ScenarioSimulationResult {
  ticker: string;
  current_price: number;
  currency: Currency;
  days_ahead: number;
  simulations: number;
  model_used: string;
  quantiles: SimulationQuantiles[];
  var_95: number;
  var_99: number;
  expected_shortfall_95: number;
  simulated_return_mean: number;
  simulated_return_std: number;
  is_simulation_not_prediction: boolean;
}

// Portfolio Types
export interface PortfolioPosition {
  id: string;
  ticker: string;
  asset_name?: string;
  quantity: number;
  average_buy_price: number;
  current_price?: number;
  current_value?: number;
  unrealized_pnl?: number;
  unrealized_pnl_percent?: number;
  weight_percent?: number;
  currency: Currency;
}

export interface Portfolio {
  id: string;
  name: string;
  description?: string;
  user_id: string;
  total_value: number;
  cash_balance: number;
  total_pnl: number;
  total_pnl_percent: number;
  daily_pnl?: number;
  daily_pnl_percent?: number;
  beta?: number;
  var_95_daily?: number;
  positions: PortfolioPosition[];
  created_at: string;
  updated_at?: string;
}

export interface PortfolioCreatePayload {
  name: string;
  description?: string;
  cash_balance?: number;
}

export interface PositionAddPayload {
  ticker: string;
  quantity: number;
  buy_price: number;
}

// Watchlist Types
export interface WatchlistItem {
  id: string;
  ticker: string;
  name: string;
  current_price: number;
  change: number;
  change_percent: number;
  currency: Currency;
  added_at: string;
}

// Sector Performance Types
export interface SectorItem {
  sector: string;
  performance_pct: number;
  momentum_score: number;
  top_stock: string;
  market_cap_weight: number;
}

export interface MarketIndexItem {
  symbol: string;
  name: string;
  price: number;
  change: number;
  change_pct: number;
}

export interface MarketOverviewResponse {
  indices: MarketIndexItem[];
  top_gainers?: any[];
  top_losers?: any[];
  market_regime: string;
  timestamp: string;
}

export interface AnomalyStreamResponse {
  anomalies: AnomalyItem[];
  total_active: number;
  systemic_stress_index: number;
  timestamp: string;
}

export interface PortfolioHolding {
  ticker: string;
  shares: number;
  avg_price: number;
  current_price: number;
  market_value: number;
  unrealized_pnl: number;
  unrealized_pnl_pct: number;
  weight_pct: number;
  company_name?: string;
  sector?: string;
  beta?: number;
  daily_change?: number;
  daily_change_pct?: number;
}

export interface PortfolioTransaction {
  id: string;
  ticker: string;
  company_name?: string;
  transaction_type: "BUY" | "SELL" | "DIVIDEND" | "OTHER";
  shares: number;
  price: number;
  fees?: number;
  total_value: number;
  executed_at: string;
  notes?: string;
}

export interface PortfolioRiskMetrics {
  portfolio_beta?: number;
  daily_var_95?: number;
  daily_var_95_pct?: number;
  sharpe_ratio?: number;
  sortino_ratio?: number;
  annualized_volatility_pct?: number;
  max_drawdown_pct?: number;
  downside_deviation_pct?: number;
  tracking_error_pct?: number;
  alpha_pct?: number;
}

export interface ConcentrationMetrics {
  top_1_weight_pct: number;
  top_1_ticker: string;
  top_3_weight_pct: number;
  top_5_weight_pct: number;
  largest_sector_weight_pct: number;
  largest_sector_name: string;
  hhi_index: number;
}

export interface PortfolioStressTestCrisis {
  crisis_name: string;
  period: string;
  projected_portfolio_loss_dollars: number;
  projected_drawdown_pct: number;
  stressed_portfolio_value: number;
  description: string;
}

export interface PortfolioStressTestResponse {
  initial_portfolio_value: number;
  crises_stress_results: Record<string, PortfolioStressTestCrisis>;
}

export interface PortfolioSummaryResponse {
  total_value: number;
  total_cost: number;
  total_unrealized_pnl: number;
  total_unrealized_pnl_pct: number;
  daily_pnl: number;
  daily_pnl_pct: number;
  cash_balance?: number;
  weighted_beta?: number;
  daily_var_95_pct?: number;
  positions_count?: number;
  positions?: Array<{
    ticker: string;
    shares: number;
    price: number;
    market_value: number;
    avg_cost: number;
    unrealized_pnl_pct: number;
    sector: string;
    beta: number;
  }>;
  holdings: PortfolioHolding[];
  risk_metrics?: PortfolioRiskMetrics;
}

export interface AgentQueryResponse {
  session_id?: string;
  query: string;
  intent: string;
  ticker_focus?: string | null;
  answer: string;
  thought_steps?: Array<{ step: number; agent: string; message: string }>;
  tool_calls?: Array<Record<string, any>>;
  citations?: Array<Record<string, any>>;
  ui_widgets?: Array<Record<string, any>>;
  guardrail_passed?: boolean;
}


export interface CitationItem {
  id: string;
  ticker: string;
  title: string;
  filing_type: string;
  fiscal_year: number | string;
  section: string;
  page_number?: number;
  content_snippet: string;
  relevance_score?: number;
  relevance?: number;
  date?: string;
  source?: string;
}

export interface DocumentSearchRequest {
  query: string;
  ticker?: string;
  doc_type?: string;
  top_k?: number;
}

export interface DocumentSearchResponse {
  query: string;
  total_results: number;
  citations: CitationItem[];
  synthesis_summary: string;
}

export type ResearchMode =
  | "ALL"
  | "GENERAL"
  | "COMPANY"
  | "TECHNICAL"
  | "FUNDAMENTAL"
  | "RISK"
  | "ANOMALY"
  | "NEWS"
  | "FILINGS";

export interface ResearchMessage {
  id: string;
  role: "user" | "assistant";
  content: string;
  timestamp: string;
  ticker?: string | null;
  mode?: ResearchMode;
  agentResponse?: AgentQueryResponse;
  citations?: CitationItem[];
  thoughtSteps?: Array<{ step: number; agent: string; message: string }>;
  isStreaming?: boolean;
}

export interface ResearchSession {
  id: string;
  title: string;
  ticker?: string | null;
  createdAt: string;
  updatedAt: string;
  messages: ResearchMessage[];
  lastQuery: string;
}

export type PipelineNodeStatus = "pending" | "running" | "completed" | "warning" | "failed";

export interface PipelineNode {
  id: string;
  name: string;
  agent: string;
  description: string;
  status: PipelineNodeStatus;
  detail?: string;
}

