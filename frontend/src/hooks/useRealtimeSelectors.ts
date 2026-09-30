"use client";

import { useSyncExternalStore, useCallback } from "react";
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
  const selector = useCallback(
    () => marketStore.getSnapshot().quotes[canonical],
    [canonical]
  );
  return useSyncExternalStore(marketStore.subscribe, selector, selector);
}

/**
 * React hook to select real-time index data for a specific index ticker.
 */
export function useRealtimeIndex(rawSymbol: string): RealtimeIndex | undefined {
  const canonical = normalizeSymbol(rawSymbol);
  const selector = useCallback(
    () => marketStore.getSnapshot().indices[canonical],
    [canonical]
  );
  return useSyncExternalStore(marketStore.subscribe, selector, selector);
}

/**
 * React hook to select all real-time benchmark indices.
 */
export function useRealtimeIndices(): Record<string, RealtimeIndex> {
  const selector = useCallback(() => marketStore.getSnapshot().indices, []);
  return useSyncExternalStore(marketStore.subscribe, selector, selector);
}

/**
 * React hook to select real-time anomaly alerts stream.
 */
export function useRealtimeAnomalies(limit: number = 20): RealtimeAnomaly[] {
  const selector = useCallback(
    () => marketStore.getSnapshot().anomalies.slice(0, limit),
    [limit]
  );
  return useSyncExternalStore(marketStore.subscribe, selector, selector);
}

/**
 * React hook to select market session status for an exchange.
 */
export function useRealtimeMarketStatus(exchange: string = "NSE"): RealtimeMarketStatus | undefined {
  const exch = exchange.toUpperCase();
  const selector = useCallback(
    () => marketStore.getSnapshot().marketStatus[exch],
    [exch]
  );
  return useSyncExternalStore(marketStore.subscribe, selector, selector);
}

/**
 * React hook to select connection state and data freshness.
 */
export function useRealtimeConnectionState() {
  const selector = useCallback(() => {
    const snap = marketStore.getSnapshot();
    const isStale =
      snap.connectionStatus === "CONNECTED" &&
      snap.lastEventAt !== null &&
      Date.now() - snap.lastEventAt.getTime() > 60000;

    return {
      status: snap.connectionStatus,
      dataStatus: isStale ? "STALE" : snap.dataStatus,
      dataSource: snap.dataSource,
      lastEventAt: snap.lastEventAt,
      isStale,
    };
  }, []);

  return useSyncExternalStore(marketStore.subscribe, selector, selector);
}
