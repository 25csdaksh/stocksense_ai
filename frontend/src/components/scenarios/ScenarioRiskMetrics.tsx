"use client";

import React from "react";
import { MonteCarloResponse, MacroShockResponse, ScenarioMode } from "@/types";
import { formatCurrency } from "@/lib/utils";
import { AlertTriangle, Activity, Sliders, ShieldAlert, Percent } from "lucide-react";
import { Badge } from "@/components/common/Badge";

interface ScenarioRiskMetricsProps {
  mode: ScenarioMode;
  monteCarloData: MonteCarloResponse | null;
  macroShockData: MacroShockResponse | null;
  isLoading: boolean;
}

export const ScenarioRiskMetrics: React.FC<ScenarioRiskMetricsProps> = ({
  mode,
  monteCarloData,
  macroShockData,
  isLoading,
}) => {
  if (isLoading) {
    return (
      <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
        {[1, 2, 3].map((i) => (
          <div key={i} className="bg-surface p-4 rounded-xl border border-border animate-pulse h-24" />
        ))}
      </div>
    );
  }

  if (mode === "MONTE_CARLO" && monteCarloData) {
    return (
      <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
        <div className="bg-surface p-4 rounded-2xl border border-border shadow-card space-y-1">
          <div className="flex items-center justify-between">
            <span className="text-xs font-semibold text-content-muted uppercase">95% Value-at-Risk (VaR)</span>
            <AlertTriangle className="w-4 h-4 text-financial-loss" />
          </div>
          <p className="text-xl font-bold text-financial-loss font-tabular">
            {monteCarloData.value_at_risk_95_pct.toFixed(2)}%
          </p>
          <p className="text-[11px] text-content-muted">
            95% probability that terminal loss does not exceed this threshold over {monteCarloData.days} days.
          </p>
        </div>

        <div className="bg-surface p-4 rounded-2xl border border-border shadow-card space-y-1">
          <div className="flex items-center justify-between">
            <span className="text-xs font-semibold text-content-muted uppercase">99% CVaR / Expected Shortfall</span>
            <ShieldAlert className="w-4 h-4 text-financial-loss" />
          </div>
          <p className="text-xl font-bold text-financial-loss font-tabular">
            {monteCarloData.cvar_expected_shortfall_99_pct.toFixed(2)}%
          </p>
          <p className="text-[11px] text-content-muted">
            Average expected loss in the worst 1% tail event distribution.
          </p>
        </div>

        <div className="bg-surface p-4 rounded-2xl border border-border shadow-card space-y-1">
          <div className="flex items-center justify-between">
            <span className="text-xs font-semibold text-content-muted uppercase">Annualized Volatility (σ)</span>
            <Activity className="w-4 h-4 text-primary" />
          </div>
          <p className="text-xl font-bold text-content font-tabular">
            {monteCarloData.annualized_volatility_pct.toFixed(1)}%
          </p>
          <p className="text-[11px] text-content-muted">
            Continuous Brownian motion diffusion standard deviation.
          </p>
        </div>
      </div>
    );
  }

  if (mode === "MACRO_SHOCK" && macroShockData) {
    const isGain = macroShockData.total_projected_return_pct >= 0;

    return (
      <div className="bg-surface p-5 rounded-2xl border border-border shadow-card space-y-4">
        <div className="flex items-center justify-between border-b border-border pb-3">
          <div className="flex items-center gap-2">
            <Sliders className="w-4 h-4 text-primary" />
            <h3 className="text-sm font-bold text-content uppercase tracking-wider">
              Macroeconomic Factor Decomposition
            </h3>
          </div>
          <Badge variant={isGain ? "gain" : "loss"} size="sm">
            Total Impact: {isGain ? `+${macroShockData.total_projected_return_pct}%` : `${macroShockData.total_projected_return_pct}%`}
          </Badge>
        </div>

        <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
          <div className="p-3 bg-surface-subtle/70 rounded-xl border border-border">
            <span className="text-[10px] text-content-muted uppercase font-semibold">Interest Rates Effect</span>
            <p className="text-sm font-bold text-content font-tabular mt-0.5">
              {macroShockData.factor_decomposition.rates_effect_pct > 0 ? `+` : ``}
              {macroShockData.factor_decomposition.rates_effect_pct.toFixed(2)}%
            </p>
          </div>

          <div className="p-3 bg-surface-subtle/70 rounded-xl border border-border">
            <span className="text-[10px] text-content-muted uppercase font-semibold">Inflation Effect</span>
            <p className="text-sm font-bold text-content font-tabular mt-0.5">
              {macroShockData.factor_decomposition.inflation_effect_pct > 0 ? `+` : ``}
              {macroShockData.factor_decomposition.inflation_effect_pct.toFixed(2)}%
            </p>
          </div>

          <div className="p-3 bg-surface-subtle/70 rounded-xl border border-border">
            <span className="text-[10px] text-content-muted uppercase font-semibold">Crude Oil Effect</span>
            <p className="text-sm font-bold text-content font-tabular mt-0.5">
              {macroShockData.factor_decomposition.oil_effect_pct > 0 ? `+` : ``}
              {macroShockData.factor_decomposition.oil_effect_pct.toFixed(2)}%
            </p>
          </div>

          <div className="p-3 bg-surface-subtle/70 rounded-xl border border-border">
            <span className="text-[10px] text-content-muted uppercase font-semibold">Real GDP Effect</span>
            <p className="text-sm font-bold text-content font-tabular mt-0.5">
              {macroShockData.factor_decomposition.gdp_effect_pct > 0 ? `+` : ``}
              {macroShockData.factor_decomposition.gdp_effect_pct.toFixed(2)}%
            </p>
          </div>
        </div>

        <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 pt-2">
          <div className="p-3 bg-surface-subtle rounded-xl border border-border flex items-center justify-between">
            <span className="text-xs font-semibold text-content">Projected Stressed Price:</span>
            <span className="text-sm font-bold text-content font-tabular">
              {formatCurrency(macroShockData.projected_price, "INR")}
            </span>
          </div>

          <div className="p-3 bg-surface-subtle rounded-xl border border-border flex items-center justify-between">
            <span className="text-xs font-semibold text-content">Projected Dollar Impact:</span>
            <span className={`text-sm font-bold font-tabular ${macroShockData.dollar_impact_per_share >= 0 ? "text-financial-gain" : "text-financial-loss"}`}>
              {macroShockData.dollar_impact_per_share >= 0 ? `+` : ``}
              {formatCurrency(macroShockData.dollar_impact_per_share, "INR")} / share
            </span>
          </div>
        </div>
      </div>
    );
  }

  return null;
};
