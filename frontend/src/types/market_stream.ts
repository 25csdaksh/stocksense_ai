/**
 * MarketMind AI — Real-Time WebSocket Streaming Client Types & Contract (Phase 6.4 & 6.5).
 * Standardized typed interface for WebSocket connections, incoming event payloads,
 * streaming subscriptions, and real-time state management.
 */

export type WebSocketConnectionState =
  | 'DISCONNECTED'
  | 'CONNECTING'
  | 'CONNECTED'
  | 'RECONNECTING'
  | 'ERROR';

export type MarketDataStatus =
  | 'LIVE'
  | 'DEMO'
  | 'STALE'
  | 'UNKNOWN'
  | 'DELAYED'
  | 'CONFIGURATION_REQUIRED'
  | 'OFFLINE';

export type MarketDataSource =
  | 'ZERODHA'
  | 'INDIAN_EXCHANGE'
  | 'YFINANCE'
  | 'DEMO'
  | 'COLLECTOR'
  | 'SYSTEM'
  | string;

export type MarketStreamChannel =
  | 'quotes'
  | 'indices'
  | 'anomalies'
  | 'market_status'
  | 'ingestion'
  | 'portfolio';

export type MarketStreamEventType =
  | 'CONNECTED'
  | 'QUOTE_TICK'
  | 'BAR_CLOSED'
  | 'INDEX_TICK'
  | 'ANOMALY_DETECTED'
  | 'SESSION_CHANGE'
  | 'INGESTION_CYCLE_COMPLETED'
  | 'SUBSCRIPTION_SUCCESS'
  | 'UNSUBSCRIPTION_SUCCESS'
  | 'SUBSCRIPTIONS'
  | 'AUTH_SUCCESS'
  | 'pong'
  | 'ERROR';

export interface MarketStreamMessage<T = Record<string, any>> {
  event: MarketStreamEventType | string;
  event_id?: string;
  symbol?: string;
  exchange?: string;
  timestamp?: string;
  data_status?: MarketDataStatus | string;
  data_source?: MarketDataSource;
  payload?: T;
  code?: string;
  message?: string;
  server_time?: string;
  connection_id?: string;
  user_id?: string;
  is_authenticated?: boolean;
  supported_channels?: string[];
  subscribed_symbols?: string[];
  subscribed_channels?: string[];
  added_symbols?: string[];
  added_channels?: string[];
  removed_symbols?: string[];
  removed_channels?: string[];
}

export interface QuoteTickPayload {
  price: number;
  volume?: number;
  change?: number;
  change_percent?: number;
  day_high?: number;
  day_low?: number;
  is_simulated?: boolean;
}

export interface IndexTickPayload {
  index_name?: string;
  value: number;
  change?: number;
  change_percent?: number;
  is_simulated?: boolean;
}

export interface AnomalyPayload {
  anomaly_type: string;
  severity: 'LOW' | 'MEDIUM' | 'HIGH' | 'CRITICAL' | string;
  confidence_score: number;
  detection_model?: string;
  is_simulated?: boolean;
  metrics?: Record<string, any>;
  summary?: string;
}

export interface SessionChangePayload {
  exchange: string;
  status: 'OPEN' | 'CLOSED' | 'PRE_MARKET' | 'POST_MARKET' | string;
  is_open: boolean;
  is_simulated?: boolean;
}

export interface IngestionCyclePayload {
  symbols_processed: number;
  status: string;
  mode: string;
  is_simulated?: boolean;
}

// Normalized Realtime State Entities
export interface RealtimeQuote {
  symbol: string;
  exchange: string;
  price: number;
  change: number;
  changePercent: number;
  volume?: number;
  dayHigh?: number;
  dayLow?: number;
  timestamp: string;
  dataStatus: MarketDataStatus;
  dataSource: MarketDataSource;
  lastUpdated: Date;
}

export interface RealtimeIndex {
  symbol: string;
  name: string;
  exchange: string;
  price: number;
  change: number;
  changePercent: number;
  timestamp: string;
  dataStatus: MarketDataStatus;
  dataSource: MarketDataSource;
  lastUpdated: Date;
}

export interface RealtimeAnomaly {
  id: string;
  ticker: string;
  anomaly_type: string;
  severity: 'LOW' | 'MEDIUM' | 'HIGH' | 'CRITICAL';
  severity_score: number;
  summary: string;
  timestamp: string;
  dataStatus: MarketDataStatus;
  dataSource: MarketDataSource;
  metrics?: Record<string, any>;
  receivedAt: Date;
}

export interface RealtimeMarketStatus {
  exchange: string;
  status: 'OPEN' | 'CLOSED' | 'PRE_MARKET' | 'POST_MARKET' | string;
  isOpen: boolean;
  timestamp: string;
  dataStatus: MarketDataStatus;
  lastUpdated: Date;
}

export interface RealtimeStoreState {
  quotes: Record<string, RealtimeQuote>;
  indices: Record<string, RealtimeIndex>;
  anomalies: RealtimeAnomaly[];
  marketStatus: Record<string, RealtimeMarketStatus>;
  lastEventAt: Date | null;
  connectionStatus: WebSocketConnectionState;
  dataStatus: MarketDataStatus;
  dataSource: MarketDataSource;
}

export interface MarketWebSocketContextType {
  status: WebSocketConnectionState;
  dataStatus: MarketDataStatus;
  dataSource: MarketDataSource;
  connected: boolean;
  lastEventAt: Date | null;
  isStale: boolean;
  subscribeSymbol: (symbol: string) => void;
  unsubscribeSymbol: (symbol: string) => void;
  subscribeChannel: (channel: MarketStreamChannel) => void;
  unsubscribeChannel: (channel: MarketStreamChannel) => void;
  reconnect: () => void;
}

export interface MarketStreamHealthResponse {
  websocket_enabled: boolean;
  active_connections: number;
  active_subscriptions: number;
  events_per_second: number;
  dropped_events: number;
  last_event_timestamp: string | null;
  telemetry: {
    connections_total: number;
    active_connections: number;
    connections_rejected: number;
    subscriptions_total: number;
    events_sent: number;
    events_dropped: number;
    authentication_failures: number;
    disconnects: number;
  };
}
