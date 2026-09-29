"use client";

import { useState, useEffect, useCallback } from "react";
import { stocksApi } from "@/lib/api/stocks";
import { OHLCV } from "@/types";

export type Timeframe = "1D" | "1W" | "1M" | "3M" | "6M" | "1Y";

export interface MarketChartState {
  ticker: string;
  setTicker: (ticker: string) => void;
  timeframe: Timeframe;
  setTimeframe: (tf: Timeframe) => void;
  historyData: OHLCV[];
  isLoading: boolean;
  isError: boolean;
  error: string | null;
  isDemo: boolean;
  refresh: () => Promise<void>;
}

// Generate realistic synthetic OHLCV series for fallback / demo
function generateFallbackOHLCV(days: number = 90, basePrice: number = 24500): OHLCV[] {
  const result: OHLCV[] = [];
  const now = new Date();
  let currentClose = basePrice;

  for (let i = days; i >= 0; i--) {
    const date = new Date(now.getTime() - i * 24 * 60 * 60 * 1000);
    // Skip weekends
    if (date.getDay() === 0 || date.getDay() === 6) continue;

    const changePct = (Math.random() - 0.48) * 0.018;
    const open = currentClose * (1 + (Math.random() - 0.5) * 0.004);
    const close = open * (1 + changePct);
    const high = Math.max(open, close) * (1 + Math.random() * 0.008);
    const low = Math.min(open, close) * (1 - Math.random() * 0.008);
    const volume = Math.floor(150000000 + Math.random() * 80000000);

    result.push({
      timestamp: date.toISOString().split("T")[0],
      open: parseFloat(open.toFixed(2)),
      high: parseFloat(high.toFixed(2)),
      low: parseFloat(low.toFixed(2)),
      close: parseFloat(close.toFixed(2)),
      volume,
    });

    currentClose = close;
  }

  return result;
}

const TIMEFRAME_MAP: Record<Timeframe, { timeframe: string; interval: string; days: number }> = {
  "1D": { timeframe: "1m", interval: "1d", days: 30 },
  "1W": { timeframe: "1m", interval: "1d", days: 14 },
  "1M": { timeframe: "1m", interval: "1d", days: 30 },
  "3M": { timeframe: "3m", interval: "1d", days: 90 },
  "6M": { timeframe: "6m", interval: "1d", days: 180 },
  "1Y": { timeframe: "1y", interval: "1d", days: 365 },
};

export function useMarketChart(initialTicker: string = "^NSEI"): MarketChartState {
  const [ticker, setTicker] = useState<string>(initialTicker);
  const [timeframe, setTimeframe] = useState<Timeframe>("3M");
  const [historyData, setHistoryData] = useState<OHLCV[]>([]);
  const [isLoading, setIsLoading] = useState<boolean>(true);
  const [isError, setIsError] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);
  const [isDemo, setIsDemo] = useState<boolean>(false);

  const fetchHistory = useCallback(async () => {
    setIsLoading(true);
    setIsError(false);
    setError(null);

    const config = TIMEFRAME_MAP[timeframe];

    try {
      const response = await stocksApi.getStockHistory(ticker, config.timeframe, config.interval);
      if (response && response.data && response.data.length > 0) {
        setHistoryData(response.data);
        setIsDemo(Boolean(response.is_demo));
      } else {
        const base = ticker.includes("NSEI") ? 24800 : ticker.includes("BSESN") ? 81400 : 2800;
        setHistoryData(generateFallbackOHLCV(config.days, base));
        setIsDemo(true);
      }
    } catch (err: any) {
      console.warn(`Market chart data unavailable for ${ticker}, generating demo series:`, err.message);
      const base = ticker.includes("NSEI") ? 24800 : ticker.includes("BSESN") ? 81400 : 2800;
      setHistoryData(generateFallbackOHLCV(config.days, base));
      setIsDemo(true);
    } finally {
      setIsLoading(false);
    }
  }, [ticker, timeframe]);

  useEffect(() => {
    fetchHistory();
  }, [fetchHistory]);

  return {
    ticker,
    setTicker,
    timeframe,
    setTimeframe,
    historyData,
    isLoading,
    isError,
    error,
    isDemo,
    refresh: fetchHistory,
  };
}
