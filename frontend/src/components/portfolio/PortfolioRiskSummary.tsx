"use client";

import React from "react";
import { PortfolioRiskContext } from "@/types/portfolio-copilot";
import { ShieldAlert, Activity, BarChart2, Layers, AlertCircle } from "lucide-react";

interface PortfolioRiskSummaryProps {
  risk: PortfolioRiskContext;
}

export const PortfolioRiskSummary: React.FC<PortfolioRiskSummaryProps> = ({ risk }) => {
  return (
    <div className="bg-surface border border-border rounded-2xl p-6 shadow-card space-y-6">
      <div className="flex items-center justify-between border-b border-border pb-4">
        <div className="flex items-center gap-2">
          <div className="p-2 rounded-xl bg-financial-warning/10 text-financial-warning border border-financial-warning/20">
            <ShieldAlert className="w-5 h-5" />
          </div>
          <div>
            <h3 className="text-sm font-black text-content uppercase tracking-wider">
              Portfolio Downside & Factor Exposures
            </h3>
            <p className="text-xs text-content-muted">
              Parametric Value at Risk and historical crisis sensitivity
            </p>
          </div>
        </div>
        <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-surface-subtle border border-border text-content-muted">
          PROVENANCE: {risk.provenance}
        </span>
      </div>

      {/* Metrics Row */}
      <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 font-tabular text-xs">
        <div className="p-3 bg-surface-subtle rounded-xl border border-border/60 space-y-1">
          <span className="text-[10px] uppercase font-bold text-content-muted">Weighted Beta</span>
          <p className="text-base font-black text-content">{risk.weighted_beta}</p>
          <span className="text-[10px] text-content-muted">vs Benchmark Index</span>
        </div>

        <div className="p-3 bg-surface-subtle rounded-xl border border-border/60 space-y-1">
          <span className="text-[10px] uppercase font-bold text-content-muted">30d Volatility</span>
          <p className="text-base font-black text-content">{risk.portfolio_volatility_pct}%</p>
          <span className="text-[10px] text-content-muted">Downside Dev: {risk.downside_deviation_pct}%</span>
        </div>

        <div className="p-3 bg-surface-subtle rounded-xl border border-border/60 space-y-1">
          <span className="text-[10px] uppercase font-bold text-content-muted">1-Day 95% VaR</span>
          <p className="text-base font-black text-content">{risk.var_95_daily_pct}%</p>
          <span className="text-[10px] text-content-muted">Max DD: {risk.max_drawdown_pct}%</span>
        </div>

        <div className="p-3 bg-surface-subtle rounded-xl border border-border/60 space-y-1">
          <span className="text-[10px] uppercase font-bold text-content-muted">Sharpe / Sortino</span>
          <p className="text-base font-black text-content">{risk.sharpe_ratio} / {risk.sortino_ratio}</p>
          <span className="text-[10px] text-content-muted">Risk-Adjusted Ratios</span>
        </div>
      </div>

      {/* Correlation Clusters */}
      {risk.correlation_clusters && risk.correlation_clusters.length > 0 && (
        <div className="space-y-2">
          <h4 className="text-xs font-bold text-content flex items-center gap-1.5">
            <Layers className="w-4 h-4 text-primary" /> Sector Correlation Clusters
          </h4>
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-2 text-xs">
            {risk.correlation_clusters.map((c, i) => (
              <div key={i} className="p-3 bg-surface-subtle rounded-xl border border-border/60 space-y-1">
                <div className="flex items-center justify-between font-bold text-content">
                  <span>{c.cluster_name}</span>
                  <span className="text-[10px] font-mono text-primary">{c.aggregate_weight_pct}% Weight</span>
                </div>
                <p className="text-[10px] text-content-muted font-mono">
                  Symbols: {c.symbols.join(", ")}
                </p>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
};
