"use client";

import React from "react";
import { Badge } from "@/components/common/Badge";
import { Button } from "@/components/common/Button";
import { Activity, Play, RotateCcw, ShieldAlert, Sparkles, Clock } from "lucide-react";
import { ScenarioMode } from "@/types";

interface ScenarioHeaderProps {
  targetType: "STOCK" | "PORTFOLIO";
  ticker: string;
  mode: ScenarioMode;
  lastRunTimestamp: string | null;
  isLoading: boolean;
  onRun: () => void;
  onReset: () => void;
}

export const ScenarioHeader: React.FC<ScenarioHeaderProps> = ({
  targetType,
  ticker,
  mode,
  lastRunTimestamp,
  isLoading,
  onRun,
  onReset,
}) => {
  const getModeLabel = (m: ScenarioMode) => {
    switch (m) {
      case "MONTE_CARLO":
        return "Merton Jump Diffusion (5,000 Paths)";
      case "HISTORICAL_STRESS":
        return "Crisis Drawdown Replay (GFC, COVID, Fed)";
      case "MACRO_SHOCK":
        return "Macro Sensitivity Elasticity (Rates, Oil, GDP)";
      case "PORTFOLIO_STRESS":
        return "Multi-Asset Portfolio Stress";
    }
  };

  return (
    <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 bg-surface p-5 rounded-2xl border border-border shadow-card">
      <div className="space-y-1.5">
        <div className="flex flex-wrap items-center gap-2.5">
          <div className="w-8 h-8 rounded-xl bg-primary/10 flex items-center justify-center text-primary">
            <Activity className="w-4 h-4" />
          </div>
          <h1 className="text-xl sm:text-2xl font-bold tracking-tight text-content">
            SCENARIO & STRESS TEST LAB
          </h1>
          <Badge variant="primary" size="sm">
            {targetType === "PORTFOLIO" ? "Portfolio Target" : `Asset: ${ticker}`}
          </Badge>
          <Badge variant="gold" size="sm">
            {getModeLabel(mode)}
          </Badge>
          <Badge variant="neutral" size="sm">
            DEMO / BACKTEST DATA
          </Badge>
        </div>

        <p className="text-xs text-content-muted max-w-3xl leading-relaxed">
          Quantitative multi-path Monte Carlo jump diffusion, historical macroeconomic crisis replay,
          and multi-variable elasticity stress testing. Analytical simulation output — not guaranteed financial prediction.
        </p>

        {lastRunTimestamp && (
          <div className="flex items-center gap-1.5 text-[11px] text-content-muted font-tabular pt-0.5">
            <Clock className="w-3.5 h-3.5 text-primary" />
            <span>Last Simulated: {new Date(lastRunTimestamp).toLocaleTimeString()}</span>
          </div>
        )}
      </div>

      <div className="flex items-center gap-2.5 shrink-0">
        <Button
          variant="outline"
          size="sm"
          onClick={onReset}
          disabled={isLoading}
          leftIcon={<RotateCcw className="w-3.5 h-3.5" />}
        >
          Reset
        </Button>
        <Button
          variant="gold"
          size="md"
          onClick={onRun}
          isLoading={isLoading}
          leftIcon={<Play className="w-4 h-4 fill-current" />}
        >
          {isLoading ? "Simulating..." : "Run Scenario"}
        </Button>
      </div>
    </div>
  );
};
