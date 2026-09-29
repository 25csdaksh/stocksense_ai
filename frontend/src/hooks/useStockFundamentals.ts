"use client";

import { useState, useEffect, useCallback } from "react";
import { stocksApi } from "@/lib/api/stocks";
import { FundamentalOverviewResponse } from "@/types";

const FALLBACK_FUNDAMENTALS: Record<string, FundamentalOverviewResponse> = {
  "RELIANCE.NS": {
    ticker: "RELIANCE.NS",
    name: "Reliance Industries Limited",
    sector: "Energy / Conglomerate",
    valuation: {
      pe_ratio: 28.4,
      forward_pe: 24.2,
      pb_ratio: 2.35,
      ev_ebitda: 14.8,
      fcf_yield_pct: 4.2,
    },
    profitability: {
      gross_margin_pct: 34.8,
      operating_margin_pct: 18.2,
      net_margin_pct: 10.4,
      roe_pct: 12.8,
      roa_pct: 6.4,
    },
    financial_health: {
      current_ratio: 1.25,
      debt_to_equity: 0.42,
      interest_coverage_ratio: 6.8,
      altman_z_score: 3.45,
      health_score: "STRONG",
    },
  },
  "TCS.NS": {
    ticker: "TCS.NS",
    name: "Tata Consultancy Services Limited",
    sector: "Technology / IT Services",
    valuation: {
      pe_ratio: 31.2,
      forward_pe: 27.5,
      pb_ratio: 12.8,
      ev_ebitda: 21.4,
      fcf_yield_pct: 3.8,
    },
    profitability: {
      gross_margin_pct: 42.1,
      operating_margin_pct: 26.5,
      net_margin_pct: 19.8,
      roe_pct: 48.2,
      roa_pct: 32.4,
    },
    financial_health: {
      current_ratio: 2.85,
      debt_to_equity: 0.02,
      interest_coverage_ratio: 84.5,
      altman_z_score: 8.92,
      health_score: "EXCELLENT",
    },
  },
  "INFY.NS": {
    ticker: "INFY.NS",
    name: "Infosys Limited",
    sector: "Technology / IT Services",
    valuation: {
      pe_ratio: 26.8,
      forward_pe: 23.4,
      pb_ratio: 7.9,
      ev_ebitda: 17.6,
      fcf_yield_pct: 4.5,
    },
    profitability: {
      gross_margin_pct: 39.4,
      operating_margin_pct: 21.8,
      net_margin_pct: 16.2,
      roe_pct: 31.5,
      roa_pct: 21.0,
    },
    financial_health: {
      current_ratio: 2.1,
      debt_to_equity: 0.08,
      interest_coverage_ratio: 42.0,
      altman_z_score: 6.78,
      health_score: "EXCELLENT",
    },
  },
  "HDFCBANK.NS": {
    ticker: "HDFCBANK.NS",
    name: "HDFC Bank Limited",
    sector: "Financial Services / Banking",
    valuation: {
      pe_ratio: 19.5,
      forward_pe: 16.8,
      pb_ratio: 2.8,
      ev_ebitda: null,
      fcf_yield_pct: null,
    },
    profitability: {
      gross_margin_pct: 58.2,
      operating_margin_pct: 41.5,
      net_margin_pct: 24.6,
      roe_pct: 16.4,
      roa_pct: 1.95,
    },
    financial_health: {
      current_ratio: 1.15,
      debt_to_equity: 6.4,
      interest_coverage_ratio: null,
      altman_z_score: null,
      health_score: "STABLE",
    },
  },
};

export function useStockFundamentals(ticker: string) {
  const [fundamentals, setFundamentals] = useState<FundamentalOverviewResponse | null>(null);
  const [isLoading, setIsLoading] = useState<boolean>(true);
  const [isError, setIsError] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);
  const [isDemo, setIsDemo] = useState<boolean>(false);

  const fetchFundamentals = useCallback(async () => {
    if (!ticker) return;
    setIsLoading(true);
    setIsError(false);
    setError(null);

    try {
      const data = await stocksApi.getFundamentalOverview(ticker);
      if (data && data.valuation) {
        setFundamentals(data);
        setIsDemo(false);
      } else {
        const fallback = FALLBACK_FUNDAMENTALS[ticker] || {
          ticker,
          name: ticker,
          sector: "Equity Universe",
          valuation: {
            pe_ratio: 24.5,
            forward_pe: 21.0,
            pb_ratio: 3.2,
            ev_ebitda: 14.5,
            fcf_yield_pct: 3.5,
          },
          profitability: {
            gross_margin_pct: 35.0,
            operating_margin_pct: 18.5,
            net_margin_pct: 12.0,
            roe_pct: 16.5,
            roa_pct: 8.2,
          },
          financial_health: {
            current_ratio: 1.8,
            debt_to_equity: 0.35,
            interest_coverage_ratio: 12.4,
            altman_z_score: 4.1,
            health_score: "STABLE",
          },
        };
        setFundamentals(fallback);
        setIsDemo(true);
      }
    } catch {
      const fallback = FALLBACK_FUNDAMENTALS[ticker] || {
        ticker,
        name: ticker,
        sector: "Equity Universe",
        valuation: {
          pe_ratio: 24.5,
          forward_pe: 21.0,
          pb_ratio: 3.2,
          ev_ebitda: 14.5,
          fcf_yield_pct: 3.5,
        },
        profitability: {
          gross_margin_pct: 35.0,
          operating_margin_pct: 18.5,
          net_margin_pct: 12.0,
          roe_pct: 16.5,
          roa_pct: 8.2,
        },
        financial_health: {
          current_ratio: 1.8,
          debt_to_equity: 0.35,
          interest_coverage_ratio: 12.4,
          altman_z_score: 4.1,
          health_score: "STABLE",
        },
      };
      setFundamentals(fallback);
      setIsDemo(true);
    } finally {
      setIsLoading(false);
    }
  }, [ticker]);

  useEffect(() => {
    fetchFundamentals();
  }, [fetchFundamentals]);

  return {
    fundamentals,
    isLoading,
    isError,
    error,
    isDemo,
    refresh: fetchFundamentals,
  };
}
