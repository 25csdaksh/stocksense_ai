/**
 * MarketMind AI — Real-Time WebSocket Streaming Client Types & Contract (Phase 6.4).
 * Typed interface matching backend streaming events and channels.
 */

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

export type MarketDataStatus =
  | 'LIVE'
  | 'DELAYED'
  | 'DEMO'
  | 'CONFIGURATION_REQUIRED'
  | 'OFFLINE';

export interface MarketStreamMessage<T = any> {
  event: MarketStreamEventType | string;
  event_id?: string;
  symbol?: string;
  exchange?: string;
  timestamp?: string;
  data_status?: MarketDataStatus | string;
  data_source?: string;
  payload?: T;
  code?: string;
  message?: string;
  subscribed_symbols?: string[];
  subscribed_channels?: string[];
}

export interface QuoteTickPayload {
  price: number;
  volume?: number;
  change?: number;
  change_percent?: number;
  day_high?: number;
  day_low?: number;
}

export interface IndexTickPayload {
  index_name?: string;
  value: number;
  change_percent?: number;
}

export interface AnomalyPayload {
  anomaly_type: string;
  severity: string;
  confidence_score: number;
  detection_model?: string;
}

export interface SessionChangePayload {
  exchange: string;
  status: 'OPEN' | 'CLOSED' | 'PRE_MARKET' | 'POST_MARKET';
  is_open: boolean;
}

export interface IngestionCyclePayload {
  symbols_processed: number;
  status: string;
  mode: string;
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
