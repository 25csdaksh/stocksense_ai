"use client";

import React from "react";
import { Card, CardHeader, CardTitle, CardDescription, CardContent } from "@/components/common/Card";
import { Badge } from "@/components/common/Badge";
import { formatPercent } from "@/lib/utils";
import { ConcentrationMetrics } from "@/types";
import { PieChart, Layers, Shield } from "lucide-react";

export interface ConcentrationAnalysisProps {
  concentration: ConcentrationMetrics;
}

export const ConcentrationAnalysis: React.FC<ConcentrationAnalysisProps> = ({ concentration }) => {
  const bars = [
    {
      label: `Top 1 Position (${concentration.top_1_ticker})`,
      value: concentration.top_1_weight_pct,
      color: "bg-primary",
      description: "Weight of largest single asset",
    },
    {
      label: "Top 3 Holdings Combined",
      value: concentration.top_3_weight_pct,
      color: "bg-secondary",
      description: "Cumulative weight of top 3 constituents",
    },
    {
      label: "Top 5 Holdings Combined",
      value: concentration.top_5_weight_pct,
      color: "bg-accent-dark",
      description: "Cumulative weight of top 5 constituents",
    },
    {
      label: `Largest Sector (${concentration.largest_sector_name})`,
      value: concentration.largest_sector_weight_pct,
      color: "bg-primary-dark",
      description: "Industry concentration exposure",
    },
  ];

  return (
    <Card>
      <CardHeader className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-2 pb-2">
        <div>
          <div className="flex items-center gap-2">
            <CardTitle className="flex items-center gap-2">
              <PieChart className="w-4 h-4 text-primary" />
              Holding & Sector Concentration Analysis
            </CardTitle>
            <Badge variant="neutral" size="sm" className="font-mono text-[10px]">
              HHI: {concentration.hhi_index}
            </Badge>
          </div>
          <CardDescription>
            Factual measurement of capital concentration and single-stock dependency.
          </CardDescription>
        </div>
      </CardHeader>

      <CardContent className="space-y-4">
        <div className="space-y-3.5">
          {bars.map((bar, idx) => (
            <div key={idx} className="space-y-1.5">
              <div className="flex items-center justify-between text-xs">
                <span className="font-semibold text-content">{bar.label}</span>
                <span className="font-bold text-primary font-tabular">
                  {formatPercent(bar.value)}
                </span>
              </div>

              {/* Progress bar */}
              <div className="w-full h-2.5 bg-surface-subtle border border-border rounded-full overflow-hidden">
                <div
                  className={`h-full ${bar.color} rounded-full transition-all duration-500`}
                  style={{ width: `${Math.min(100, Math.max(0, bar.value))}%` }}
                />
              </div>

              <div className="flex items-center justify-between text-[10px] text-content-muted">
                <span>{bar.description}</span>
                <span className="font-tabular font-medium">
                  {bar.value.toFixed(1)}% of total portfolio
                </span>
              </div>
            </div>
          ))}
        </div>

        {/* HHI Explanation Box */}
        <div className="p-3 bg-surface-subtle/70 rounded-xl border border-border flex items-start gap-2.5 text-xs text-content-muted">
          <Shield className="w-4 h-4 text-primary flex-shrink-0 mt-0.5" />
          <p className="leading-relaxed">
            <strong className="text-content font-semibold">Herfindahl-Hirschman Index (HHI): </strong>
            Calculated at <span className="font-mono font-bold text-content">{concentration.hhi_index}</span> based on current asset weights. An index under 1,500 indicates a diversified distribution, while above 2,500 indicates high concentration.
          </p>
        </div>
      </CardContent>
    </Card>
  );
};
