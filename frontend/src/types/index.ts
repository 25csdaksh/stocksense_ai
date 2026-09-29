export interface AssetInfo {
  ticker: string;
  name: string;
  sector?: string;
  industry?: string;
  market_cap?: number;
  pe_ratio?: number;
  pb_ratio?: number;
  beta?: number;
  dividend_yield?: number;
}

export interface MarketQuote {
  ticker: string;
  name: string;
  price: number;
  change: number;
  change_pct: number;
  open: number;
  high: number;
  low: number;
  previous_close: number;
  volume: number;
  avg_volume: number;
  market_cap?: number;
  pe_ratio?: number;
  week_52_high: number;
  week_52_low: number;
  is_synthetic: boolean;
  data_source: string;
  timestamp: string;
}

export interface OHLCVBar {
  time: string;
  open: number;
  high: number;
  low: number;
  close: number;
  volume: number;
  vwap?: number | null;
  sma_20?: number | null;
  sma_50?: number | null;
  ema_20?: number | null;
  rsi_14?: number | null;
}

export interface HistoricalData {
  ticker: string;
  interval: string;
  range: string;
  bars: OHLCVBar[];
  is_synthetic: boolean;
  total_bars: number;
}

export interface MarketIndex {
  symbol: string;
  name: string;
  price: number;
  change: number;
  change_pct: number;
}

export interface SectorItem {
  sector: string;
  performance_pct: number;
  momentum_score: number;
  top_stock: string;
  market_cap_weight: number;
}

export interface AnomalyItem {
  ticker: string;
  timestamp: string;
  anomaly_type: string;
  severity_score: number;
  isolation_score?: number;
  summary: string;
  metrics: {
    close: number;
    volume: number;
    volume_zscore: number;
    log_return_pct: number;
    hl_spread_pct: number;
  };
}

export interface AnomalyStream {
  anomalies: AnomalyItem[];
  total_active: number;
  systemic_stress_index: number;
  timestamp: string;
}

export interface StockDNAFactor {
  factor: string;
  score: number;
  fullMark: number;
}

export interface StockDNAResponse {
  ticker: string;
  factor_scores: {
    value: number;
    growth: number;
    quality: number;
    momentum: number;
    low_volatility: number;
  };
  radar_data: StockDNAFactor[];
  dominant_persona: string;
  summary: string;
}

export interface FanChartPoint {
  day: number;
  p10: number;
  p25: number;
  p50: number;
  p75: number;
  p90: number;
}

export interface DistributionBin {
  range_label: string;
  midpoint: number;
  frequency: number;
}

export interface MonteCarloResult {
  ticker: string;
  initial_price: number;
  days: number;
  iterations: number;
  annualized_drift_pct: number;
  annualized_volatility_pct: number;
  expected_terminal_price_p50: number;
  terminal_p10_price: number;
  terminal_p90_price: number;
  value_at_risk_95_pct: number;
  value_at_risk_99_pct: number;
  cvar_expected_shortfall_95_pct: number;
  cvar_expected_shortfall_99_pct: number;
  probability_of_profit_pct: number;
  prob_loss_exceeding_10pct: number;
  prob_gain_exceeding_20pct: number;
  fan_chart: FanChartPoint[];
  distribution_histogram: DistributionBin[];
  sample_paths: number[][];
  disclaimer: string;
}

export interface NetworkNode {
  id: string;
  label: string;
  name: string;
  sector: string;
  degree: number;
  eigenvector_centrality: number;
  betweenness_centrality: number;
  annualized_volatility: number;
}

export interface NetworkEdge {
  source: string;
  target: string;
  weight: number;
  correlation: number;
  edge_type: string;
}

export interface RelationshipGraphData {
  nodes: NetworkNode[];
  edges: NetworkEdge[];
  network_metrics: {
    total_nodes: number;
    total_edges: number;
    graph_density: number;
    most_systemic_node: string;
    correlation_threshold_applied: number;
  };
}

export interface DocumentCitation {
  id: string;
  ticker: string;
  title: string;
  filing_type: string;
  fiscal_year?: number;
  section: string;
  content_snippet: string;
  relevance_score: number;
  page_number?: number;
}

export interface NewsItem {
  id: string;
  ticker: string;
  title: string;
  summary: string;
  source: string;
  url?: string;
  published_at: string;
  sentiment_label: string;
  sentiment_score: number;
  impact_score: number;
}
