"use client";

import { useState, useEffect, useCallback } from "react";
import { marketApi } from "@/lib/api/market";
import { MarketIndexItem, MarketStatus } from "@/types";

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
  const [indices, setIndices] = useState<MarketIndexItem[]>([]);
  const [marketStatus, setMarketStatus] = useState<MarketStatus | null>(null);
  const [isLoading, setIsLoading] = useState<boolean>(true);
  const [isError, setIsError] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);
  const [isDemo, setIsDemo] = useState<boolean>(false);
  const [lastUpdated, setLastUpdated] = useState<Date | null>(null);

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
        setIndices(indicesData);
        setIsDemo(false);
      } else {
        setIndices(FALLBACK_INDICES);
        setIsDemo(true);
      }
      setMarketStatus(statusData);
      setLastUpdated(new Date());
    } catch (err: any) {
      console.warn("API unavailable, utilizing fallback benchmark seed data:", err.message);
      setIndices(FALLBACK_INDICES);
      setMarketStatus({
        market: "NSE",
        is_open: true,
        timezone: "IST (UTC+5:30)",
        indices: [],
      });
      setIsDemo(true);
      setIsError(false); // Graceful degradation to demo data
      setLastUpdated(new Date());
    } finally {
      setIsLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchIndices();
  }, [fetchIndices]);

  return {
    indices,
    marketStatus,
    isLoading,
    isError,
    error,
    isDemo,
    lastUpdated,
    refresh: fetchIndices,
  };
}
