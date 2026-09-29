"use client";

import React from "react";
import { HistoricalStressResponse } from "@/types";
import { formatCurrency } from "@/lib/utils";
import { ShieldAlert, TrendingDown, Clock, Info } from "lucide-react";
import { Badge } from "@/components/common/Badge";

interface HistoricalStressTestsProps {
  data: HistoricalStressResponse | null;
  isLoading: boolean;
}

export const HistoricalStressTests: React.FC<HistoricalStressTestsProps> = ({
  data,
  isLoading,
}) => {
  if (isLoading) {
    return (
      <div className="bg-surface p-6 rounded-2xl border border-border shadow-card h-80 flex flex-col items-center justify-center space-y-3">
        <div className="w-8 h-8 border-2 border-primary border-t-transparent rounded-full animate-spin" />
        <p className="text-xs text-content-muted">Evaluating historical crisis drawdowns...</p>
      </div>
    );
  }

  if (!data || !data.scenario_results) {
    return (
      <div className="bg-surface p-6 rounded-2xl border border-border shadow-card h-80 flex items-center justify-center text-xs text-content-muted">
        No historical stress test results available. Click "Run Scenario" to simulate.
      </div>
    );
  }

  const resultsList = Object.entries(data.scenario_results);

  return (
    <div className="bg-surface p-5 rounded-2xl border border-border shadow-card space-y-4">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2 border-b border-border pb-3">
        <div>
          <div className="flex items-center gap-2">
            <ShieldAlert className="w-4 h-4 text-financial-loss" />
            <h3 className="text-sm font-bold text-content uppercase tracking-wider">
              Historical Crisis Replay Stress Test
            </h3>
          </div>
          <p className="text-[11px] text-content-muted mt-0.5">
            Asset: <span className="font-semibold text-content">{data.ticker}</span> | Current Price:{" "}
            <span className="font-semibold text-content">{formatCurrency(data.current_price, "INR")}</span> | Sector:{" "}
            <span className="font-semibold text-content">{data.sector}</span> | Systematic Beta:{" "}
            <span className="font-semibold text-content">{data.beta.toFixed(2)}</span>
          </p>
        </div>

        <Badge variant="loss" size="sm">
          HISTORICAL OBSERVATIONS
        </Badge>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {resultsList.map(([key, crisis]) => {
          const isDrawdownSevere = crisis.projected_drawdown_pct <= -40;

          return (
            <div
              key={key}
              className={`p-4 rounded-xl border transition-all ${
                isDrawdownSevere
                  ? "bg-financial-loss/5 border-financial-loss/30"
                  : "bg-surface-subtle/60 border-border"
              }`}
            >
              <div className="flex items-start justify-between gap-2 mb-2">
                <div>
                  <h4 className="text-xs font-bold text-content">{crisis.scenario_name}</h4>
                  <div className="flex items-center gap-1.5 text-[10px] text-content-muted mt-0.5">
                    <Clock className="w-3 h-3 text-secondary" />
                    <span>{crisis.period}</span>
                  </div>
                </div>
                <Badge variant="loss" size="sm">
                  {crisis.projected_drawdown_pct.toFixed(1)}%
                </Badge>
              </div>

              <p className="text-[11px] text-content-muted leading-relaxed mb-3">
                {crisis.description}
              </p>

              <div className="grid grid-cols-2 gap-2 pt-2 border-t border-border/80">
                <div>
                  <span className="text-[10px] text-content-muted uppercase">Stressed Price</span>
                  <p className="text-xs font-bold text-content font-tabular">
                    {formatCurrency(crisis.stressed_price, "INR")}
                  </p>
                </div>
                <div>
                  <span className="text-[10px] text-content-muted uppercase">Loss Per Share</span>
                  <p className="text-xs font-bold text-financial-loss font-tabular">
                    -{formatCurrency(crisis.estimated_loss_per_share, "INR")}
                  </p>
                </div>
              </div>
            </div>
          );
        })}
      </div>

      <div className="bg-surface-subtle p-3 rounded-xl border border-border flex items-start gap-2 text-[11px] text-content-muted">
        <Info className="w-4 h-4 text-primary shrink-0 mt-0.5" />
        <p>
          Historical scenario stress testing models the asset’s sector sensitivity and systematic beta against historical market drawdowns.
          These represent historical crisis patterns and are not guarantees of future performance.
        </p>
      </div>
    </div>
  );
};
