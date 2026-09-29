"use client";

import React from "react";
import { StatCard } from "@/components/common/StatCard";
import { Badge } from "@/components/common/Badge";
import { formatPercent } from "@/lib/utils";
import {
  Activity,
  AlertTriangle,
  Zap,
  TrendingDown,
  Gauge,
  ShieldAlert,
} from "lucide-react";

export interface SystemicStressOverviewProps {
  systemicStressIndex: number;
  totalActiveCount: number;
  highCount: number;
  criticalCount: number;
  marketVolatility?: number;
}

export const SystemicStressOverview: React.FC<SystemicStressOverviewProps> = ({
  systemicStressIndex,
  totalActiveCount,
  highCount,
  criticalCount,
  marketVolatility = 14.8,
}) => {
  const isElevated = systemicStressIndex > 40;
  const isCritical = systemicStressIndex > 70;

  return (
    <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-5 gap-3.5">
      {/* 1. Systemic Stress Index */}
      <div className="p-4 rounded-xl border border-border bg-surface shadow-card space-y-2 relative overflow-hidden">
        <div className="flex items-center justify-between">
          <span className="text-xs font-semibold text-content-muted uppercase tracking-wider">
            Systemic Stress Index
          </span>
          <Badge
            variant={isCritical ? "loss" : isElevated ? "gold" : "gain"}
            size="sm"
            className="text-[9px] uppercase font-bold"
          >
            Model-Derived
          </Badge>
        </div>
        <div className="flex items-baseline gap-2">
          <span className="text-2xl font-bold text-content font-tabular">
            {systemicStressIndex.toFixed(1)}
          </span>
          <span className="text-xs text-content-muted font-medium">/ 100</span>
        </div>
        {/* Progress Bar */}
        <div className="w-full h-1.5 bg-surface-subtle border border-border rounded-full overflow-hidden">
          <div
            className={`h-full rounded-full transition-all duration-500 ${
              isCritical ? "bg-financial-loss" : isElevated ? "bg-amber-500" : "bg-emerald-500"
            }`}
            style={{ width: `${Math.min(100, Math.max(5, systemicStressIndex))}%` }}
          />
        </div>
        <p className="text-[10px] text-content-muted">
          {isCritical ? "High market co-deviation" : isElevated ? "Elevated multivariate dispersion" : "Normal statistical variance"}
        </p>
      </div>

      {/* 2. Total Active Anomalies */}
      <StatCard
        label="Active Anomalies"
        value={`${totalActiveCount} Signals`}
        changeLabel="Cross-universe detections"
        icon={<Activity className="w-4 h-4 text-primary" />}
      />

      {/* 3. Critical Severity */}
      <StatCard
        label="Critical Anomalies"
        value={`${criticalCount} Alerts`}
        changeLabel="> 4.0σ extreme deviation"
        icon={<ShieldAlert className="w-4 h-4 text-financial-loss" />}
      />

      {/* 4. High Severity */}
      <StatCard
        label="High Severity"
        value={`${highCount} Events`}
        changeLabel="3.0σ - 4.0σ volume/price skew"
        icon={<AlertTriangle className="w-4 h-4 text-amber-600" />}
      />

      {/* 5. Realized Market Volatility */}
      <StatCard
        label="Realized Volatility"
        value={formatPercent(marketVolatility)}
        changeLabel="20-day annualized EWMA"
        icon={<Gauge className="w-4 h-4 text-secondary" />}
      />
    </div>
  );
};
