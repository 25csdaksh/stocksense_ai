"use client";

import { useSyncExternalStore, useMemo } from "react";
import { marketStore } from "../lib/realtime/marketStore";
import { normalizeSymbol } from "../lib/realtime/symbolNormalizer";
import type {
  RealtimeQuote,
  RealtimeIndex,
  RealtimeAnomaly,
  RealtimeMarketStatus,
} from "../types/market_stream";

/**
 * React hook to select real-time quote for a specific ticker symbol.
 */
export function useRealtimeQuote(rawSymbol: string): RealtimeQuote | undefined {
  const canonical = normalizeSymbol(rawSymbol);
  const storeState = useSyncExternalStore(
    marketStore.subscribe,
    marketStore.getSnapshot,
    marketStore.getSnapshot
  );
  return storeState.quotes[canonical];
}

/**
 * React hook to select real-time index data for a specific index ticker.
 */
export function useRealtimeIndex(rawSymbol: string): RealtimeIndex | undefined {
  const canonical = normalizeSymbol(rawSymbol);
  const storeState = useSyncExternalStore(
    marketStore.subscribe,
    marketStore.getSnapshot,
    marketStore.getSnapshot
  );
  return storeState.indices[canonical];
}

/**
 * React hook to select all real-time benchmark indices.
 */
export function useRealtimeIndices(): Record<string, RealtimeIndex> {
  const storeState = useSyncExternalStore(
    marketStore.subscribe,
    marketStore.getSnapshot,
    marketStore.getSnapshot
  );
  return storeState.indices;
}

/**
 * React hook to select real-time anomaly alerts stream.
 */
export function useRealtimeAnomalies(limit: number = 20): RealtimeAnomaly[] {
  const storeState = useSyncExternalStore(
    marketStore.subscribe,
    marketStore.getSnapshot,
    marketStore.getSnapshot
  );
  return useMemo(
    () => storeState.anomalies.slice(0, limit),
    [storeState.anomalies, limit]
  );
}

/**
 * React hook to select market session status for an exchange.
 */
export function useRealtimeMarketStatus(exchange: string = "NSE"): RealtimeMarketStatus | undefined {
  const exch = exchange.toUpperCase();
  const storeState = useSyncExternalStore(
    marketStore.subscribe,
    marketStore.getSnapshot,
    marketStore.getSnapshot
  );
  return storeState.marketStatus[exch];
}

/**
 * React hook to select connection state and data freshness.
 */
export function useRealtimeConnectionState() {
  const storeState = useSyncExternalStore(
    marketStore.subscribe,
    marketStore.getSnapshot,
    marketStore.getSnapshot
  );

  return useMemo(() => {
    const isStale =
      storeState.connectionStatus === "CONNECTED" &&
      storeState.lastEventAt !== null &&
      Date.now() - storeState.lastEventAt.getTime() > 60000;

    return {
      status: storeState.connectionStatus,
      dataStatus: isStale ? "STALE" : storeState.dataStatus,
      dataSource: storeState.dataSource,
      lastEventAt: storeState.lastEventAt,
      isStale,
    };
  }, [
    storeState.connectionStatus,
    storeState.lastEventAt,
    storeState.dataStatus,
    storeState.dataSource,
  ]);
}
