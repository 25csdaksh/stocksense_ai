"use client";

import React from "react";
import { Card, CardHeader, CardTitle, CardDescription, CardContent } from "@/components/common/Card";
import { Badge } from "@/components/common/Badge";
import { EnrichedAnomalyItem } from "@/hooks/useAnomalyFeed";
import { Clock, ShieldAlert, ArrowRight, Zap } from "lucide-react";

export interface AnomalyTimelineProps {
  anomalies: EnrichedAnomalyItem[];
  selectedAnomalyId?: string | null;
  onSelectAnomaly: (item: EnrichedAnomalyItem) => void;
}

export const AnomalyTimeline: React.FC<AnomalyTimelineProps> = ({
  anomalies,
  selectedAnomalyId,
  onSelectAnomaly,
}) => {
  const sorted = [...anomalies]
    .sort((a, b) => new Date(b.timestamp).getTime() - new Date(a.timestamp).getTime())
    .slice(0, 8);

  return (
    <Card>
      <CardHeader className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-2 pb-2">
        <div>
          <CardTitle className="flex items-center gap-2">
            <Clock className="w-4 h-4 text-primary" />
            Anomaly Event Horizon &amp; Timeline
          </CardTitle>
          <CardDescription>Chronological sequence of statistical breakout signals</CardDescription>
        </div>
      </CardHeader>

      <CardContent>
        {sorted.length === 0 ? (
          <div className="p-8 text-center text-xs text-content-muted">
            No chronological anomaly events recorded in current horizon.
          </div>
        ) : (
          <div className="relative pl-6 space-y-4 before:absolute before:left-2.5 before:top-2 before:bottom-2 before:w-0.5 before:bg-border">
            {sorted.map((item) => {
              const isSelected = selectedAnomalyId === item.id;
              const isCritical = item.severity === "CRITICAL";
              const isHigh = item.severity === "HIGH";

              const dotColor = isCritical
                ? "bg-financial-loss ring-4 ring-financial-loss-bg"
                : isHigh
                ? "bg-amber-500 ring-4 ring-amber-100"
                : "bg-primary ring-4 ring-primary-light";

              return (
                <div
                  key={item.id}
                  onClick={() => onSelectAnomaly(item)}
                  className={`relative p-3 rounded-xl border transition-all cursor-pointer ${
                    isSelected
                      ? "border-primary bg-primary-light/40 shadow-xs"
                      : "border-border bg-surface hover:bg-surface-subtle"
                  }`}
                >
                  {/* Timeline dot */}
                  <span
                    className={`absolute -left-[27px] top-4 w-2.5 h-2.5 rounded-full ${dotColor}`}
                  />

                  <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-1.5">
                    <div className="flex items-center gap-2">
                      <span className="font-bold text-content text-xs">{item.ticker}</span>
                      <Badge
                        variant={isCritical ? "loss" : isHigh ? "gold" : "neutral"}
                        size="sm"
                        className="text-[9px] font-bold"
                      >
                        {item.anomaly_type}
                      </Badge>
                      <span className="text-[10px] font-mono font-semibold text-financial-loss">
                        +{item.z_score?.toFixed(2)}σ
                      </span>
                    </div>

                    <span className="text-[10px] text-content-muted font-mono whitespace-nowrap">
                      {item.formatted_time}
                    </span>
                  </div>

                  <p className="text-xs text-content-muted mt-1 line-clamp-1">{item.summary}</p>
                </div>
              );
            })}
          </div>
        )}
      </CardContent>
    </Card>
  );
};
