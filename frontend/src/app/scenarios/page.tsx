"use client";

import React from "react";
import { useSearchParams } from "next/navigation";
import { AppLayout } from "@/components/layout/AppLayout";
import { useScenarioSimulation } from "@/hooks/useScenarioSimulation";
import {
  ScenarioHeader,
  ScenarioSelector,
  ScenarioConfiguration,
  SimulationControls,
  MonteCarloSimulation,
  ScenarioDistributionChart,
  HistoricalStressTests,
  PortfolioStressResults,
  ScenarioRiskMetrics,
  ScenarioComparison,
  AIScenarioInterpretation,
  ScenarioAssumptions,
  ScenarioLimitations,
} from "@/components/scenarios";
import { ScenarioAIContext } from "@/hooks/useScenarioAI";

function ScenariosContent() {
  const searchParams = useSearchParams();
  const initialPortfolioId = searchParams.get("portfolioId");
  const initialTicker = searchParams.get("ticker") || undefined;
  const initialTargetType = initialPortfolioId ? "PORTFOLIO" : "STOCK";

  const {
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
  } = useScenarioSimulation(
    initialTicker,
    initialPortfolioId ? "PORTFOLIO_STRESS" : "MONTE_CARLO",
    initialTargetType
  );

  // Compute AI Context
  const aiContext: ScenarioAIContext = {
    ticker: params.targetType === "STOCK" ? params.ticker : undefined,
    mode: params.mode,
    currentPrice:
      params.mode === "MONTE_CARLO"
        ? monteCarloResult?.initial_price
        : params.mode === "HISTORICAL_STRESS"
        ? historicalStressResult?.current_price
        : params.mode === "MACRO_SHOCK"
        ? macroShockResult?.current_price
        : undefined,
    expectedTerminalPrice: monteCarloResult?.expected_terminal_price_p50,
    var95: monteCarloResult?.value_at_risk_95_pct,
    cvar99: monteCarloResult?.cvar_expected_shortfall_99_pct,
    macroReturnPct: macroShockResult?.total_projected_return_pct,
    crisesDrawdowns: historicalStressResult?.scenario_results
      ? Object.fromEntries(
          Object.entries(historicalStressResult.scenario_results).map(([k, v]) => [
            k,
            v.projected_drawdown_pct,
          ])
        )
      : undefined,
    portfolioLossDollars: portfolioStressResult?.crises_stress_results?.GFC_2008
      ?.projected_portfolio_loss_dollars,
  };

  return (
    <div className="space-y-6 max-w-7xl mx-auto pb-12">
      {/* 1. Command Header */}
      <ScenarioHeader
        targetType={params.targetType}
        ticker={params.ticker}
        mode={params.mode}
        lastRunTimestamp={lastRunTimestamp}
        isLoading={isLoading}
        onRun={runSimulation}
        onReset={resetParams}
      />

      {/* 2. Simulation Controls / Loading / Error Banner */}
      <SimulationControls
        isLoading={isLoading}
        loadingStage={loadingStage}
        error={error}
        onRetry={runSimulation}
      />

      {/* 3. Target & Mode Selector */}
      <ScenarioSelector
        targetType={params.targetType}
        mode={params.mode}
        ticker={params.ticker}
        onTargetTypeChange={(target) => updateParam("targetType", target)}
        onModeChange={(mode) => updateParam("mode", mode)}
        onTickerChange={(ticker) => updateParam("ticker", ticker)}
      />

      {/* 4. Scenario Parameters Configuration Panel */}
      <ScenarioConfiguration
        params={params}
        updateParam={updateParam}
        isLoading={isLoading}
      />

      {/* 5. Primary Mode Results */}
      <div className="space-y-6">
        {params.mode === "MONTE_CARLO" && (
          <>
            <ScenarioRiskMetrics
              mode="MONTE_CARLO"
              monteCarloData={monteCarloResult}
              macroShockData={null}
              isLoading={isLoading}
            />
            <MonteCarloSimulation data={monteCarloResult} isLoading={isLoading} />
            <ScenarioDistributionChart data={monteCarloResult} isLoading={isLoading} />
          </>
        )}

        {params.mode === "HISTORICAL_STRESS" && (
          <HistoricalStressTests data={historicalStressResult} isLoading={isLoading} />
        )}

        {params.mode === "MACRO_SHOCK" && (
          <ScenarioRiskMetrics
            mode="MACRO_SHOCK"
            monteCarloData={null}
            macroShockData={macroShockResult}
            isLoading={isLoading}
          />
        )}

        {params.mode === "PORTFOLIO_STRESS" && (
          <PortfolioStressResults data={portfolioStressResult} isLoading={isLoading} />
        )}
      </div>

      {/* 6. Multi-Scenario Comparison Matrix */}
      <ScenarioComparison
        historicalData={historicalStressResult}
        monteCarloData={monteCarloResult}
        macroData={macroShockResult}
      />

      {/* 7. AI Scenario Interpretation */}
      <AIScenarioInterpretation context={aiContext} />

      {/* 8. Methodology Assumptions & Limitations */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <ScenarioAssumptions mode={params.mode} />
        <ScenarioLimitations />
      </div>
    </div>
  );
}

export default function ScenariosPage() {
  return (
    <AppLayout>
      <ScenariosContent />
    </AppLayout>
  );
}


