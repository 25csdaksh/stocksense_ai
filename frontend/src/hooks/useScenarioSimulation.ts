"use client";

import { useState, useCallback, useEffect } from "react";
import { scenariosApi } from "@/lib/api/scenarios";
import { portfolioApi } from "@/lib/api/portfolio";
import {
  ScenarioMode,
  MonteCarloRequest,
  MonteCarloResponse,
  HistoricalStressRequest,
  HistoricalStressResponse,
  MacroShockRequest,
  MacroShockResponse,
  PortfolioStressTestResponse,
} from "@/types";

export interface ScenarioSimulationParams {
  // Common
  targetType: "STOCK" | "PORTFOLIO";
  ticker: string;
  mode: ScenarioMode;

  // Monte Carlo Merton Jump Diffusion
  driftAnnualized: number;
  volatilityAnnualized: number;
  days: number;
  iterations: number;
  jumpIntensity: number;

  // Historical Stress
  sector: string;
  beta: number;

  // Macro Shock
  rateShockBps: number;
  inflationShockPct: number;
  oilShockPct: number;
  gdpShockPct: number;
}

export const DEFAULT_SCENARIO_PARAMS: ScenarioSimulationParams = {
  targetType: "STOCK",
  ticker: "RELIANCE.NS",
  mode: "MONTE_CARLO",

  // Monte Carlo
  driftAnnualized: 0.08,
  volatilityAnnualized: 0.25,
  days: 90,
  iterations: 5000,
  jumpIntensity: 0.05,

  // Historical Stress
  sector: "Energy",
  beta: 1.05,

  // Macro Shock
  rateShockBps: 100.0,
  inflationShockPct: 1.5,
  oilShockPct: 20.0,
  gdpShockPct: -1.0,
};

export function useScenarioSimulation(initialTicker?: string, initialMode?: ScenarioMode, initialTargetType?: "STOCK" | "PORTFOLIO") {
  const [params, setParams] = useState<ScenarioSimulationParams>({
    ...DEFAULT_SCENARIO_PARAMS,
    ticker: initialTicker || DEFAULT_SCENARIO_PARAMS.ticker,
    mode: initialMode || (initialTargetType === "PORTFOLIO" ? "PORTFOLIO_STRESS" : DEFAULT_SCENARIO_PARAMS.mode),
    targetType: initialTargetType || (initialMode === "PORTFOLIO_STRESS" ? "PORTFOLIO" : "STOCK"),
  });

  const [loadingStage, setLoadingStage] = useState<string>("idle");
  const [isLoading, setIsLoading] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);
  const [lastRunTimestamp, setLastRunTimestamp] = useState<string | null>(null);

  // Result stores
  const [monteCarloResult, setMonteCarloResult] = useState<MonteCarloResponse | null>(null);
  const [historicalStressResult, setHistoricalStressResult] = useState<HistoricalStressResponse | null>(null);
  const [macroShockResult, setMacroShockResult] = useState<MacroShockResponse | null>(null);
  const [portfolioStressResult, setPortfolioStressResult] = useState<PortfolioStressTestResponse | null>(null);

  // Parameter Updater
  const updateParam = useCallback(<K extends keyof ScenarioSimulationParams>(
    key: K,
    value: ScenarioSimulationParams[K]
  ) => {
    setParams((prev) => ({ ...prev, [key]: value }));
  }, []);

  const resetParams = useCallback(() => {
    setParams((prev) => ({
      ...DEFAULT_SCENARIO_PARAMS,
      ticker: prev.ticker,
      targetType: prev.targetType,
      mode: prev.mode,
    }));
  }, []);

  const runSimulation = useCallback(async () => {
    if (isLoading) return;
    setIsLoading(true);
    setError(null);

    try {
      if (params.mode === "MONTE_CARLO") {
        setLoadingStage("Preparing Merton Jump Diffusion parameters...");
        await new Promise((resolve) => setTimeout(resolve, 200));

        setLoadingStage("Generating 5,000+ stochastic price paths...");
        const req: MonteCarloRequest = {
          ticker: params.ticker,
          drift_annualized: params.driftAnnualized,
          volatility_annualized: params.volatilityAnnualized,
          days: params.days,
          iterations: params.iterations,
          jump_intensity: params.jumpIntensity,
        };

        const res = await scenariosApi.runMonteCarlo(req);
        setLoadingStage("Calculating VaR, CVaR and quantile bands...");
        setMonteCarloResult(res);
      } else if (params.mode === "HISTORICAL_STRESS") {
        setLoadingStage("Loading crisis benchmarks (2008 GFC, 2020 COVID, 2022 Fed)...");
        await new Promise((resolve) => setTimeout(resolve, 200));

        const req: HistoricalStressRequest = {
          ticker: params.ticker,
          sector: params.sector,
          beta: params.beta,
        };

        setLoadingStage("Computing historical crisis replay drawdown...");
        const res = await scenariosApi.runHistoricalStress(req);
        setHistoricalStressResult(res);
      } else if (params.mode === "MACRO_SHOCK") {
        setLoadingStage("Setting multi-variable macro sensitivity elasticity...");
        await new Promise((resolve) => setTimeout(resolve, 200));

        const req: MacroShockRequest = {
          ticker: params.ticker,
          rate_shock_bps: params.rateShockBps,
          inflation_shock_pct: params.inflationShockPct,
          oil_shock_pct: params.oilShockPct,
          gdp_shock_pct: params.gdpShockPct,
        };

        setLoadingStage("Decomposing rates, inflation, oil & GDP shocks...");
        const res = await scenariosApi.runMacroShock(req);
        setMacroShockResult(res);
      } else if (params.mode === "PORTFOLIO_STRESS") {
        setLoadingStage("Loading current portfolio holdings...");
        await new Promise((resolve) => setTimeout(resolve, 200));

        setLoadingStage("Simulating multi-crisis drawdown on portfolio assets...");
        const res = await scenariosApi.runPortfolioStressTest();
        setPortfolioStressResult(res);
      }

      setLastRunTimestamp(new Date().toISOString());
      setLoadingStage("Simulation completed.");
    } catch (err: unknown) {
      const errorMsg = err instanceof Error ? err.message : "Failed to execute scenario simulation.";
      setError(errorMsg);
      setLoadingStage("Simulation failed.");
    } finally {
      setIsLoading(false);
    }
  }, [params, isLoading]);

  // Initial simulation run on mount
  useEffect(() => {
    runSimulation();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  return {
    params,
    updateParam,
    resetParams,
    runSimulation,
    isLoading,
    loadingStage,
    error,
    lastRunTimestamp,
    monteCarloResult,
    historicalStressResult,
    macroShockResult,
    portfolioStressResult,
  };
}
