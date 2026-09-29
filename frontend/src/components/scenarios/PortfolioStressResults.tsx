"use client";

import React from "react";
import { PortfolioStressTestResponse } from "@/types";
import { formatCurrency } from "@/lib/utils";
import { Briefcase, TrendingDown, Clock, ShieldAlert } from "lucide-react";
import { Badge } from "@/components/common/Badge";

interface PortfolioStressResultsProps {
  data: PortfolioStressTestResponse | null;
  isLoading: boolean;
}

export const PortfolioStressResults: React.FC<PortfolioStressResultsProps> = ({
  data,
  isLoading,
}) => {
  if (isLoading) {
    return (
      <div className="bg-surface p-6 rounded-2xl border border-border shadow-card h-80 flex flex-col items-center justify-center space-y-3">
        <div className="w-8 h-8 border-2 border-primary border-t-transparent rounded-full animate-spin" />
        <p className="text-xs text-content-muted">Executing multi-asset portfolio crisis stress test...</p>
      </div>
    );
  }

  if (!data || !data.crises_stress_results) {
    return (
      <div className="bg-surface p-6 rounded-2xl border border-border shadow-card h-80 flex items-center justify-center text-xs text-content-muted">
        No portfolio stress test results available. Select Portfolio mode and click "Run Scenario".
      </div>
    );
  }

  const crisisList = Object.entries(data.crises_stress_results);

  return (
    <div className="bg-surface p-5 rounded-2xl border border-border shadow-card space-y-4">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2 border-b border-border pb-3">
        <div>
          <div className="flex items-center gap-2">
            <Briefcase className="w-4 h-4 text-primary" />
            <h3 className="text-sm font-bold text-content uppercase tracking-wider">
              Portfolio Crisis Stress Testing
            </h3>
          </div>
          <p className="text-[11px] text-content-muted mt-0.5">
            Initial Portfolio Market Value:{" "}
            <span className="font-bold text-content font-tabular">
              {formatCurrency(data.initial_portfolio_value, "INR")}
            </span>
          </p>
        </div>

        <Badge variant="loss" size="sm">
          PORTFOLIO SIMULATION
        </Badge>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {crisisList.map(([key, crisis]) => {
          return (
            <div
              key={key}
              className="p-4 rounded-xl border bg-surface-subtle/60 border-border space-y-2.5"
            >
              <div className="flex items-start justify-between gap-2">
                <div>
                  <h4 className="text-xs font-bold text-content">{crisis.crisis_name}</h4>
                  <div className="flex items-center gap-1.5 text-[10px] text-content-muted mt-0.5">
                    <Clock className="w-3 h-3 text-secondary" />
                    <span>{crisis.period}</span>
                  </div>
                </div>
                <Badge variant="loss" size="sm">
                  {crisis.projected_drawdown_pct.toFixed(1)}%
                </Badge>
              </div>

              <p className="text-[11px] text-content-muted leading-relaxed">
                {crisis.description}
              </p>

              <div className="grid grid-cols-2 gap-2 pt-2 border-t border-border/80">
                <div>
                  <span className="text-[10px] text-content-muted uppercase">Stressed Value</span>
                  <p className="text-xs font-bold text-content font-tabular">
                    {formatCurrency(crisis.stressed_portfolio_value, "INR")}
                  </p>
                </div>
                <div>
                  <span className="text-[10px] text-content-muted uppercase">Simulated Loss</span>
                  <p className="text-xs font-bold text-financial-loss font-tabular">
                    -{formatCurrency(crisis.projected_portfolio_loss_dollars, "INR")}
                  </p>
                </div>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
};
