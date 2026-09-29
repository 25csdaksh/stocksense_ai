"use client";

import { useState, useEffect, useCallback } from "react";
import { portfolioApi } from "@/lib/api/portfolio";
import { PortfolioSummaryResponse } from "@/types";

const FALLBACK_PORTFOLIO: PortfolioSummaryResponse = {
  total_value: 2845200,
  total_cost: 2450000,
  total_unrealized_pnl: 395200,
  total_unrealized_pnl_pct: 16.13,
  daily_pnl: 24800,
  daily_pnl_pct: 0.88,
  holdings: [
    {
      ticker: "RELIANCE.NS",
      shares: 350,
      avg_price: 2620.0,
      current_price: 2984.5,
      market_value: 1044575,
      unrealized_pnl: 127575,
      unrealized_pnl_pct: 13.91,
      weight_pct: 36.7,
    },
    {
      ticker: "TCS.NS",
      shares: 180,
      avg_price: 3680.0,
      current_price: 4210.8,
      market_value: 757944,
      unrealized_pnl: 95544,
      unrealized_pnl_pct: 14.42,
      weight_pct: 26.6,
    },
    {
      ticker: "HDFCBANK.NS",
      shares: 380,
      avg_price: 1510.0,
      current_price: 1642.0,
      market_value: 623960,
      unrealized_pnl: 50160,
      unrealized_pnl_pct: 8.74,
      weight_pct: 21.9,
    },
    {
      ticker: "INFY.NS",
      shares: 227,
      avg_price: 1480.0,
      current_price: 1845.2,
      market_value: 418860,
      unrealized_pnl: 82920,
      unrealized_pnl_pct: 24.68,
      weight_pct: 14.8,
    },
  ],
  risk_metrics: {
    portfolio_beta: 0.94,
    daily_var_95: 38400,
    sharpe_ratio: 1.82,
  },
};

const ALLOCATION_PALETTE = ["#12372A", "#2F5D50", "#C9A227", "#4E7B6C", "#D4AF37", "#8FA998"];

export function usePortfolio() {
  const [portfolio, setPortfolio] = useState<PortfolioSummaryResponse>(FALLBACK_PORTFOLIO);
  const [isLoading, setIsLoading] = useState<boolean>(true);
  const [isError, setIsError] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);
  const [isDemo, setIsDemo] = useState<boolean>(false);

  const fetchPortfolio = useCallback(async () => {
    setIsLoading(true);
    setIsError(false);
    setError(null);
    try {
      const data = await portfolioApi.getPortfolioSummary();
      if (data && data.holdings && data.holdings.length > 0) {
        setPortfolio(data);
        setIsDemo(false);
      } else {
        setPortfolio(FALLBACK_PORTFOLIO);
        setIsDemo(true);
      }
    } catch {
      setPortfolio(FALLBACK_PORTFOLIO);
      setIsDemo(true);
    } finally {
      setIsLoading(false);
    }
  }, []);

  const allocationData = (portfolio.holdings || []).map((h, i) => ({
    name: h.ticker,
    value: h.weight_pct || parseFloat(((h.market_value / (portfolio.total_value || 1)) * 100).toFixed(1)),
    color: ALLOCATION_PALETTE[i % ALLOCATION_PALETTE.length],
  }));

  useEffect(() => {
    fetchPortfolio();
  }, [fetchPortfolio]);

  return {
    portfolio,
    allocationData,
    isLoading,
    isError,
    error,
    isDemo,
    refresh: fetchPortfolio,
  };
}
