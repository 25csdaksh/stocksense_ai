"use client";

import { useState, useEffect, useCallback } from "react";
import { analyticsApi } from "@/lib/api/analytics";
import { StockDNAResponse } from "@/types";

const FALLBACK_DNA: Record<string, StockDNAResponse> = {
  "RELIANCE.NS": {
    ticker: "RELIANCE.NS",
    dominant_persona: "Quality Value Compounder",
    summary: "High capital efficiency and dominant market scale with balanced cash flow generation.",
    factor_scores: {
      value: 68.0,
      growth: 74.0,
      quality: 82.0,
      momentum: 65.0,
      volatility: 42.0,
    },
    radar_data: [
      { factor: "Value", score: 68.0, fullMark: 100 },
      { factor: "Growth", score: 74.0, fullMark: 100 },
      { factor: "Quality", score: 82.0, fullMark: 100 },
      { factor: "Momentum", score: 65.0, fullMark: 100 },
      { factor: "Low Volatility", score: 58.0, fullMark: 100 },
    ],
  },
  "TCS.NS": {
    ticker: "TCS.NS",
    dominant_persona: "High Quality Compounder",
    summary: "Exceptional Return on Equity (ROE > 45%), zero debt, and high shareholder dividend distributions.",
    factor_scores: {
      value: 52.0,
      growth: 68.0,
      quality: 94.0,
      momentum: 72.0,
      volatility: 34.0,
    },
    radar_data: [
      { factor: "Value", score: 52.0, fullMark: 100 },
      { factor: "Growth", score: 68.0, fullMark: 100 },
      { factor: "Quality", score: 94.0, fullMark: 100 },
      { factor: "Momentum", score: 72.0, fullMark: 100 },
      { factor: "Low Volatility", score: 66.0, fullMark: 100 },
    ],
  },
  "INFY.NS": {
    ticker: "INFY.NS",
    dominant_persona: "Quality Growth Franchise",
    summary: "Solid operating margins and robust global enterprise IT positioning with strong FCF yield.",
    factor_scores: {
      value: 58.0,
      growth: 65.0,
      quality: 88.0,
      momentum: 59.0,
      volatility: 38.0,
    },
    radar_data: [
      { factor: "Value", score: 58.0, fullMark: 100 },
      { factor: "Growth", score: 65.0, fullMark: 100 },
      { factor: "Quality", score: 88.0, fullMark: 100 },
      { factor: "Momentum", score: 59.0, fullMark: 100 },
      { factor: "Low Volatility", score: 62.0, fullMark: 100 },
    ],
  },
  "HDFCBANK.NS": {
    ticker: "HDFCBANK.NS",
    dominant_persona: "Core Banking Compounder",
    summary: "Leading private retail & wholesale deposit franchise with stable net interest margins.",
    factor_scores: {
      value: 72.0,
      growth: 62.0,
      quality: 86.0,
      momentum: 54.0,
      volatility: 36.0,
    },
    radar_data: [
      { factor: "Value", score: 72.0, fullMark: 100 },
      { factor: "Growth", score: 62.0, fullMark: 100 },
      { factor: "Quality", score: 86.0, fullMark: 100 },
      { factor: "Momentum", score: 54.0, fullMark: 100 },
      { factor: "Low Volatility", score: 64.0, fullMark: 100 },
    ],
  },
};

export function useStockDNA(ticker: string) {
  const [dna, setDna] = useState<StockDNAResponse | null>(null);
  const [isLoading, setIsLoading] = useState<boolean>(true);
  const [isError, setIsError] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);
  const [isDemo, setIsDemo] = useState<boolean>(false);

  const fetchStockDNA = useCallback(async () => {
    if (!ticker) return;
    setIsLoading(true);
    setIsError(false);
    setError(null);

    try {
      const data = await analyticsApi.getStockDNA(ticker);
      if (data && data.factor_scores) {
        setDna(data);
        setIsDemo(false);
      } else {
        const fallback = FALLBACK_DNA[ticker] || {
          ticker,
          dominant_persona: "Balanced Quantitative Asset",
          summary: "Factor scores summarize the available quantitative characteristics across multiple dimensions.",
          factor_scores: {
            value: 60.0,
            growth: 65.0,
            quality: 75.0,
            momentum: 60.0,
            volatility: 40.0,
          },
          radar_data: [
            { factor: "Value", score: 60.0, fullMark: 100 },
            { factor: "Growth", score: 65.0, fullMark: 100 },
            { factor: "Quality", score: 75.0, fullMark: 100 },
            { factor: "Momentum", score: 60.0, fullMark: 100 },
            { factor: "Low Volatility", score: 60.0, fullMark: 100 },
          ],
        };
        setDna(fallback);
        setIsDemo(true);
      }
    } catch {
      const fallback = FALLBACK_DNA[ticker] || {
        ticker,
        dominant_persona: "Balanced Quantitative Asset",
        summary: "Factor scores summarize the available quantitative characteristics across multiple dimensions.",
        factor_scores: {
          value: 60.0,
          growth: 65.0,
          quality: 75.0,
          momentum: 60.0,
          volatility: 40.0,
        },
        radar_data: [
          { factor: "Value", score: 60.0, fullMark: 100 },
          { factor: "Growth", score: 65.0, fullMark: 100 },
          { factor: "Quality", score: 75.0, fullMark: 100 },
          { factor: "Momentum", score: 60.0, fullMark: 100 },
          { factor: "Low Volatility", score: 60.0, fullMark: 100 },
        ],
      };
      setDna(fallback);
      setIsDemo(true);
    } finally {
      setIsLoading(false);
    }
  }, [ticker]);

  useEffect(() => {
    fetchStockDNA();
  }, [fetchStockDNA]);

  return {
    dna,
    isLoading,
    isError,
    error,
    isDemo,
    refresh: fetchStockDNA,
  };
}
