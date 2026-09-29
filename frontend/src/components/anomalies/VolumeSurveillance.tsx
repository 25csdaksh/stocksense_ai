"use client";

import React from "react";
import { Card, CardHeader, CardTitle, CardDescription, CardContent } from "@/components/common/Card";
import { Badge } from "@/components/common/Badge";
import { formatNumber } from "@/lib/utils";
import { Zap, Activity, BarChart2 } from "lucide-react";

export interface VolumeSurveillanceProps {
  ticker: string;
  currentVolume?: number;
  avgVolume?: number;
  volumeRatio?: number;
  volumeZScore?: number;
}

export const VolumeSurveillance: React.FC<VolumeSurveillanceProps> = ({
  ticker,
  currentVolume = 14250000,
  avgVolume = 4180000,
  volumeRatio = 3.41,
  volumeZScore = 3.42,
}) => {
  const isSurge = volumeRatio > 2.0;

  return (
    <Card>
      <CardHeader className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-2 pb-2">
        <div>
          <div className="flex items-center gap-2">
            <CardTitle className="flex items-center gap-2">
              <Zap className="w-4 h-4 text-amber-500" />
              Volume Flow Surveillance: {ticker}
            </CardTitle>
            <Badge variant={isSurge ? "loss" : "neutral"} size="sm">
              {isSurge ? "INSTITUTIONAL SURGE" : "NORMAL FLOW"}
            </Badge>
          </div>
          <CardDescription>
            Order flow concentration and abnormal volume acceleration relative to 30-day baseline.
          </CardDescription>
        </div>
      </CardHeader>

      <CardContent className="space-y-4">
        <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
          <div className="p-3 bg-surface-subtle rounded-xl border border-border space-y-1">
            <span className="text-[10px] uppercase font-bold text-content-muted">Current Session Volume</span>
            <div className="text-base font-bold text-content font-tabular">
              {formatNumber(currentVolume, { compact: true })}
            </div>
            <span className="text-[10px] text-content-muted">Shares traded</span>
          </div>

          <div className="p-3 bg-surface-subtle rounded-xl border border-border space-y-1">
            <span className="text-[10px] uppercase font-bold text-content-muted">30-Day Avg Volume</span>
            <div className="text-base font-bold text-content font-tabular">
              {formatNumber(avgVolume, { compact: true })}
            </div>
            <span className="text-[10px] text-content-muted">Baseline liquidity</span>
          </div>

          <div className="p-3 bg-surface-subtle rounded-xl border border-border space-y-1">
            <span className="text-[10px] uppercase font-bold text-content-muted">Volume Ratio</span>
            <div className="text-base font-bold text-financial-loss font-tabular">
              {volumeRatio.toFixed(2)}x
            </div>
            <span className="text-[10px] text-content-muted">Multiple of average</span>
          </div>

          <div className="p-3 bg-surface-subtle rounded-xl border border-border space-y-1">
            <span className="text-[10px] uppercase font-bold text-content-muted">Volume Z-Score</span>
            <div className="text-base font-bold text-amber-600 font-tabular">
              +{volumeZScore.toFixed(2)}σ
            </div>
            <span className="text-[10px] text-content-muted">Standard deviation</span>
          </div>
        </div>

        {/* Visual Volume Comparison Meter */}
        <div className="space-y-2 p-3.5 bg-surface-subtle/50 rounded-xl border border-border">
          <div className="flex items-center justify-between text-xs">
            <span className="font-semibold text-content">Session vs Baseline Ratio</span>
            <span className="font-bold text-primary font-tabular">{volumeRatio.toFixed(1)}x Expansion</span>
          </div>
          <div className="w-full h-2.5 bg-surface border border-border rounded-full overflow-hidden">
            <div
              className={`h-full rounded-full transition-all duration-500 ${
                isSurge ? "bg-amber-500" : "bg-primary"
              }`}
              style={{ width: `${Math.min(100, (volumeRatio / 4) * 100)}%` }}
            />
          </div>
          <div className="flex items-center justify-between text-[10px] text-content-muted">
            <span>1.0x Normal</span>
            <span>2.0x Threshold</span>
            <span>3.0x+ Extreme Surge</span>
          </div>
        </div>
      </CardContent>
    </Card>
  );
};
