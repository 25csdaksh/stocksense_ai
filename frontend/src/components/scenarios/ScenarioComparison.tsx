"use client";

import React from "react";
import { HistoricalStressResponse, MonteCarloResponse, MacroShockResponse } from "@/types";
import { formatCurrency } from "@/lib/utils";
import { Layers, TrendingDown, ArrowRight } from "lucide-react";
import { Badge } from "@/components/common/Badge";

interface ScenarioComparisonProps {
  historicalData: HistoricalStressResponse | null;
  monteCarloData: MonteCarloResponse | null;
  macroData: MacroShockResponse | null;
}

export const ScenarioComparison: React.FC<ScenarioComparisonProps> = ({
  historicalData,
  monteCarloData,
  macroData,
}) => {
  const comparisonItems: Array<{
    name: string;
    type: "Historical" | "Stochastic" | "Elasticity";
    drawdownPct: number;
    description: string;
  }> = [];

  if (historicalData?.scenario_results) {
    Object.values(historicalData.scenario_results).forEach((scen) => {
      comparisonItems.push({
        name: scen.scenario_name,
        type: "Historical",
        drawdownPct: scen.projected_drawdown_pct,
        description: scen.period,
      });
    });
  }

  if (monteCarloData) {
    const p10Return = ((monteCarloData.terminal_p10_price - monteCarloData.initial_price) / monteCarloData.initial_price) * 100;
    comparisonItems.push({
      name: "Merton P10 Downside (90-Day)",
      type: "Stochastic",
      drawdownPct: p10Return,
      description: "10th percentile lowest path",
    });
  }

  if (macroData) {
    comparisonItems.push({
      name: "Macro Factor Shock Model",
      type: "Elasticity",
      drawdownPct: macroData.total_projected_return_pct,
      description: "Rates, CPI, Oil, GDP multi-shock",
    });
  }

  if (comparisonItems.length === 0) {
    return null;
  }

  return (
    <div className="bg-surface p-5 rounded-2xl border border-border shadow-card space-y-4">
      <div className="flex items-center justify-between border-b border-border pb-3">
        <div className="flex items-center gap-2">
          <Layers className="w-4 h-4 text-primary" />
          <h3 className="text-sm font-bold text-content uppercase tracking-wider">
            Multi-Scenario Comparative Stress Matrix
          </h3>
        </div>
        <span className="text-[11px] text-content-muted">Relative Drawdown Sensitivity</span>
      </div>

      <div className="space-y-2.5">
        {comparisonItems.map((item, idx) => {
          const isLoss = item.drawdownPct < 0;
          const absVal = Math.min(100, Math.abs(item.drawdownPct));

          return (
            <div
              key={idx}
              className="p-3 bg-surface-subtle/50 rounded-xl border border-border flex flex-col sm:flex-row sm:items-center justify-between gap-3"
            >
              <div className="space-y-0.5 sm:w-1/3">
                <div className="flex items-center gap-2">
                  <span className="text-xs font-bold text-content">{item.name}</span>
                  <Badge variant={item.type === "Historical" ? "outline" : item.type === "Stochastic" ? "gold" : "primary"} size="sm">
                    {item.type}
                  </Badge>
                </div>
                <p className="text-[10px] text-content-muted">{item.description}</p>
              </div>

              {/* Bar visualization */}
              <div className="flex-1 max-w-md hidden sm:block">
                <div className="w-full bg-border/60 h-2 rounded-full overflow-hidden flex">
                  <div
                    className={`h-full rounded-full transition-all ${
                      isLoss ? "bg-financial-loss" : "bg-financial-gain"
                    }`}
                    style={{ width: `${absVal}%` }}
                  />
                </div>
              </div>

              <div className="text-right shrink-0">
                <span className={`text-xs font-bold font-tabular ${isLoss ? "text-financial-loss" : "text-financial-gain"}`}>
                  {item.drawdownPct > 0 ? `+` : ``}
                  {item.drawdownPct.toFixed(1)}%
                </span>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
};
