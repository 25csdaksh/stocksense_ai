"use client";

import React from "react";
import { Card, CardHeader, CardTitle, CardDescription, CardContent } from "@/components/common/Card";
import { Badge } from "@/components/common/Badge";
import { formatPercent, formatCurrency } from "@/lib/utils";
import { EnrichedAnomalyItem } from "@/hooks/useAnomalyFeed";
import { Activity, Gauge, Zap, Shield, Info } from "lucide-react";

export interface AnomalySignalBreakdownProps {
  anomaly: EnrichedAnomalyItem | null;
}

export const AnomalySignalBreakdown: React.FC<AnomalySignalBreakdownProps> = ({ anomaly }) => {
  if (!anomaly) {
    return (
      <Card>
        <CardContent className="p-8 text-center text-xs text-content-muted">
          Select an anomaly signal from the surveillance feed to inspect its multivariate statistical telemetry.
        </CardContent>
      </Card>
    );
  }

  const metrics = anomaly.metrics || {};
  const isolationScore = anomaly.isolation_score ?? -0.35;
  const zScore = anomaly.z_score ?? 3.12;
  const volZ = metrics.volume_z_score ?? 2.85;
  const garchVol = metrics.garch_volatility_pct ?? 34.2;
  const atr = metrics.atr_14 ?? 48.5;
  const priceImpulse = metrics.impulse_pct ?? 2.4;

  const signals = [
    {
      label: "Isolation Forest Score",
      value: isolationScore.toFixed(3),
      sub: "Contamination boundary (< -0.30)",
      badge: "Tree-Based Isolation",
      isOutlier: isolationScore < -0.3,
    },
    {
      label: "Price Impulse Z-Score",
      value: `+${zScore.toFixed(2)}σ`,
      sub: "Standard deviation from mean",
      badge: "Gaussian Z-Score",
      isOutlier: zScore > 2.5,
    },
    {
      label: "Volume Z-Score",
      value: `+${volZ.toFixed(2)}σ`,
      sub: "Intraday volume concentration",
      badge: "Volume Surge",
      isOutlier: volZ > 3.0,
    },
    {
      label: "GARCH(1,1) Conditional Vol",
      value: formatPercent(garchVol),
      sub: "Model-derived variance regime",
      badge: "GARCH Model",
      isOutlier: garchVol > 30,
    },
    {
      label: "Average True Range (ATR-14)",
      value: formatCurrency(atr, "INR"),
      sub: "14-day absolute volatility",
      badge: "Technical Range",
      isOutlier: false,
    },
    {
      label: "Candle Return Deviation",
      value: formatPercent(priceImpulse),
      sub: "Single bar price excursion",
      badge: "Session Return",
      isOutlier: priceImpulse > 2.0,
    },
  ];

  return (
    <Card>
      <CardHeader className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-2 pb-2">
        <div>
          <div className="flex items-center gap-2">
            <CardTitle className="flex items-center gap-2">
              <Activity className="w-4 h-4 text-primary" />
              Statistical Signal Breakdown: {anomaly.ticker}
            </CardTitle>
            <Badge variant="loss" size="sm">
              {anomaly.anomaly_type}
            </Badge>
          </div>
          <CardDescription>
            Multi-model mathematical telemetry capturing statistical departure from historical distribution.
          </CardDescription>
        </div>
      </CardHeader>

      <CardContent className="space-y-4">
        <div className="grid grid-cols-2 sm:grid-cols-3 gap-3">
          {signals.map((sig, idx) => (
            <div
              key={idx}
              className="p-3 bg-surface-subtle/60 rounded-xl border border-border space-y-1.5 hover:bg-surface-subtle transition-all"
            >
              <div className="flex items-center justify-between">
                <span className="text-[10px] font-bold text-content-muted uppercase tracking-wider">
                  {sig.label}
                </span>
                <Badge variant={sig.isOutlier ? "loss" : "neutral"} size="sm" className="text-[8px] py-0 px-1">
                  {sig.badge}
                </Badge>
              </div>

              <div
                className={`text-lg font-bold font-tabular ${
                  sig.isOutlier ? "text-financial-loss" : "text-content"
                }`}
              >
                {sig.value}
              </div>

              <div className="text-[10px] text-content-muted truncate">{sig.sub}</div>
            </div>
          ))}
        </div>

        {/* Statistical disclaimer */}
        <div className="p-3 bg-surface-subtle/70 rounded-xl border border-border flex items-start gap-2.5 text-xs text-content-muted">
          <Info className="w-4 h-4 text-primary flex-shrink-0 mt-0.5" />
          <p className="leading-relaxed">
            <strong className="text-content font-semibold">Mathematical Note: </strong>
            These quantitative signals measure historical dispersion and non-linear isolation. They represent empirical observations of unusual market behavior and do not constitute price direction predictions.
          </p>
        </div>
      </CardContent>
    </Card>
  );
};
