"use client";

import { useState, useEffect, useCallback } from "react";
import { analyticsApi } from "@/lib/api/analytics";
import { CorrelationMatrixResponse } from "@/types";

const FALLBACK_CORRELATION: CorrelationMatrixResponse = {
  assets: ["RELIANCE.NS", "TCS.NS", "INFY.NS", "HDFCBANK.NS", "ICICIBANK.NS", "^NSEI"],
  matrix: [
    [1.0, 0.42, 0.38, 0.51, 0.48, 0.78],
    [0.42, 1.0, 0.84, 0.35, 0.39, 0.65],
    [0.38, 0.84, 1.0, 0.31, 0.36, 0.62],
    [0.51, 0.35, 0.31, 1.0, 0.82, 0.81],
    [0.48, 0.39, 0.36, 0.82, 1.0, 0.79],
    [0.78, 0.65, 0.62, 0.81, 0.79, 1.0],
  ],
  method: "pearson",
  top_pairs: [
    { asset_a: "TCS.NS", asset_b: "INFY.NS", correlation: 0.84 },
    { asset_a: "HDFCBANK.NS", asset_b: "ICICIBANK.NS", correlation: 0.82 },
    { asset_a: "HDFCBANK.NS", asset_b: "^NSEI", correlation: 0.81 },
    { asset_a: "RELIANCE.NS", asset_b: "^NSEI", correlation: 0.78 },
  ],
  observations: 126,
};

export function useStockCorrelations(ticker: string, method: string = "pearson") {
  const [correlations, setCorrelations] = useState<CorrelationMatrixResponse | null>(null);
  const [isLoading, setIsLoading] = useState<boolean>(true);
  const [isError, setIsError] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);
  const [isDemo, setIsDemo] = useState<boolean>(false);

  const fetchCorrelations = useCallback(async () => {
    setIsLoading(true);
    setIsError(false);
    setError(null);

    try {
      const data = await analyticsApi.getCorrelationMatrix(method);
      if (data && data.assets && data.assets.length > 0) {
        setCorrelations(data);
        setIsDemo(false);
      } else {
        setCorrelations(FALLBACK_CORRELATION);
        setIsDemo(true);
      }
    } catch {
      setCorrelations(FALLBACK_CORRELATION);
      setIsDemo(true);
    } finally {
      setIsLoading(false);
    }
  }, [method]);

  useEffect(() => {
    fetchCorrelations();
  }, [fetchCorrelations]);

  // Derive active ticker's correlation with benchmark and peers
  const activeTickerIndex = correlations?.assets.indexOf(ticker) ?? -1;
  const benchmarkIndex = correlations?.assets.findIndex((a) => a.includes("NSEI") || a.includes("NIFTY")) ?? -1;

  const benchmarkCorrelation =
    activeTickerIndex >= 0 && benchmarkIndex >= 0 && correlations?.matrix[activeTickerIndex]
      ? correlations.matrix[activeTickerIndex][benchmarkIndex]
      : 0.76;

  return {
    correlations,
    benchmarkCorrelation,
    isLoading,
    isError,
    error,
    isDemo,
    refresh: fetchCorrelations,
  };
}
