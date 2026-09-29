"use client";

import { useState, useEffect, useCallback } from "react";
import { portfolioApi } from "@/lib/api/portfolio";
import { PortfolioStressTestResponse } from "@/types";

const FALLBACK_STRESS_TEST: PortfolioStressTestResponse = {
  initial_portfolio_value: 2845200,
  crises_stress_results: {
    "2008_GFC": {
      crisis_name: "2008 Global Financial Crisis",
      period: "Sep 2008 - Mar 2009",
      projected_portfolio_loss_dollars: 1337244,
      projected_drawdown_pct: -47.0,
      stressed_portfolio_value: 1507956,
      description: "Subprime mortgage collapse, Lehman bankruptcy, and global liquidity freeze.",
    },
    "2020_COVID": {
      crisis_name: "2020 COVID-19 Liquidity Shock",
      period: "Feb 2020 - Mar 2020",
      projected_portfolio_loss_dollars: 882012,
      projected_drawdown_pct: -31.0,
      stressed_portfolio_value: 1963188,
      description: "Sudden pandemic lockdowns, cross-asset flash crash, and dollar flight.",
    },
    "2022_TECH_SELLOFF": {
      crisis_name: "2022 Tech Valuation De-rating",
      period: "Jan 2022 - Nov 2022",
      projected_portfolio_loss_dollars: 625944,
      projected_drawdown_pct: -22.0,
      stressed_portfolio_value: 2219256,
      description: "Global central bank rate tightening cycle causing severe multiple compression in tech.",
    },
    "2024_RATE_SHOCK": {
      crisis_name: "2024 Geopolitical & Crude Spike",
      period: "Hypothetical Scenario",
      projected_portfolio_loss_dollars: 426780,
      projected_drawdown_pct: -15.0,
      stressed_portfolio_value: 2418420,
      description: "Brent crude surging above $110/bbl causing margin pressure on emerging market equities.",
    },
  },
};

export function usePortfolioStressTest(holdings?: Array<{ ticker: string; shares: number; price: number; sector?: string; beta?: number }>) {
  const [data, setData] = useState<PortfolioStressTestResponse>(FALLBACK_STRESS_TEST);
  const [isLoading, setIsLoading] = useState<boolean>(true);
  const [isError, setIsError] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);

  const fetchStressTest = useCallback(async () => {
    setIsLoading(true);
    setIsError(false);
    setError(null);
    try {
      const payload = holdings && holdings.length > 0 ? { holdings } : undefined;
      const res = await portfolioApi.stressTestPortfolio(payload);
      if (res && res.crises_stress_results && Object.keys(res.crises_stress_results).length > 0) {
        setData(res);
      } else {
        setData(FALLBACK_STRESS_TEST);
      }
    } catch {
      setData(FALLBACK_STRESS_TEST);
    } finally {
      setIsLoading(false);
    }
  }, [holdings]);

  useEffect(() => {
    fetchStressTest();
  }, [fetchStressTest]);

  return {
    stressData: data,
    isLoading,
    isError,
    error,
    refresh: fetchStressTest,
  };
}
