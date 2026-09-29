"use client";

import { useState, useEffect, useCallback } from "react";
import { analyticsApi } from "@/lib/api/analytics";
import { AnomalyItem, TickerAnomalyResponse } from "@/types";

const FALLBACK_ANOMALIES: Record<string, AnomalyItem[]> = {
  "RELIANCE.NS": [
    {
      ticker: "RELIANCE.NS",
      timestamp: new Date(Date.now() - 3600000 * 4).toISOString(),
      anomaly_type: "VOLUME_SPIKE",
      severity_score: 0.74,
      isolation_score: -0.142,
      summary: "Volume burst (2.8σ from 20d mean) & High-Low spread expansion (4.8%)",
      metrics: {
        close: 2984.5,
        volume: 14200000,
        volume_zscore: 2.85,
        log_return_pct: 1.45,
        hl_spread_pct: 4.8,
      },
    },
  ],
  "TCS.NS": [
    {
      ticker: "TCS.NS",
      timestamp: new Date(Date.now() - 3600000 * 12).toISOString(),
      anomaly_type: "VOLATILITY_BURST",
      severity_score: 0.62,
      isolation_score: -0.098,
      summary: "Price gap expansion (+1.85% intraday) post deal announcement",
      metrics: {
        close: 4210.8,
        volume: 4850000,
        volume_zscore: 2.1,
        log_return_pct: 1.85,
        hl_spread_pct: 3.2,
      },
    },
  ],
};

export function useStockAnomalies(ticker: string) {
  const [data, setData] = useState<TickerAnomalyResponse | null>(null);
  const [anomalies, setAnomalies] = useState<AnomalyItem[]>([]);
  const [isLoading, setIsLoading] = useState<boolean>(true);
  const [isError, setIsError] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);
  const [isDemo, setIsDemo] = useState<boolean>(false);

  const fetchAnomalies = useCallback(async () => {
    if (!ticker) return;
    setIsLoading(true);
    setIsError(false);
    setError(null);

    try {
      const resp = await analyticsApi.getTickerAnomalies(ticker);
      if (resp && Array.isArray(resp.anomalies)) {
        setData(resp);
        setAnomalies(resp.anomalies);
        setIsDemo(false);
      } else {
        const fallbackList = FALLBACK_ANOMALIES[ticker] || [];
        setAnomalies(fallbackList);
        setData({
          ticker,
          anomalies: fallbackList,
          volatility_regime: {
            current_volatility_pct: 18.4,
            volatility_regime: "NORMAL_VOLATILITY",
            garch_forecast_5d: [18.5, 18.4, 18.2, 18.0, 17.9],
          },
          volume_spike: {
            is_spike: false,
            volume_ratio: 1.12,
            z_score: 0.85,
          },
        });
        setIsDemo(true);
      }
    } catch {
      const fallbackList = FALLBACK_ANOMALIES[ticker] || [];
      setAnomalies(fallbackList);
      setData({
        ticker,
        anomalies: fallbackList,
        volatility_regime: {
          current_volatility_pct: 18.4,
          volatility_regime: "NORMAL_VOLATILITY",
          garch_forecast_5d: [18.5, 18.4, 18.2, 18.0, 17.9],
        },
        volume_spike: {
          is_spike: false,
          volume_ratio: 1.12,
          z_score: 0.85,
        },
      });
      setIsDemo(true);
    } finally {
      setIsLoading(false);
    }
  }, [ticker]);

  useEffect(() => {
    fetchAnomalies();
  }, [fetchAnomalies]);

  return {
    data,
    anomalies,
    volatilityRegime: data?.volatility_regime,
    volumeSpike: data?.volume_spike,
    isLoading,
    isError,
    error,
    isDemo,
    refresh: fetchAnomalies,
  };
}
