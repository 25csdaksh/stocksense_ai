"use client";

import { useState, useEffect, useCallback } from "react";
import { analyticsApi } from "@/lib/api/analytics";
import { AnomalyItem } from "@/types";

const FALLBACK_ANOMALIES: AnomalyItem[] = [
  {
    ticker: "RELIANCE.NS",
    timestamp: "10 mins ago",
    anomaly_type: "VOLUME_SURGE",
    severity_score: 0.88,
    isolation_score: -0.42,
    summary: "Intraday institutional block volume exceeded 3.4x 30-day average near key resistance.",
    metrics: { volume_z_score: 3.42, price_impact_bps: 45, block_trades_count: 14 },
  },
  {
    ticker: "INFY.NS",
    timestamp: "24 mins ago",
    anomaly_type: "CORRELATION_BREAK",
    severity_score: 0.74,
    isolation_score: -0.31,
    summary: "Pairwise correlation with NIFTY IT de-linked (-0.68 divergence) during afternoon session.",
    metrics: { rolling_correlation: -0.68, sector_beta_shift: 1.85 },
  },
  {
    ticker: "HDFCBANK.NS",
    timestamp: "45 mins ago",
    anomaly_type: "VOLATILITY_BURST",
    severity_score: 0.52,
    isolation_score: -0.21,
    summary: "GARCH(1,1) forecasted realized variance expansion following derivative expiry positioning.",
    metrics: { implied_vol_jump: 2.8, garch_sigma: 18.4 },
  },
  {
    ticker: "TATAMOTORS.NS",
    timestamp: "1 hour ago",
    anomaly_type: "PRICE_SPIKE",
    severity_score: 0.92,
    isolation_score: -0.55,
    summary: "Sudden +2.4% price impulse in 5-minute candle accompanied by order book asymmetry.",
    metrics: { impulse_pct: 2.41, bid_ask_spread_bps: 18, skewness: 2.1 },
  },
];

export function useAnomalies() {
  const [anomalies, setAnomalies] = useState<AnomalyItem[]>([]);
  const [totalActive, setTotalActive] = useState<number>(4);
  const [systemicStressIndex, setSystemicStressIndex] = useState<number>(18.4);
  const [isLoading, setIsLoading] = useState<boolean>(true);
  const [isError, setIsError] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);
  const [isDemo, setIsDemo] = useState<boolean>(false);

  const fetchAnomalies = useCallback(async () => {
    setIsLoading(true);
    setIsError(false);
    setError(null);
    try {
      const data = await analyticsApi.getMarketAnomalyStream();
      if (data && data.anomalies && data.anomalies.length > 0) {
        setAnomalies(data.anomalies);
        setTotalActive(data.total_active || data.anomalies.length);
        setSystemicStressIndex(data.systemic_stress_index || 14.5);
        setIsDemo(false);
      } else {
        setAnomalies(FALLBACK_ANOMALIES);
        setTotalActive(FALLBACK_ANOMALIES.length);
        setSystemicStressIndex(18.4);
        setIsDemo(true);
      }
    } catch {
      setAnomalies(FALLBACK_ANOMALIES);
      setTotalActive(FALLBACK_ANOMALIES.length);
      setSystemicStressIndex(18.4);
      setIsDemo(true);
    } finally {
      setIsLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchAnomalies();
  }, [fetchAnomalies]);

  return {
    anomalies,
    totalActive,
    systemicStressIndex,
    isLoading,
    isError,
    error,
    isDemo,
    refresh: fetchAnomalies,
  };
}
