"use client";

import React from "react";
import { Card, CardHeader, CardTitle, CardDescription, CardContent } from "@/components/common/Card";
import { Badge } from "@/components/common/Badge";
import { PieChart, ShieldAlert, Layers } from "lucide-react";

export interface AnomalySeverityDistributionProps {
  distribution: { LOW: number; MEDIUM: number; HIGH: number; CRITICAL: number };
  activeSeverity: string;
  onSelectSeverity: (sev: string) => void;
}

export const AnomalySeverityDistribution: React.FC<AnomalySeverityDistributionProps> = ({
  distribution,
  activeSeverity,
  onSelectSeverity,
}) => {
  const total = distribution.LOW + distribution.MEDIUM + distribution.HIGH + distribution.CRITICAL || 1;

  const items = [
    {
      level: "CRITICAL",
      count: distribution.CRITICAL,
      color: "bg-financial-loss",
      textColor: "text-financial-loss",
      bgSubtle: "bg-financial-loss-bg",
      border: "border-financial-loss/30",
      description: "> 4.0σ Extreme Impulse / Flash Event",
    },
    {
      level: "HIGH",
      count: distribution.HIGH,
      color: "bg-amber-500",
      textColor: "text-amber-600",
      bgSubtle: "bg-amber-50",
      border: "border-amber-200",
      description: "3.0σ - 4.0σ Block Volume / Volatility Surge",
    },
    {
      level: "MEDIUM",
      count: distribution.MEDIUM,
      color: "bg-primary",
      textColor: "text-primary",
      bgSubtle: "bg-primary-light",
      border: "border-primary/20",
      description: "2.0σ - 3.0σ Correlation De-link / Spread Divergence",
    },
    {
      level: "LOW",
      count: distribution.LOW,
      color: "bg-secondary",
      textColor: "text-secondary",
      bgSubtle: "bg-surface-subtle",
      border: "border-border",
      description: "< 2.0σ Mild Statistical Isolation",
    },
  ];

  return (
    <Card>
      <CardHeader className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-2 pb-2">
        <div>
          <CardTitle className="flex items-center gap-2">
            <PieChart className="w-4 h-4 text-primary" />
            Severity Distribution
          </CardTitle>
          <CardDescription>Click a tier to filter the live surveillance feed</CardDescription>
        </div>
      </CardHeader>

      <CardContent className="space-y-3.5">
        <div className="grid grid-cols-2 sm:grid-cols-4 gap-2.5">
          {items.map((item) => {
            const isSelected = activeSeverity === item.level;
            const pct = ((item.count / total) * 100).toFixed(0);

            return (
              <button
                key={item.level}
                onClick={() => onSelectSeverity(isSelected ? "ALL" : item.level)}
                className={`p-3 rounded-xl border text-left transition-all space-y-1.5 ${
                  isSelected
                    ? "ring-2 ring-primary border-transparent bg-surface shadow-xs"
                    : `${item.bgSubtle} ${item.border} hover:bg-surface`
                }`}
              >
                <div className="flex items-center justify-between">
                  <span className={`text-[10px] font-bold uppercase tracking-wider ${item.textColor}`}>
                    {item.level}
                  </span>
                  <span className="text-[10px] text-content-muted font-tabular">{pct}%</span>
                </div>

                <div className="text-xl font-bold text-content font-tabular">
                  {item.count} <span className="text-xs font-medium text-content-muted">Signals</span>
                </div>

                {/* Meter */}
                <div className="w-full h-1.5 bg-border/50 rounded-full overflow-hidden">
                  <div
                    className={`h-full ${item.color} rounded-full`}
                    style={{ width: `${Math.min(100, (item.count / total) * 100)}%` }}
                  />
                </div>
              </button>
            );
          })}
        </div>
      </CardContent>
    </Card>
  );
};
