"use client";

import { useState, useEffect, useCallback } from "react";
import { stocksApi } from "@/lib/api/stocks";
import { watchlistApi } from "@/lib/api/watchlist";
import { StockQuote } from "@/types";

export interface StockQuoteState {
  quote: StockQuote | null;
  isInWatchlist: boolean;
  isLoading: boolean;
  isError: boolean;
  error: string | null;
  isDemo: boolean;
  toggleWatchlist: () => Promise<void>;
  refresh: () => Promise<void>;
}

// Fallback seed quotes for standard equities
const FALLBACK_QUOTES: Record<string, Partial<StockQuote>> = {
  "RELIANCE.NS": {
    ticker: "RELIANCE.NS",
    name: "Reliance Industries Limited",
    price: 2984.5,
    change: 32.1,
    change_pct: 1.09,
    open: 2955.0,
    high: 2998.0,
    low: 2942.0,
    previous_close: 2952.4,
    volume: 8420000,
    market_cap: 20185000000000,
    pe_ratio: 28.4,
    week_52_high: 3217.9,
    week_52_low: 2220.3,
  },
  "TCS.NS": {
    ticker: "TCS.NS",
    name: "Tata Consultancy Services Limited",
    price: 4210.8,
    change: 54.3,
    change_pct: 1.31,
    open: 4170.0,
    high: 4235.0,
    low: 4155.0,
    previous_close: 4156.5,
    volume: 3120000,
    market_cap: 15240000000000,
    pe_ratio: 31.2,
    week_52_high: 4592.25,
    week_52_low: 3313.0,
  },
  "INFY.NS": {
    ticker: "INFY.NS",
    name: "Infosys Limited",
    price: 1845.2,
    change: -12.4,
    change_pct: -0.67,
    open: 1860.0,
    high: 1872.0,
    low: 1838.0,
    previous_close: 1857.6,
    volume: 6840000,
    market_cap: 7650000000000,
    pe_ratio: 26.8,
    week_52_high: 1991.45,
    week_52_low: 1358.35,
  },
  "HDFCBANK.NS": {
    ticker: "HDFCBANK.NS",
    name: "HDFC Bank Limited",
    price: 1642.0,
    change: 8.5,
    change_pct: 0.52,
    open: 1635.0,
    high: 1655.0,
    low: 1630.0,
    previous_close: 1633.5,
    volume: 12400000,
    market_cap: 12480000000000,
    pe_ratio: 19.5,
    week_52_high: 1794.0,
    week_52_low: 1363.55,
  },
};

export function useStockQuote(ticker: string): StockQuoteState {
  const [quote, setQuote] = useState<StockQuote | null>(null);
  const [isInWatchlist, setIsInWatchlist] = useState<boolean>(false);
  const [isLoading, setIsLoading] = useState<boolean>(true);
  const [isError, setIsError] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);
  const [isDemo, setIsDemo] = useState<boolean>(false);

  const fetchQuoteAndWatchlist = useCallback(async () => {
    if (!ticker) return;
    setIsLoading(true);
    setIsError(false);
    setError(null);

    try {
      const [quoteData, watchlistData] = await Promise.all([
        stocksApi.getStockQuote(ticker),
        watchlistApi.getWatchlist().catch(() => []),
      ]);

      if (quoteData && quoteData.price) {
        setQuote(quoteData);
        setIsDemo(Boolean(quoteData.is_synthetic || quoteData.is_demo));
      } else {
        const fallback = FALLBACK_QUOTES[ticker] || {
          ticker,
          name: ticker,
          price: 2450.0,
          change: 18.5,
          change_pct: 0.76,
          open: 2435.0,
          high: 2468.0,
          low: 2420.0,
          previous_close: 2431.5,
          volume: 4500000,
          week_52_high: 2800.0,
          week_52_low: 1900.0,
        };
        setQuote(fallback as StockQuote);
        setIsDemo(true);
      }

      const inWatch = Array.isArray(watchlistData) && watchlistData.some((w: any) => (w.ticker || w.symbol) === ticker);
      setIsInWatchlist(inWatch);
    } catch (err: any) {
      console.warn(`Quote API failed for ${ticker}, using fallback:`, err.message);
      const fallback = FALLBACK_QUOTES[ticker] || {
        ticker,
        name: ticker,
        price: 2450.0,
        change: 18.5,
        change_pct: 0.76,
        open: 2435.0,
        high: 2468.0,
        low: 2420.0,
        previous_close: 2431.5,
        volume: 4500000,
        week_52_high: 2800.0,
        week_52_low: 1900.0,
      };
      setQuote(fallback as StockQuote);
      setIsDemo(true);
    } finally {
      setIsLoading(false);
    }
  }, [ticker]);

  const toggleWatchlist = async () => {
    if (!ticker) return;
    try {
      if (isInWatchlist) {
        await watchlistApi.removeFromWatchlist(ticker);
        setIsInWatchlist(false);
      } else {
        await watchlistApi.addToWatchlist(ticker);
        setIsInWatchlist(true);
      }
    } catch (err) {
      console.error("Watchlist toggle error:", err);
      // Optimistic fallback for local UI toggle
      setIsInWatchlist((prev) => !prev);
    }
  };

  useEffect(() => {
    fetchQuoteAndWatchlist();
  }, [fetchQuoteAndWatchlist]);

  return {
    quote,
    isInWatchlist,
    isLoading,
    isError,
    error,
    isDemo,
    toggleWatchlist,
    refresh: fetchQuoteAndWatchlist,
  };
}
