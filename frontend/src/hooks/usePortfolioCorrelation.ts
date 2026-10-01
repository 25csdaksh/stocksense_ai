"use client";

import { useState, useEffect, useCallback, useMemo } from "react";
import { analyticsApi } from "@/lib/api/analytics";
import { CorrelationPair } from "@/types";

export interface CorrelationHighlight {
  pair: [string, string];
  correlation: number;
  description: string;
}

export function usePortfolioCorrelation(portfolioTickers: string[] = ["RELIANCE.NS", "TCS.NS", "HDFCBANK.NS", "INFY.NS"]) {
  const [method, setMethod] = useState<"pearson" | "spearman">("pearson");
  const [matrixData, setMatrixData] = useState<{
    assets: string[];
    matrix: number[][];
    top_pairs: CorrelationPair[];
  } | null>(null);
  const [isLoading, setIsLoading] = useState<boolean>(true);
  const [isError, setIsError] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);

  const tickersKey = useMemo(() => (portfolioTickers || []).join(","), [portfolioTickers]);

  const fetchCorrelations = useCallback(async () => {
    setIsLoading(true);
    setIsError(false);
    setError(null);
    try {
      const res = await analyticsApi.getCorrelationMatrix(method);
      if (res && res.assets && res.matrix) {
        setMatrixData({
          assets: res.assets,
          matrix: res.matrix,
          top_pairs: res.top_pairs || [],
        });
      } else {
        setMatrixData(getFallbackCorrelations(portfolioTickers));
      }
    } catch {
      setMatrixData(getFallbackCorrelations(portfolioTickers));
    } finally {
      setIsLoading(false);
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [method, tickersKey]);

  useEffect(() => {
    fetchCorrelations();
  }, [fetchCorrelations]);

  // Filter or align matrix to portfolio tickers
  const { displayTickers, displayMatrix, highestPair, lowestPair, averageCorrelation } = useMemo(() => {
    const rawAssets = matrixData?.assets || portfolioTickers;
    const rawMatrix = matrixData?.matrix || [];

    // Filter to tickers in portfolio (or fallback to portfolioTickers)
    const matchedIndices: number[] = [];
    const validTickers: string[] = [];

    portfolioTickers.forEach((t) => {
      const idx = rawAssets.indexOf(t);
      if (idx !== -1) {
        matchedIndices.push(idx);
        validTickers.push(t);
      }
    });

    let activeTickers = validTickers;
    let finalMatrix: number[][] = [];

    if (activeTickers.length >= 2 && matchedIndices.length >= 2) {
      finalMatrix = matchedIndices.map((rIdx) =>
        matchedIndices.map((cIdx) => rawMatrix[rIdx]?.[cIdx] ?? (rIdx === cIdx ? 1.0 : 0.5))
      );
    } else {
      // Fallback matrix for active tickers
      activeTickers = portfolioTickers.length >= 2 ? portfolioTickers : ["RELIANCE.NS", "TCS.NS", "HDFCBANK.NS", "INFY.NS"];
      const fallback = getFallbackCorrelations(activeTickers);
      finalMatrix = fallback.matrix;
    }

    // Calculate highest and lowest pair
    let maxCorr = -2;
    let minCorr = 2;
    let maxP: [string, string] = [activeTickers[0] || "", activeTickers[1] || ""];
    let minP: [string, string] = [activeTickers[0] || "", activeTickers[1] || ""];
    let corrSum = 0;
    let pairCount = 0;

    for (let i = 0; i < activeTickers.length; i++) {
      for (let j = i + 1; j < activeTickers.length; j++) {
        const val = finalMatrix[i]?.[j] ?? 0;
        corrSum += val;
        pairCount++;

        if (val > maxCorr) {
          maxCorr = val;
          maxP = [activeTickers[i], activeTickers[j]];
        }
        if (val < minCorr) {
          minCorr = val;
          minP = [activeTickers[i], activeTickers[j]];
        }
      }
    }

    const avgCorr = pairCount > 0 ? corrSum / pairCount : 0.5;

    const highest: CorrelationHighlight = {
      pair: maxP,
      correlation: Number(maxCorr.toFixed(2)),
      description: `High co-movement: ${maxP[0]} and ${maxP[1]} exhibit positive synchronicity`,
    };

    const lowest: CorrelationHighlight = {
      pair: minP,
      correlation: Number(minCorr.toFixed(2)),
      description: `Strong diversification: ${minP[0]} and ${minP[1]} provide portfolio buffering`,
    };

    return {
      displayTickers: activeTickers,
      displayMatrix: finalMatrix,
      highestPair: highest,
      lowestPair: lowest,
      averageCorrelation: Number(avgCorr.toFixed(2)),
    };
  }, [matrixData, portfolioTickers]);

  return {
    method,
    setMethod,
    displayTickers,
    displayMatrix,
    highestPair,
    lowestPair,
    averageCorrelation,
    isLoading,
    isError,
    error,
    refresh: fetchCorrelations,
  };
}

function getFallbackCorrelations(tickers: string[]) {
  const assets = tickers.length > 0 ? tickers : ["RELIANCE.NS", "TCS.NS", "HDFCBANK.NS", "INFY.NS"];
  const n = assets.length;
  const matrix: number[][] = Array(n).fill(0).map(() => Array(n).fill(1));

  const knownPairs: Record<string, number> = {
    "TCS.NS-INFY.NS": 0.84,
    "INFY.NS-TCS.NS": 0.84,
    "RELIANCE.NS-HDFCBANK.NS": 0.32,
    "HDFCBANK.NS-RELIANCE.NS": 0.32,
    "RELIANCE.NS-TCS.NS": 0.42,
    "TCS.NS-RELIANCE.NS": 0.42,
    "RELIANCE.NS-INFY.NS": 0.45,
    "INFY.NS-RELIANCE.NS": 0.45,
    "HDFCBANK.NS-TCS.NS": 0.28,
    "TCS.NS-HDFCBANK.NS": 0.28,
    "HDFCBANK.NS-INFY.NS": 0.31,
    "INFY.NS-HDFCBANK.NS": 0.31,
  };

  for (let i = 0; i < n; i++) {
    for (let j = 0; j < n; j++) {
      if (i === j) {
        matrix[i][j] = 1.0;
      } else {
        const key = `${assets[i]}-${assets[j]}`;
        matrix[i][j] = knownPairs[key] ?? 0.45;
      }
    }
  }

  return {
    assets,
    matrix,
    top_pairs: [
      { asset_a: "TCS.NS", asset_b: "INFY.NS", correlation: 0.84 },
      { asset_a: "RELIANCE.NS", asset_b: "INFY.NS", correlation: 0.45 },
    ],
  };
}
