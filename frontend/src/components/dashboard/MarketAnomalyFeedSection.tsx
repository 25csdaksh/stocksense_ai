"use client";

import React from "react";
import Link from "next/link";
import { useAnomalies } from "@/hooks/useAnomalies";
import { Card, CardHeader, CardTitle, CardContent } from "@/components/common/Card";
import { Badge } from "@/components/common/Badge";
import { Button } from "@/components/common/Button";
import { Skeleton } from "@/components/common/Skeleton";
import { AlertTriangle, ArrowRight, Activity, Zap } from "lucide-react";

export const MarketAnomalyFeedSection: React.FC = () => {
  const { anomalies, totalActive, systemicStressIndex, isLoading, isDemo } = useAnomalies();

  const getSeverityBadge = (severityScore: number) => {
    if (severityScore >= 0.85) return <Badge variant="loss" size="sm">CRITICAL</Badge>;
    if (severityScore >= 0.7) return <Badge variant="gold" size="sm">HIGH</Badge>;
    if (severityScore >= 0.4) return <Badge variant="secondary" size="sm">MEDIUM</Badge>;
    return <Badge variant="neutral" size="sm">LOW</Badge>;
  };

  return (
    <Card className="border-border shadow-card">
      <CardHeader className="pb-3 border-b border-border flex flex-row items-center justify-between">
        <div className="flex items-center gap-2">
          <div className="p-1.5 rounded-lg bg-loss/10 text-loss">
            <AlertTriangle className="w-4 h-4" />
          </div>
          <div>
            <CardTitle className="text-base font-bold text-content flex items-center gap-2">
              Univariate & Multivariate Anomaly Feed
              {isDemo && (
                <Badge variant="gold" size="sm">
                  DEMO DATA
                </Badge>
              )}
            </CardTitle>
            <p className="text-xs text-content-muted mt-0.5">
              Isolation Forest, GARCH(1,1) Volatility & Volume Spike Alerts
            </p>
          </div>
        </div>

        {/* Systemic Stress Index */}
        <div className="flex items-center gap-2">
          <div className="hidden sm:flex items-center gap-1.5 px-2.5 py-1 rounded-lg bg-surface-subtle border border-border text-xs font-mono">
            <Activity className="w-3.5 h-3.5 text-primary" />
            <span className="text-content-muted">Stress Index:</span>
            <span className="font-bold text-content">{systemicStressIndex.toFixed(1)}/100</span>
          </div>
          <span className="text-xs font-bold px-2 py-0.5 rounded-full bg-primary/10 text-primary font-mono">
            {totalActive} Active
          </span>
        </div>
      </CardHeader>

      <CardContent className="p-4 sm:p-5">
        {isLoading ? (
          <div className="space-y-3">
            {[1, 2, 3].map((i) => (
              <Skeleton key={i} variant="card" className="h-20 w-full" />
            ))}
          </div>
        ) : anomalies.length === 0 ? (
          <div className="p-8 text-center text-content-muted">
            <p className="text-sm">No systemic anomalies detected across active universe.</p>
          </div>
        ) : (
          <div className="space-y-3">
            {anomalies.map((item, idx) => (
              <div
                key={`${item.ticker}-${idx}`}
                className="p-3.5 rounded-xl bg-surface border border-border/80 hover:border-primary/30 transition-all space-y-2"
              >
                {/* Header: Ticker, Type, Severity & Time */}
                <div className="flex flex-wrap items-center justify-between gap-2">
                  <div className="flex items-center gap-2">
                    <span className="text-xs sm:text-sm font-bold font-mono text-content">
                      {item.ticker}
                    </span>
                    <span className="text-[11px] font-semibold text-primary px-2 py-0.5 rounded bg-primary/5 border border-primary/10 font-mono">
                      {item.anomaly_type.replace(/_/g, " ")}
                    </span>
                    {getSeverityBadge(item.severity_score)}
                  </div>
                  <span className="text-[11px] text-content-muted font-mono">{item.timestamp}</span>
                </div>

                {/* Summary Description */}
                <p className="text-xs sm:text-sm text-content leading-relaxed">
                  {item.summary}
                </p>

                {/* Supporting Metrics Badges */}
                <div className="flex flex-wrap items-center justify-between gap-2 pt-1 border-t border-border/50 text-[11px] font-mono text-content-muted">
                  <div className="flex flex-wrap items-center gap-3">
                    {Object.entries(item.metrics || {}).map(([k, v]) => (
                      <span key={k} className="flex items-center gap-1">
                        <span className="text-content-muted/80">{k.replace(/_/g, " ")}:</span>
                        <span className="font-semibold text-content">
                          {typeof v === "number" ? v.toFixed(2) : String(v)}
                        </span>
                      </span>
                    ))}
                  </div>

                  <Link
                    href={`/anomalies?ticker=${encodeURIComponent(item.ticker)}`}
                    className="inline-flex items-center gap-1 text-primary hover:text-secondary font-semibold transition-colors"
                  >
                    <span>Inspect</span>
                    <ArrowRight className="w-3 h-3" />
                  </Link>
                </div>
              </div>
            ))}

            {/* Footer View Analysis CTA */}
            <div className="pt-2 flex justify-end">
              <Link href="/anomalies">
                <Button
                  variant="outline"
                  size="sm"
                  rightIcon={<ArrowRight className="w-3.5 h-3.5" />}
                >
                  View All Anomalies & Volatility Streams
                </Button>
              </Link>
            </div>
          </div>
        )}
      </CardContent>
    </Card>
  );
};
