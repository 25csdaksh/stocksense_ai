"use client";

import { useState, useEffect, useCallback } from "react";
import { marketApi } from "@/lib/api/market";
import { SectorItem } from "@/types";

const FALLBACK_SECTORS: SectorItem[] = [
  {
    sector: "Information Technology",
    performance_pct: 1.45,
    momentum_score: 84.2,
    top_stock: "TCS.NS",
    market_cap_weight: 14.8,
  },
  {
    sector: "Banking & Financials",
    performance_pct: 0.72,
    momentum_score: 76.5,
    top_stock: "HDFCBANK.NS",
    market_cap_weight: 32.4,
  },
  {
    sector: "Energy & Petrochemicals",
    performance_pct: -0.38,
    momentum_score: 52.1,
    top_stock: "RELIANCE.NS",
    market_cap_weight: 15.2,
  },
  {
    sector: "Automobile & EV",
    performance_pct: 1.15,
    momentum_score: 79.8,
    top_stock: "TATAMOTORS.NS",
    market_cap_weight: 6.9,
  },
  {
    sector: "Pharmaceuticals & Healthcare",
    performance_pct: 0.42,
    momentum_score: 68.3,
    top_stock: "SUNPHARMA.NS",
    market_cap_weight: 4.8,
  },
  {
    sector: "Fast-Moving Consumer Goods (FMCG)",
    performance_pct: -0.15,
    momentum_score: 48.9,
    top_stock: "ITC.NS",
    market_cap_weight: 8.5,
  },
  {
    sector: "Metals & Mining",
    performance_pct: 0.88,
    momentum_score: 71.2,
    top_stock: "TATASTEEL.NS",
    market_cap_weight: 3.7,
  },
];

export function useSectors() {
  const [sectors, setSectors] = useState<SectorItem[]>([]);
  const [isLoading, setIsLoading] = useState<boolean>(true);
  const [isError, setIsError] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);
  const [isDemo, setIsDemo] = useState<boolean>(false);

  const fetchSectors = useCallback(async () => {
    setIsLoading(true);
    setIsError(false);
    setError(null);
    try {
      const data = await marketApi.getSectorPerformance();
      if (data && data.length > 0) {
        setSectors(data);
        setIsDemo(false);
      } else {
        setSectors(FALLBACK_SECTORS);
        setIsDemo(true);
      }
    } catch {
      setSectors(FALLBACK_SECTORS);
      setIsDemo(true);
    } finally {
      setIsLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchSectors();
  }, [fetchSectors]);

  return {
    sectors,
    isLoading,
    isError,
    error,
    isDemo,
    refresh: fetchSectors,
  };
}
