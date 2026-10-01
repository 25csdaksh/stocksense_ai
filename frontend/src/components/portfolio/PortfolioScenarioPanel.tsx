"use client";

import React from "react";
import { PortfolioRiskContext } from "@/types/portfolio-copilot";
import { ShieldAlert, AlertTriangle, TrendingDown, Activity } from "lucide-react";
import { Badge } from "@/components/common/Badge";

interface PortfolioScenarioPanelProps {
  risk: PortfolioRiskContext;
}

export const PortfolioScenarioPanel: React.FC<PortfolioScenarioPanelProps> = ({ risk }) => {
  const scenarios = risk.stress_scenarios || {};
  const mc = risk.monte_carlo_summary || {};

  return (
    <div className="bg-surface border border-border rounded-2xl p-6 shadow-card space-y-6">
      <div className="flex items-center justify-between border-b border-border pb-4">
        <div className="flex items-center gap-2">
          <div className="p-2 rounded-xl bg-financial-loss/10 text-financial-loss border border-financial-loss/20">
            <TrendingDown className="w-5 h-5" />
          </div>
          <div>
            <h3 className="text-sm font-black text-content uppercase tracking-wider">
              Stress Scenarios & Stochastic Simulations
            </h3>
            <p className="text-xs text-content-muted">
              Historical crisis replays and 252-day forward Monte Carlo projections
            </p>
          </div>
        </div>

        <Badge variant="neutral" size="sm">
          MODEL_DERIVED
        </Badge>
      </div>

      {/* Historical Stress Scenarios */}
      <div className="space-y-3">
        <h4 className="text-xs font-bold text-content uppercase tracking-wider flex items-center gap-1.5">
          <ShieldAlert className="w-4 h-4 text-financial-warning" /> Historical Crisis Replays
        </h4>
        <div className="grid grid-cols-1 sm:grid-cols-3 gap-3 text-xs font-tabular">
          {Object.entries(scenarios).map(([key, sc]: [string, any]) => (
            <div
              key={key}
              className="p-3.5 bg-surface-subtle rounded-xl border border-border/70 space-y-1.5"
            >
              <div className="flex items-center justify-between">
                <span className="font-bold text-content truncate block max-w-[140px]">
                  {sc.name || key}
                </span>
                <span className="text-[9px] font-mono px-1.5 py-0.5 rounded bg-surface border border-border text-content-muted">
                  {sc.status || "HISTORICAL"}
                </span>
              </div>
              <p className="text-lg font-black text-financial-loss">
                {sc.projected_drawdown_pct}%
              </p>
              <span className="text-[10px] text-content-muted">
                Simulated Drawdown
              </span>
            </div>
          ))}
        </div>
      </div>

      {/* Monte Carlo Summary */}
      {mc.simulations_count && (
        <div className="p-4 rounded-xl bg-surface-subtle border border-border/70 space-y-2 text-xs">
          <div className="flex items-center justify-between">
            <span className="font-bold text-content flex items-center gap-1.5">
              <Activity className="w-4 h-4 text-primary" /> Monte Carlo Simulation Summary ({mc.simulations_count} Iterations)
            </span>
            <span className="text-[9px] font-mono px-2 py-0.5 rounded bg-surface border border-border text-primary font-bold">
              {mc.status || "MODEL_DERIVED"}
            </span>
          </div>
          <div className="grid grid-cols-2 sm:grid-cols-3 gap-3 font-tabular pt-1">
            <div>
              <span className="text-[10px] text-content-muted block">Median Simulated Return:</span>
              <span className="font-bold text-financial-gain">+{mc.median_return_pct}%</span>
            </div>
            {mc.confidence_interval_95 && (
              <div className="col-span-2">
                <span className="text-[10px] text-content-muted block">95% Confidence Return Interval:</span>
                <span className="font-bold text-content">
                  {mc.confidence_interval_95.lower_pnl_pct}% to +{mc.confidence_interval_95.upper_pnl_pct}%
                </span>
              </div>
            )}
          </div>
          <p className="text-[10px] text-content-muted italic pt-1 border-t border-border/40">
            Methodology: {mc.methodology || "Geometric Brownian Motion"}. Simulations are statistical models, not guaranteed predictions.
          </p>
        </div>
      )}
    </div>
  );
};
