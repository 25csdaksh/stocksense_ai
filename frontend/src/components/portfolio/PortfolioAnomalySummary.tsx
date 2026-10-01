"use client";

import React from "react";
import { PortfolioAnomalyContext } from "@/types/portfolio-copilot";
import { Zap, AlertTriangle, CheckCircle } from "lucide-react";

interface PortfolioAnomalySummaryProps {
  anomaly: PortfolioAnomalyContext;
}

export const PortfolioAnomalySummary: React.FC<PortfolioAnomalySummaryProps> = ({ anomaly }) => {
  const hasAnomalies = anomaly.total_anomalies > 0;

  return (
    <div className="bg-surface border border-border rounded-2xl p-6 shadow-card space-y-5">
      <div className="flex items-center justify-between border-b border-border pb-4">
        <div className="flex items-center gap-2">
          <div className="p-2 rounded-xl bg-financial-warning/10 text-financial-warning border border-financial-warning/20">
            <Zap className="w-5 h-5" />
          </div>
          <div>
            <h3 className="text-sm font-black text-content uppercase tracking-wider">
              Statistical Anomaly Surveillance
            </h3>
            <p className="text-xs text-content-muted">
              Outlier return dispersion, volatility jumps, and volume surges
            </p>
          </div>
        </div>

        <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-surface-subtle border border-border text-content-muted">
          STATUS: {hasAnomalies ? `${anomaly.total_anomalies} DETECTED` : "NORMAL"}
        </span>
      </div>

      <div className="p-3.5 bg-surface-subtle rounded-xl border border-border/60 text-xs text-content space-y-2">
        <div className="flex items-start gap-2">
          {hasAnomalies ? (
            <AlertTriangle className="w-4 h-4 text-financial-warning flex-shrink-0 mt-0.5" />
          ) : (
            <CheckCircle className="w-4 h-4 text-financial-gain flex-shrink-0 mt-0.5" />
          )}
          <p className="leading-relaxed">{anomaly.associative_summary}</p>
        </div>
      </div>

      {hasAnomalies && (
        <div className="space-y-2 pt-2">
          <span className="text-[10px] font-bold uppercase text-content-muted tracking-wider">
            Flagged Tickers
          </span>
          <div className="flex flex-wrap gap-2">
            {Object.keys(anomaly.holding_anomalies_map).map((sym, i) => (
              <span
                key={i}
                className="px-2.5 py-1 rounded-lg bg-surface border border-financial-warning/40 text-xs font-mono font-bold text-content flex items-center gap-1"
              >
                <Zap className="w-3 h-3 text-financial-warning" />
                {sym}
              </span>
            ))}
          </div>
        </div>
      )}
    </div>
  );
};
