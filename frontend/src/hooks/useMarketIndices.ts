"use client";

import { useState, useEffect, useCallback, useMemo } from "react";
import { marketApi } from "@/lib/api/market";
import { MarketIndexItem, MarketStatus } from "@/types";
import { useMarketWebSocket } from "@/providers/MarketWebSocketProvider";
import { useRealtimeIndices, useRealtimeMarketStatus } from "./useRealtimeSelectors";

export interface MarketIndicesState {
  indices: MarketIndexItem[];
  marketStatus: MarketStatus | null;
  isLoading: boolean;
  isError: boolean;
  error: string | null;
  isDemo: boolean;
  lastUpdated: Date | null;
  refresh: () => Promise<void>;
}

// Institutional fallback data for Indian Benchmark Indices
const FALLBACK_INDICES: MarketIndexItem[] = [
  {
    symbol: "^NSEI",
    name: "NIFTY 50",
    price: 24823.15,
    change: 142.8,
    change_pct: 0.58,
  },
  {
    symbol: "^BSESN",
    name: "SENSEX",
    price: 81455.4,
    change: 418.25,
    change_pct: 0.52,
  },
  {
    symbol: "^NSEBANK",
    name: "NIFTY BANK",
    price: 52340.85,
    change: -88.4,
    change_pct: -0.17,
  },
  {
    symbol: "^CNXIT",
    name: "NIFTY IT",
    price: 41890.1,
    change: 532.65,
    change_pct: 1.29,
  },
];

export function useMarketIndices(): MarketIndicesState {
  const [baseIndices, setBaseIndices] = useState<MarketIndexItem[]>([]);
  const [baseMarketStatus, setBaseMarketStatus] = useState<MarketStatus | null>(null);
  const [isLoading, setIsLoading] = useState<boolean>(true);
  const [isError, setIsError] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);
  const [isDemo, setIsDemo] = useState<boolean>(false);
  const [lastUpdated, setLastUpdated] = useState<Date | null>(null);

  const { subscribeChannel, unsubscribeChannel } = useMarketWebSocket();
  const realtimeIndices = useRealtimeIndices();
  const realtimeNseStatus = useRealtimeMarketStatus("NSE");

  // Subscribe to 'indices' and 'market_status' channels
  useEffect(() => {
    subscribeChannel("indices");
    subscribeChannel("market_status");
    return () => {
      unsubscribeChannel("indices");
      unsubscribeChannel("market_status");
    };
  }, [subscribeChannel, unsubscribeChannel]);

  const fetchIndices = useCallback(async () => {
    setIsLoading(true);
    setIsError(false);
    setError(null);
    try {
      const [indicesData, statusData] = await Promise.all([
        marketApi.getMarketIndices(),
        marketApi.getMarketStatus(),
      ]);

      if (indicesData && indicesData.length > 0) {
        setBaseIndices(indicesData);
        setIsDemo(false);
      } else {
        setBaseIndices(FALLBACK_INDICES);
        setIsDemo(true);
      }
      setBaseMarketStatus(statusData);
      setLastUpdated(new Date());
    } catch (err: any) {
      console.warn("API unavailable, utilizing fallback benchmark seed data:", err.message);
      setBaseIndices(FALLBACK_INDICES);
      setBaseMarketStatus({
        market: "NSE",
        is_open: true,
        timezone: "IST (UTC+5:30)",
        indices: [],
      });
      setIsDemo(true);
      setIsError(false); // Graceful degradation
      setLastUpdated(new Date());
    } finally {
      setIsLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchIndices();
  }, [fetchIndices]);

  // Dynamically merge real-time index tick updates over base indices
  const mergedIndices = useMemo(() => {
    const list = baseIndices.length > 0 ? baseIndices : FALLBACK_INDICES;
    return list.map((idx) => {
      const rt = realtimeIndices[idx.symbol] || realtimeIndices[idx.name.toUpperCase()];
      if (!rt) return idx;
      return {
        ...idx,
        price: rt.price,
        change: rt.change,
        change_pct: rt.changePercent,
      };
    });
  }, [baseIndices, realtimeIndices]);

  const mergedMarketStatus = useMemo(() => {
    if (!realtimeNseStatus) return baseMarketStatus;
    return {
      ...(baseMarketStatus || { market: "NSE", timezone: "IST (UTC+5:30)", indices: [] }),
      is_open: realtimeNseStatus.isOpen,
    };
  }, [baseMarketStatus, realtimeNseStatus]);

  return {
    indices: mergedIndices,
    marketStatus: mergedMarketStatus,
    isLoading,
    isError,
    error,
    isDemo,
    lastUpdated,
    refresh: fetchIndices,
  };
}
