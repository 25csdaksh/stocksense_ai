"use client";

import React from "react";
import Link from "next/link";
import { useStockAnomalies } from "@/hooks/useStockAnomalies";
import { Card, CardHeader, CardTitle, CardDescription, CardContent } from "@/components/common/Card";
import { Badge } from "@/components/common/Badge";
import { Skeleton } from "@/components/common/Skeleton";
import { Button } from "@/components/common/Button";
import { AlertTriangle, ArrowRight, Zap, CheckCircle2, AlertCircle, RefreshCw } from "lucide-react";
import { cn, formatCurrency } from "@/lib/utils";

export interface AnomalyIntelligenceProps {
  ticker: string;
  currency?: string;
  isDemo?: boolean;
}

export const AnomalyIntelligence: React.FC<AnomalyIntelligenceProps> = ({
  ticker,
  currency = "INR",
  isDemo: parentDemo = false,
}) => {
  const { anomalies, volumeSpike, volatilityRegime, isLoading, isError, error, isDemo, refresh } =
    useStockAnomalies(ticker);

  const displayDemo = parentDemo || isDemo;

  if (isLoading) {
    return (
      <Card className="border-border">
        <CardHeader>
          <Skeleton className="h-6 w-48" />
          <Skeleton className="h-4 w-72" />
        </CardHeader>
        <CardContent>
          <div className="space-y-3">
            {[1, 2, 3].map((i) => (
              <Skeleton key={i} className="h-16 rounded-xl" />
            ))}
          </div>
        </CardContent>
      </Card>
    );
  }

  if (isError) {
    return (
      <Card className="border-border">
        <CardContent className="py-8 text-center space-y-3">
          <AlertCircle className="w-8 h-8 text-financial-loss mx-auto" />
          <p className="text-sm font-semibold text-content">Unable to load anomaly intelligence</p>
          <p className="text-xs text-content-muted">{error || "Server response unavailable"}</p>
          <Button variant="outline" size="sm" onClick={() => refresh()}>
            Retry
          </Button>
        </CardContent>
      </Card>
    );
  }

  const getSeverityBadge = (score: number, severity?: string) => {
    if (severity) {
      if (severity === "CRITICAL") return <Badge variant="loss" size="sm">CRITICAL</Badge>;
      if (severity === "HIGH") return <Badge variant="loss" size="sm">HIGH</Badge>;
      if (severity === "MEDIUM") return <Badge variant="gold" size="sm">MEDIUM</Badge>;
      return <Badge variant="neutral" size="sm">LOW</Badge>;
    }
    if (score >= 0.75) return <Badge variant="loss" size="sm">CRITICAL</Badge>;
    if (score >= 0.55) return <Badge variant="loss" size="sm">HIGH</Badge>;
    if (score >= 0.35) return <Badge variant="gold" size="sm">MEDIUM</Badge>;
    return <Badge variant="neutral" size="sm">LOW</Badge>;
  };

  return (
    <Card className="border-border shadow-card">
      <CardHeader className="pb-3 border-b border-border/60 flex flex-col sm:flex-row sm:items-center justify-between gap-3">
        <div>
          <div className="flex items-center gap-2">
            <CardTitle className="text-lg font-bold flex items-center gap-2 text-content">
              <Zap className="w-5 h-5 text-accent" />
              Statistical Anomaly & Flow Intelligence
            </CardTitle>
            {displayDemo && (
              <Badge variant="gold" size="sm">
                DEMO DATA
              </Badge>
            )}
            <Badge variant={anomalies.length > 0 ? "gold" : "gain"} size="md">
              {anomalies.length > 0 ? `${anomalies.length} DEVIATIONS` : "CLEAN BASELINE"}
            </Badge>
          </div>

          <CardDescription className="text-xs text-content-muted">
            Isolation Forest multivariate deviations, z-score volume bursts, and intraday spread expansion
          </CardDescription>
        </div>

        <div className="flex items-center gap-2 self-end sm:self-center">
          <Link href="/anomalies">
            <Button variant="outline" size="sm" rightIcon={<ArrowRight className="w-3.5 h-3.5" />}>
              Inspect Systemic Feed
            </Button>
          </Link>
          <button
            onClick={() => refresh()}
            className="p-1.5 rounded-lg text-content-muted hover:text-content hover:bg-surface-subtle transition-colors"
            title="Refresh Anomalies"
          >
            <RefreshCw className="w-3.5 h-3.5" />
          </button>
        </div>
      </CardHeader>

      <CardContent className="pt-4 space-y-4">
        {/* Real-time Flow / Spike Highlights */}
        {volumeSpike && (
          <div className="p-3 bg-surface-subtle rounded-xl border border-border flex flex-wrap items-center justify-between gap-3 text-xs">
            <div className="flex items-center gap-2">
              <span className="w-2 h-2 rounded-full bg-primary" />
              <span className="font-semibold text-content">Volume Flow Dynamics:</span>
              <span className="text-content-muted">
                Z-Score: <strong className="text-content font-tabular">{volumeSpike.z_score !== undefined ? `${volumeSpike.z_score}σ` : "Normal"}</strong>
              </span>
            </div>
            <div className="flex items-center gap-3">
              <span className="text-content-muted">
                20D Volume Ratio: <strong className="text-content font-tabular">{volumeSpike.volume_ratio ? `${volumeSpike.volume_ratio}x` : "1.0x"}</strong>
              </span>
              <Badge variant={volumeSpike.is_spike ? "gold" : "neutral"} size="sm">
                {volumeSpike.is_spike ? "BURST DETECTED" : "NORMAL FLOW"}
              </Badge>
            </div>
          </div>
        )}

        {/* Anomalies List / Table */}
        {anomalies.length > 0 ? (
          <div className="space-y-2.5">
            {anomalies.map((anom, idx) => (
              <div
                key={idx}
                className="p-3.5 rounded-xl bg-surface border border-border hover:border-accent/40 transition-colors shadow-sm flex flex-col sm:flex-row sm:items-center justify-between gap-3"
              >
                <div className="space-y-1">
                  <div className="flex items-center gap-2">
                    {getSeverityBadge(anom.severity_score, anom.severity)}
                    <span className="text-xs font-extrabold text-content tracking-wide">
                      {anom.anomaly_type?.replace("_", " ") || "MULTIVARIATE DEVIATION"}
                    </span>
                    <span className="text-[11px] text-content-muted font-tabular">
                      • {new Date(anom.timestamp).toLocaleDateString([], { month: "short", day: "numeric" })} {new Date(anom.timestamp).toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" })}
                    </span>
                  </div>
                  <p className="text-xs text-content-muted leading-relaxed">
                    {anom.summary || "Multivariate statistical deviation detected via Isolation Forest."}
                  </p>
                </div>

                <div className="flex items-center justify-between sm:justify-end gap-3 font-tabular text-xs flex-shrink-0">
                  {anom.metrics?.volume_zscore !== undefined && (
                    <div className="text-right">
                      <span className="text-[10px] text-content-muted block">Vol Z-Score</span>
                      <span className="font-bold text-primary">{anom.metrics.volume_zscore}σ</span>
                    </div>
                  )}
                  {anom.metrics?.log_return_pct !== undefined && (
                    <div className="text-right">
                      <span className="text-[10px] text-content-muted block">Intraday Shock</span>
                      <span className={cn("font-bold", anom.metrics.log_return_pct >= 0 ? "text-financial-gain" : "text-financial-loss")}>
                        {anom.metrics.log_return_pct >= 0 ? "+" : ""}{anom.metrics.log_return_pct}%
                      </span>
                    </div>
                  )}
                  <Link href="/anomalies">
                    <Button variant="ghost" size="sm" className="text-primary hover:text-primary-dark">
                      Inspect →
                    </Button>
                  </Link>
                </div>
              </div>
            ))}
          </div>
        ) : (
          <div className="p-6 text-center rounded-xl bg-surface-subtle/50 border border-dashed border-border space-y-1.5">
            <CheckCircle2 className="w-6 h-6 text-financial-gain mx-auto" />
            <p className="text-xs font-bold text-content">No active statistical anomalies detected</p>
            <p className="text-[11px] text-content-muted">
              Trading behavior across volume, price return acceleration, and volatility bands aligns with normal distributions.
            </p>
          </div>
        )}
      </CardContent>
    </Card>
  );
};
