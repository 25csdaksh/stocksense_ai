"use client";

import { useState, useEffect, useCallback } from "react";
import { analyticsApi } from "@/lib/api/analytics";
import { TechnicalAnalyticsResponse } from "@/types";

const FALLBACK_TECHNICALS: Record<string, TechnicalAnalyticsResponse> = {
  default: {
    ticker: "GENERIC",
    sma_20: 2940.5,
    sma_50: 2880.2,
    ema_20: 2955.0,
    rsi_14: 58.4,
    macd: {
      macd: 14.8,
      signal: 11.2,
      histogram: 3.6,
      macd_line: 14.8,
      signal_line: 11.2,
    },
    bollinger_bands: {
      upper: 3050.0,
      middle: 2940.5,
      lower: 2831.0,
      bandwidth: 7.45,
    },
    atr_14: 48.2,
    realized_volatility_20d_pct: 18.5,
    technical_bias: "BULLISH",
  },
};

export function useStockTechnicals(ticker: string) {
  const [technicals, setTechnicals] = useState<TechnicalAnalyticsResponse | null>(null);
  const [isLoading, setIsLoading] = useState<boolean>(true);
  const [isError, setIsError] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);
  const [isDemo, setIsDemo] = useState<boolean>(false);

  const fetchTechnicals = useCallback(async () => {
    if (!ticker) return;
    setIsLoading(true);
    setIsError(false);
    setError(null);

    try {
      const data = await analyticsApi.getTechnicalAnalysis(ticker);
      if (data && typeof data.rsi_14 === "number") {
        setTechnicals(data);
        setIsDemo(false);
      } else {
        setTechnicals({ ...FALLBACK_TECHNICALS.default, ticker });
        setIsDemo(true);
      }
    } catch {
      setTechnicals({ ...FALLBACK_TECHNICALS.default, ticker });
      setIsDemo(true);
    } finally {
      setIsLoading(false);
    }
  }, [ticker]);

  useEffect(() => {
    fetchTechnicals();
  }, [fetchTechnicals]);

  return {
    technicals,
    isLoading,
    isError,
    error,
    isDemo,
    refresh: fetchTechnicals,
  };
}
