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
  price: number;
  change: number;
  change_percent: number;
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
  currency: Currency;
  timestamp: string;
  is_demo?: boolean;
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
  title: string;
  summary: string;
  source: string;
  url: string;
  published_at: string;
  sentiment_score: number; // -1.0 to 1.0
  sentiment_label: 'POSITIVE' | 'NEUTRAL' | 'NEGATIVE';
  related_tickers: string[];
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
  timestamp: string;
  rsi_14: number;
  macd: {
    macd_line: number;
    signal_line: number;
    histogram: number;
  };
  sma_20: number;
  sma_50: number;
  sma_200: number;
  ema_20: number;
  bollinger_bands: {
    upper: number;
    middle: number;
    lower: number;
    bandwidth: number;
  };
  atr_14: number;
  realized_volatility: number;
  signals: {
    trend: 'BULLISH' | 'BEARISH' | 'NEUTRAL';
    rsi_state: 'OVERBOUGHT' | 'OVERSOLD' | 'NEUTRAL';
    overall: 'BUY' | 'HOLD' | 'SELL';
  };
}

// Correlation & Stock DNA Types
export interface CorrelationMatrix {
  tickers: string[];
  matrix: number[][]; // 2D array of correlation coefficients
  period: string;
  central_hubs?: string[];
}

export interface StockDNA {
  ticker: string;
  name: string;
  factors: {
    value: number;       // 0-100
    growth: number;      // 0-100
    quality: number;     // 0-100
    momentum: number;    // 0-100
    volatility: number;  // 0-100 (lower score = lower volatility)
  };
  composite_score: number;
  factor_deciles: Record<string, number>;
  style_box: string;
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
}

export interface PortfolioSummaryResponse {
  total_value: number;
  total_cost: number;
  total_unrealized_pnl: number;
  total_unrealized_pnl_pct: number;
  daily_pnl: number;
  daily_pnl_pct: number;
  holdings: PortfolioHolding[];
  risk_metrics?: {
    portfolio_beta?: number;
    daily_var_95?: number;
    sharpe_ratio?: number;
  };
}

export interface AgentQueryResponse {
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

// AI & RAG Research Types
export interface CitationSource {
  id: number;
  ticker: string;
  company: string;
  document_type: string;
  fiscal_year: string | number;
  section: string;
  filing_date?: string;
  excerpt: string;
  relevance_score?: number;
}

export interface AIResearchResponse {
  query: string;
  intent: string;
  entities: string[];
  execution_plan: string[];
  tools_called: string[];
  structured_response: {
    data_summary: string;
    analysis: string;
    assumptions: string;
    uncertainty_and_risks: string;
    sources: CitationSource[];
  };
  markdown_answer: string;
  disclaimer: string;
  latency_ms: number;
  timestamp: string;
}
