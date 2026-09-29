"use client";

import React, { useState } from "react";
import Link from "next/link";
import { Card, CardHeader, CardTitle, CardDescription, CardContent } from "@/components/common/Card";
import { Badge } from "@/components/common/Badge";
import { EnrichedAnomalyItem } from "@/hooks/useAnomalyFeed";
import {
  ShieldAlert,
  AlertTriangle,
  ArrowRight,
  ExternalLink,
  Zap,
  Activity,
} from "lucide-react";

export interface AnomalyFeedProps {
  anomalies: EnrichedAnomalyItem[];
  selectedAnomalyId?: string | null;
  onSelectAnomaly: (item: EnrichedAnomalyItem) => void;
  isLoading?: boolean;
}

export const AnomalyFeed: React.FC<AnomalyFeedProps> = ({
  anomalies,
  selectedAnomalyId,
  onSelectAnomaly,
  isLoading = false,
}) => {
  return (
    <Card className="overflow-hidden">
      <CardHeader className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-3 pb-3">
        <div>
          <div className="flex items-center gap-2">
            <CardTitle className="flex items-center gap-2">
              <ShieldAlert className="w-4 h-4 text-financial-loss" />
              Active Anomaly Surveillance Feed
            </CardTitle>
            <Badge variant="neutral" size="sm">
              {anomalies.length} Filtered Signals
            </Badge>
          </div>
          <CardDescription>
            Multi-model statistical deviations detected via Isolation Forest, GARCH volatility, and Volume Z-Score.
          </CardDescription>
        </div>
      </CardHeader>

      <CardContent className="p-0">
        {anomalies.length === 0 ? (
          <div className="p-12 text-center text-xs text-content-muted">
            No statistical anomalies currently match the selected filter criteria.
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs border-collapse">
              <thead>
                <tr className="border-b border-border bg-surface-subtle/50 text-content-muted font-semibold">
                  <th className="p-3.5 pl-4">Time</th>
                  <th className="p-3.5">Asset / Symbol</th>
                  <th className="p-3.5">Anomaly Type</th>
                  <th className="p-3.5 text-right">Observed Value</th>
                  <th className="p-3.5 text-right">Expected Baseline</th>
                  <th className="p-3.5 text-right">Z-Score</th>
                  <th className="p-3.5 text-center">Severity</th>
                  <th className="p-3.5">Detection Model</th>
                  <th className="p-3.5 pr-4 text-center">Inspect</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-border/60">
                {anomalies.map((item) => {
                  const isSelected = selectedAnomalyId === item.id;
                  const isCritical = item.severity === "CRITICAL";
                  const isHigh = item.severity === "HIGH";

                  return (
                    <tr
                      key={item.id}
                      onClick={() => onSelectAnomaly(item)}
                      className={`hover:bg-surface-subtle transition-colors cursor-pointer ${
                        isSelected ? "bg-primary-light/40 font-medium" : ""
                      }`}
                    >
                      {/* Time */}
                      <td className="p-3.5 pl-4 whitespace-nowrap text-content-muted font-mono text-[11px]">
                        {item.formatted_time}
                      </td>

                      {/* Asset / Symbol */}
                      <td className="p-3.5">
                        <div className="flex items-center gap-2">
                          <div
                            className={`w-2 h-2 rounded-full ${
                              isCritical ? "bg-financial-loss animate-pulse" : isHigh ? "bg-amber-500" : "bg-primary"
                            }`}
                          />
                          <div>
                            <span className="font-bold text-content hover:text-primary transition-colors">
                              {item.ticker}
                            </span>
                            {item.company_name && (
                              <p className="text-[10px] text-content-muted truncate max-w-[130px]">
                                {item.company_name}
                              </p>
                            )}
                          </div>
                        </div>
                      </td>

                      {/* Anomaly Type */}
                      <td className="p-3.5">
                        <Badge
                          variant={isCritical ? "loss" : isHigh ? "gold" : "neutral"}
                          size="sm"
                          className="font-bold text-[9px] uppercase tracking-wider"
                        >
                          {item.anomaly_type}
                        </Badge>
                      </td>

                      {/* Observed Value */}
                      <td className="p-3.5 text-right font-tabular text-content font-semibold">
                        {item.observed_value}
                      </td>

                      {/* Expected Baseline */}
                      <td className="p-3.5 text-right font-tabular text-content-muted text-[11px]">
                        {item.expected_value}
                      </td>

                      {/* Z-Score */}
                      <td className="p-3.5 text-right font-tabular font-bold text-financial-loss">
                        +{item.z_score?.toFixed(2)}σ
                      </td>

                      {/* Severity */}
                      <td className="p-3.5 text-center">
                        <Badge
                          variant={
                            item.severity === "CRITICAL"
                              ? "loss"
                              : item.severity === "HIGH"
                              ? "gold"
                              : item.severity === "MEDIUM"
                              ? "primary"
                              : "secondary"
                          }
                          size="sm"
                          className="font-bold text-[9px] uppercase"
                        >
                          {item.severity}
                        </Badge>
                      </td>

                      {/* Detection Model */}
                      <td className="p-3.5 text-content-muted text-[11px] truncate max-w-[150px]">
                        {item.model_name}
                      </td>

                      {/* Inspect Action */}
                      <td className="p-3.5 pr-4 text-center">
                        <button
                          onClick={(e: React.MouseEvent) => {
                            e.stopPropagation();
                            onSelectAnomaly(item);
                          }}
                          className="p-1.5 rounded-lg border border-border bg-surface text-content-muted hover:text-primary hover:border-primary/40 transition-all text-xs"
                          title="Open Anomaly Inspector"
                        >
                          <ArrowRight className="w-3.5 h-3.5" />
                        </button>
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        )}
      </CardContent>
    </Card>
  );
};
