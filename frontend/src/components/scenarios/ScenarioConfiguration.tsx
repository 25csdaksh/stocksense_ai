"use client";

import React from "react";
import { ScenarioSimulationParams } from "@/hooks/useScenarioSimulation";
import { Sliders, ShieldAlert, Activity, DollarSign } from "lucide-react";

interface ScenarioConfigurationProps {
  params: ScenarioSimulationParams;
  updateParam: <K extends keyof ScenarioSimulationParams>(key: K, value: ScenarioSimulationParams[K]) => void;
  isLoading: boolean;
}

const SECTOR_OPTIONS = [
  "Information Technology",
  "Financials",
  "Energy",
  "Consumer Discretionary",
  "Health Care",
  "Index ETF",
];

export const ScenarioConfiguration: React.FC<ScenarioConfigurationProps> = ({
  params,
  updateParam,
  isLoading,
}) => {
  return (
    <div className="bg-surface p-5 rounded-2xl border border-border shadow-card space-y-4">
      <div className="flex items-center justify-between border-b border-border pb-3">
        <div className="flex items-center gap-2">
          <Sliders className="w-4 h-4 text-primary" />
          <h3 className="text-sm font-bold text-content uppercase tracking-wider">
            {params.mode === "MONTE_CARLO" && "Merton Jump Diffusion Parameters"}
            {params.mode === "HISTORICAL_STRESS" && "Historical Stress Model Assumptions"}
            {params.mode === "MACRO_SHOCK" && "Macroeconomic Elasticity Factors"}
            {params.mode === "PORTFOLIO_STRESS" && "Portfolio Stress Engine Settings"}
          </h3>
        </div>
        <span className="text-[11px] text-content-muted font-medium">Validated Mathematical Bounds</span>
      </div>

      {params.mode === "MONTE_CARLO" && (
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-5 gap-4">
          <div>
            <label className="block text-xs font-semibold text-content mb-1">
              Annualized Drift (μ): {(params.driftAnnualized * 100).toFixed(1)}%
            </label>
            <input
              type="range"
              min="-0.30"
              max="0.40"
              step="0.01"
              value={params.driftAnnualized}
              onChange={(e: React.ChangeEvent<HTMLInputElement>) => updateParam("driftAnnualized", parseFloat(e.target.value))}
              disabled={isLoading}
              className="w-full accent-primary h-1.5 bg-surface-subtle rounded-lg cursor-pointer"
            />
            <span className="text-[10px] text-content-muted">Base expected annual growth</span>
          </div>

          <div>
            <label className="block text-xs font-semibold text-content mb-1">
              Annual Volatility (σ): {(params.volatilityAnnualized * 100).toFixed(1)}%
            </label>
            <input
              type="range"
              min="0.05"
              max="0.80"
              step="0.01"
              value={params.volatilityAnnualized}
              onChange={(e: React.ChangeEvent<HTMLInputElement>) => updateParam("volatilityAnnualized", parseFloat(e.target.value))}
              disabled={isLoading}
              className="w-full accent-primary h-1.5 bg-surface-subtle rounded-lg cursor-pointer"
            />
            <span className="text-[10px] text-content-muted">Continuous Wiener volatility</span>
          </div>

          <div>
            <label className="block text-xs font-semibold text-content mb-1">
              Time Horizon: {params.days} Days
            </label>
            <input
              type="range"
              min="5"
              max="365"
              step="5"
              value={params.days}
              onChange={(e: React.ChangeEvent<HTMLInputElement>) => updateParam("days", parseInt(e.target.value, 10))}
              disabled={isLoading}
              className="w-full accent-primary h-1.5 bg-surface-subtle rounded-lg cursor-pointer"
            />
            <span className="text-[10px] text-content-muted">Trading days simulated (dt = 1/252)</span>
          </div>

          <div>
            <label className="block text-xs font-semibold text-content mb-1">
              Monte Carlo Paths: {params.iterations.toLocaleString()}
            </label>
            <select
              value={params.iterations}
              onChange={(e: React.ChangeEvent<HTMLSelectElement>) => updateParam("iterations", parseInt(e.target.value, 10))}
              disabled={isLoading}
              className="w-full bg-surface-subtle border border-border rounded-lg text-xs font-semibold text-content p-2 focus:outline-none focus:border-primary"
            >
              <option value={1000}>1,000 Paths (Fast)</option>
              <option value={5000}>5,000 Paths (Standard)</option>
              <option value={10000}>10,000 Paths (Institutional)</option>
            </select>
            <span className="text-[10px] text-content-muted">Independent stochastic paths</span>
          </div>

          <div>
            <label className="block text-xs font-semibold text-content mb-1">
              Jump Intensity (λ): {params.jumpIntensity.toFixed(2)}
            </label>
            <input
              type="range"
              min="0.00"
              max="0.30"
              step="0.01"
              value={params.jumpIntensity}
              onChange={(e: React.ChangeEvent<HTMLInputElement>) => updateParam("jumpIntensity", parseFloat(e.target.value))}
              disabled={isLoading}
              className="w-full accent-primary h-1.5 bg-surface-subtle rounded-lg cursor-pointer"
            />
            <span className="text-[10px] text-content-muted">Poisson discrete shock arrival rate</span>
          </div>
        </div>
      )}

      {params.mode === "HISTORICAL_STRESS" && (
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
          <div>
            <label className="block text-xs font-semibold text-content mb-1">Sector Classification</label>
            <select
              value={params.sector}
              onChange={(e: React.ChangeEvent<HTMLSelectElement>) => updateParam("sector", e.target.value)}
              disabled={isLoading}
              className="w-full bg-surface-subtle border border-border rounded-lg text-xs font-semibold text-content p-2 focus:outline-none focus:border-primary"
            >
              {SECTOR_OPTIONS.map((sec) => (
                <option key={sec} value={sec}>
                  {sec}
                </option>
              ))}
            </select>
            <span className="text-[10px] text-content-muted">Applies historical sector shock multiplier</span>
          </div>

          <div>
            <label className="block text-xs font-semibold text-content mb-1">
              Systematic Beta (β): {params.beta.toFixed(2)}
            </label>
            <input
              type="range"
              min="0.40"
              max="2.50"
              step="0.05"
              value={params.beta}
              onChange={(e: React.ChangeEvent<HTMLInputElement>) => updateParam("beta", parseFloat(e.target.value))}
              disabled={isLoading}
              className="w-full accent-primary h-1.5 bg-surface-subtle rounded-lg cursor-pointer"
            />
            <span className="text-[10px] text-content-muted">Drawdown scaling vs broad benchmark index</span>
          </div>
        </div>
      )}

      {params.mode === "MACRO_SHOCK" && (
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
          <div>
            <label className="block text-xs font-semibold text-content mb-1">
              Interest Rate Shock: {params.rateShockBps > 0 ? `+${params.rateShockBps}` : params.rateShockBps} bps
            </label>
            <input
              type="range"
              min="-200"
              max="400"
              step="25"
              value={params.rateShockBps}
              onChange={(e: React.ChangeEvent<HTMLInputElement>) => updateParam("rateShockBps", parseFloat(e.target.value))}
              disabled={isLoading}
              className="w-full accent-primary h-1.5 bg-surface-subtle rounded-lg cursor-pointer"
            />
            <span className="text-[10px] text-content-muted">Central bank policy rate change in basis points</span>
          </div>

          <div>
            <label className="block text-xs font-semibold text-content mb-1">
              CPI Inflation Shock: {params.inflationShockPct > 0 ? `+${params.inflationShockPct}` : params.inflationShockPct}%
            </label>
            <input
              type="range"
              min="-3.0"
              max="6.0"
              step="0.5"
              value={params.inflationShockPct}
              onChange={(e: React.ChangeEvent<HTMLInputElement>) => updateParam("inflationShockPct", parseFloat(e.target.value))}
              disabled={isLoading}
              className="w-full accent-primary h-1.5 bg-surface-subtle rounded-lg cursor-pointer"
            />
            <span className="text-[10px] text-content-muted">Unexpected headline inflation shift</span>
          </div>

          <div>
            <label className="block text-xs font-semibold text-content mb-1">
              Crude Oil Shock: {params.oilShockPct > 0 ? `+${params.oilShockPct}` : params.oilShockPct}%
            </label>
            <input
              type="range"
              min="-40"
              max="80"
              step="5"
              value={params.oilShockPct}
              onChange={(e: React.ChangeEvent<HTMLInputElement>) => updateParam("oilShockPct", parseFloat(e.target.value))}
              disabled={isLoading}
              className="w-full accent-primary h-1.5 bg-surface-subtle rounded-lg cursor-pointer"
            />
            <span className="text-[10px] text-content-muted">Brent crude spot price shift</span>
          </div>

          <div>
            <label className="block text-xs font-semibold text-content mb-1">
              Real GDP Shock: {params.gdpShockPct > 0 ? `+${params.gdpShockPct}` : params.gdpShockPct}%
            </label>
            <input
              type="range"
              min="-5.0"
              max="3.0"
              step="0.5"
              value={params.gdpShockPct}
              onChange={(e: React.ChangeEvent<HTMLInputElement>) => updateParam("gdpShockPct", parseFloat(e.target.value))}
              disabled={isLoading}
              className="w-full accent-primary h-1.5 bg-surface-subtle rounded-lg cursor-pointer"
            />
            <span className="text-[10px] text-content-muted">Real GDP annualized growth deviation</span>
          </div>
        </div>
      )}

      {params.mode === "PORTFOLIO_STRESS" && (
        <div className="bg-surface-subtle p-3.5 rounded-xl border border-border flex items-center justify-between">
          <div>
            <p className="text-xs font-semibold text-content">Active Portfolio Holdings Connected</p>
            <p className="text-[11px] text-content-muted">
              Simulating crisis drawdowns across all current positions with constituent-weighted sector betas.
            </p>
          </div>
          <span className="text-xs font-bold text-primary px-3 py-1 bg-primary/10 rounded-lg">
            Auto-Enriched
          </span>
        </div>
      )}
    </div>
  );
};
