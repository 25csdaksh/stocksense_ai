"use client";

import React from "react";
import { PortfolioChangeReport } from "@/types/portfolio-copilot";
import { History, ArrowRight, TrendingUp, Scale, Clock } from "lucide-react";

interface PortfolioChangeTimelineProps {
  changeReport: PortfolioChangeReport;
}

export const PortfolioChangeTimeline: React.FC<PortfolioChangeTimelineProps> = ({
  changeReport,
}) => {
  const allChanges = [
    ...changeReport.holding_changes,
    ...changeReport.valuation_changes,
    ...changeReport.risk_changes,
    ...changeReport.research_changes,
  ];

  return (
    <div className="bg-surface border border-border rounded-2xl p-6 shadow-card space-y-5">
      <div className="flex items-center justify-between border-b border-border pb-4">
        <div className="flex items-center gap-2">
          <div className="p-2 rounded-xl bg-primary/10 text-primary border border-primary/20">
            <History className="w-5 h-5" />
          </div>
          <div>
            <h3 className="text-sm font-black text-content uppercase tracking-wider">
              Research Delta & Change Audit
            </h3>
            <p className="text-xs text-content-muted">
              Audited metric and weight deviations relative to prior research
            </p>
          </div>
        </div>

        <span className="text-xs font-mono font-bold px-2 py-0.5 rounded bg-surface-subtle border border-border text-primary">
          {changeReport.total_changes} DELTAS
        </span>
      </div>

      <p className="text-xs text-content-muted bg-surface-subtle p-3 rounded-xl border border-border/60">
        {changeReport.summary}
      </p>

      {allChanges.length > 0 && (
        <div className="space-y-2.5 pt-1">
          {allChanges.map((item, idx) => (
            <div
              key={idx}
              className="p-3.5 bg-surface-subtle rounded-xl border border-border/70 flex flex-col sm:flex-row sm:items-center justify-between gap-2 text-xs"
            >
              <div className="space-y-1">
                <div className="flex items-center gap-2">
                  <span className="px-1.5 py-0.5 rounded bg-surface border border-border text-[9px] font-mono font-bold text-primary">
                    {item.change_type}
                  </span>
                  {item.symbol && (
                    <span className="font-bold text-content font-mono">{item.symbol}</span>
                  )}
                </div>
                <p className="text-content leading-relaxed">{item.description}</p>
              </div>

              {item.previous_value !== undefined && item.current_value !== undefined && (
                <div className="flex items-center gap-2 font-mono font-bold text-content flex-shrink-0 bg-surface px-2.5 py-1 rounded-lg border border-border">
                  <span className="text-content-muted">{String(item.previous_value)}</span>
                  <ArrowRight className="w-3 h-3 text-primary" />
                  <span className="text-primary">{String(item.current_value)}</span>
                </div>
              )}
            </div>
          ))}
        </div>
      )}
    </div>
  );
};
