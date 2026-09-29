"use client";

import React from "react";
import { ScenarioMode } from "@/types";
import { Sliders, HelpCircle, CheckCircle2 } from "lucide-react";

interface ScenarioAssumptionsProps {
  mode: ScenarioMode;
}

export const ScenarioAssumptions: React.FC<ScenarioAssumptionsProps> = ({ mode }) => {
  return (
    <div className="bg-surface p-5 rounded-2xl border border-border shadow-card space-y-3">
      <div className="flex items-center justify-between border-b border-border pb-2.5">
        <div className="flex items-center gap-2">
          <Sliders className="w-4 h-4 text-primary" />
          <h4 className="text-xs font-bold text-content uppercase tracking-wider">
            Model Parameters & Econometric Assumptions
          </h4>
        </div>
        <span className="text-[10px] text-content-muted">Transparent Methodology</span>
      </div>

      <div className="space-y-2 text-[11px] text-content-muted leading-relaxed">
        {mode === "MONTE_CARLO" && (
          <>
            <div className="flex items-start gap-2">
              <CheckCircle2 className="w-3.5 h-3.5 text-primary shrink-0 mt-0.5" />
              <span>
                <strong>Stochastic Diffusion:</strong> Geometric Brownian Motion with Merton (1976) compound Poisson jump process.
              </span>
            </div>
            <div className="flex items-start gap-2">
              <CheckCircle2 className="w-3.5 h-3.5 text-primary shrink-0 mt-0.5" />
              <span>
                <strong>Time Discretization:</strong> Daily increments (dt = 1/252 trading days) over simulated horizon.
              </span>
            </div>
            <div className="flex items-start gap-2">
              <CheckCircle2 className="w-3.5 h-3.5 text-primary shrink-0 mt-0.5" />
              <span>
                <strong>Jump Distribution:</strong> Log-normal jump magnitude ~ N(-5%, 15%) calibrated to historical sudden shocks.
              </span>
            </div>
          </>
        )}

        {mode === "HISTORICAL_STRESS" && (
          <>
            <div className="flex items-start gap-2">
              <CheckCircle2 className="w-3.5 h-3.5 text-primary shrink-0 mt-0.5" />
              <span>
                <strong>Crisis Calibration:</strong> Uses peak-to-trough historical drawdowns from actual market regimes.
              </span>
            </div>
            <div className="flex items-start gap-2">
              <CheckCircle2 className="w-3.5 h-3.5 text-primary shrink-0 mt-0.5" />
              <span>
                <strong>Beta Scaling:</strong> Individual asset drawdown is scaled as: <code>Sector_Drop × [1 + (β - 1) × 0.4]</code>.
              </span>
            </div>
          </>
        )}

        {mode === "MACRO_SHOCK" && (
          <>
            <div className="flex items-start gap-2">
              <CheckCircle2 className="w-3.5 h-3.5 text-primary shrink-0 mt-0.5" />
              <span>
                <strong>Sector Elasticities:</strong> Empirically calibrated factor sensitivities for Rates, CPI Inflation, Brent Oil, and Real GDP.
              </span>
            </div>
            <div className="flex items-start gap-2">
              <CheckCircle2 className="w-3.5 h-3.5 text-primary shrink-0 mt-0.5" />
              <span>
                <strong>Decomposition:</strong> Total projected impact is a linear combination of factor elasticity multiplied by beta adjustment.
              </span>
            </div>
          </>
        )}

        {mode === "PORTFOLIO_STRESS" && (
          <>
            <div className="flex items-start gap-2">
              <CheckCircle2 className="w-3.5 h-3.5 text-primary shrink-0 mt-0.5" />
              <span>
                <strong>Constituent Attribution:</strong> Simulates each individual portfolio holding under historical crises and aggregates total drawdown.
              </span>
            </div>
          </>
        )}
      </div>
    </div>
  );
};
