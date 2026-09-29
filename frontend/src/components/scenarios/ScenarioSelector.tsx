"use client";

import React from "react";
import { ScenarioMode } from "@/types";
import { Activity, ShieldAlert, Sliders, Briefcase } from "lucide-react";

interface ScenarioSelectorProps {
  targetType: "STOCK" | "PORTFOLIO";
  mode: ScenarioMode;
  ticker: string;
  onTargetTypeChange: (target: "STOCK" | "PORTFOLIO") => void;
  onModeChange: (mode: ScenarioMode) => void;
  onTickerChange: (ticker: string) => void;
}

const STOCK_UNIVERSE = [
  { value: "RELIANCE.NS", label: "RELIANCE.NS — Reliance Industries (Energy/Retail)" },
  { value: "TCS.NS", label: "TCS.NS — Tata Consultancy Services (IT Services)" },
  { value: "INFY.NS", label: "INFY.NS — Infosys Ltd (IT Services)" },
  { value: "HDFCBANK.NS", label: "HDFCBANK.NS — HDFC Bank Ltd (Financials)" },
  { value: "ICICIBANK.NS", label: "ICICIBANK.NS — ICICI Bank Ltd (Financials)" },
  { value: "BHARTIARTL.NS", label: "BHARTIARTL.NS — Bharti Airtel (Telecom)" },
  { value: "ITC.NS", label: "ITC.NS — ITC Ltd (Consumer Goods)" },
  { value: "NVDA", label: "NVDA — NVIDIA Corporation (Global Tech / Semis)" },
];

export const ScenarioSelector: React.FC<ScenarioSelectorProps> = ({
  targetType,
  mode,
  ticker,
  onTargetTypeChange,
  onModeChange,
  onTickerChange,
}) => {
  return (
    <div className="bg-surface p-4 rounded-2xl border border-border shadow-card space-y-4">
      {/* Target Type Switcher */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 border-b border-border pb-3.5">
        <div className="flex items-center gap-2">
          <span className="text-xs font-bold text-content uppercase tracking-wider">Analysis Target:</span>
          <div className="inline-flex p-0.5 rounded-xl bg-surface-subtle border border-border">
            <button
              onClick={() => {
                onTargetTypeChange("STOCK");
                if (mode === "PORTFOLIO_STRESS") {
                  onModeChange("MONTE_CARLO");
                }
              }}
              className={`px-3 py-1 text-xs font-semibold rounded-lg transition-all ${
                targetType === "STOCK"
                  ? "bg-primary text-white shadow-sm"
                  : "text-content-muted hover:text-content"
              }`}
            >
              Single Equity
            </button>
            <button
              onClick={() => {
                onTargetTypeChange("PORTFOLIO");
                onModeChange("PORTFOLIO_STRESS");
              }}
              className={`px-3 py-1 text-xs font-semibold rounded-lg transition-all ${
                targetType === "PORTFOLIO"
                  ? "bg-primary text-white shadow-sm"
                  : "text-content-muted hover:text-content"
              }`}
            >
              Portfolio Holdings
            </button>
          </div>
        </div>

        {targetType === "STOCK" && (
          <div className="flex items-center gap-2">
            <span className="text-xs font-medium text-content-muted">Selected Ticker:</span>
            <select
              value={ticker}
              onChange={(e: React.ChangeEvent<HTMLSelectElement>) => onTickerChange(e.target.value)}
              className="bg-surface-subtle border border-border rounded-lg text-xs font-semibold text-content px-2.5 py-1.5 focus:outline-none focus:border-primary"
            >
              {STOCK_UNIVERSE.map((item) => (
                <option key={item.value} value={item.value}>
                  {item.label}
                </option>
              ))}
            </select>
          </div>
        )}
      </div>

      {/* Mode Selection Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-3">
        <button
          onClick={() => {
            onModeChange("MONTE_CARLO");
            onTargetTypeChange("STOCK");
          }}
          className={`text-left p-3.5 rounded-xl border transition-all ${
            mode === "MONTE_CARLO"
              ? "bg-primary/5 border-primary ring-1 ring-primary/30"
              : "bg-surface-subtle/50 border-border hover:border-primary/40"
          }`}
        >
          <div className="flex items-center gap-2 mb-1.5">
            <div className={`p-1.5 rounded-lg ${mode === "MONTE_CARLO" ? "bg-primary text-white" : "bg-surface text-content-muted"}`}>
              <Activity className="w-3.5 h-3.5" />
            </div>
            <span className="text-xs font-bold text-content">Monte Carlo Diffusion</span>
          </div>
          <p className="text-[11px] text-content-muted leading-relaxed">
            Merton Jump Diffusion with Poisson arrival jumps, VaR/CVaR, and fan chart quantile cones.
          </p>
        </button>

        <button
          onClick={() => {
            onModeChange("HISTORICAL_STRESS");
            onTargetTypeChange("STOCK");
          }}
          className={`text-left p-3.5 rounded-xl border transition-all ${
            mode === "HISTORICAL_STRESS"
              ? "bg-primary/5 border-primary ring-1 ring-primary/30"
              : "bg-surface-subtle/50 border-border hover:border-primary/40"
          }`}
        >
          <div className="flex items-center gap-2 mb-1.5">
            <div className={`p-1.5 rounded-lg ${mode === "HISTORICAL_STRESS" ? "bg-primary text-white" : "bg-surface text-content-muted"}`}>
              <ShieldAlert className="w-3.5 h-3.5" />
            </div>
            <span className="text-xs font-bold text-content">Historical Crisis Replay</span>
          </div>
          <p className="text-[11px] text-content-muted leading-relaxed">
            2008 GFC, 2020 COVID, 2022 Fed Rate Shock, and 2000 Dot-Com equity drawdown impact.
          </p>
        </button>

        <button
          onClick={() => {
            onModeChange("MACRO_SHOCK");
            onTargetTypeChange("STOCK");
          }}
          className={`text-left p-3.5 rounded-xl border transition-all ${
            mode === "MACRO_SHOCK"
              ? "bg-primary/5 border-primary ring-1 ring-primary/30"
              : "bg-surface-subtle/50 border-border hover:border-primary/40"
          }`}
        >
          <div className="flex items-center gap-2 mb-1.5">
            <div className={`p-1.5 rounded-lg ${mode === "MACRO_SHOCK" ? "bg-primary text-white" : "bg-surface text-content-muted"}`}>
              <Sliders className="w-3.5 h-3.5" />
            </div>
            <span className="text-xs font-bold text-content">Macro Sensitivity Shock</span>
          </div>
          <p className="text-[11px] text-content-muted leading-relaxed">
            Factor sensitivities across interest rates (bps), inflation (CPI %), crude oil (%), and GDP.
          </p>
        </button>

        <button
          onClick={() => {
            onModeChange("PORTFOLIO_STRESS");
            onTargetTypeChange("PORTFOLIO");
          }}
          className={`text-left p-3.5 rounded-xl border transition-all ${
            mode === "PORTFOLIO_STRESS"
              ? "bg-primary/5 border-primary ring-1 ring-primary/30"
              : "bg-surface-subtle/50 border-border hover:border-primary/40"
          }`}
        >
          <div className="flex items-center gap-2 mb-1.5">
            <div className={`p-1.5 rounded-lg ${mode === "PORTFOLIO_STRESS" ? "bg-primary text-white" : "bg-surface text-content-muted"}`}>
              <Briefcase className="w-3.5 h-3.5" />
            </div>
            <span className="text-xs font-bold text-content">Portfolio Stress Test</span>
          </div>
          <p className="text-[11px] text-content-muted leading-relaxed">
            Multi-crisis portfolio stress testing across current positions and sector weights.
          </p>
        </button>
      </div>
    </div>
  );
};
