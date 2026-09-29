"use client";

import React, { useState } from "react";
import { useStockCorrelations } from "@/hooks/useStockCorrelations";
import { CorrelationHeatmap } from "@/components/charts/CorrelationHeatmap";
import { Card, CardHeader, CardTitle, CardDescription, CardContent } from "@/components/common/Card";
import { Badge } from "@/components/common/Badge";
import { Skeleton } from "@/components/common/Skeleton";
import { Button } from "@/components/common/Button";
import { Network, Link2, GitFork, AlertCircle, RefreshCw } from "lucide-react";
import { cn } from "@/lib/utils";

export interface CorrelationIntelligenceProps {
  ticker: string;
  isDemo?: boolean;
}

export const CorrelationIntelligence: React.FC<CorrelationIntelligenceProps> = ({
  ticker,
  isDemo: parentDemo = false,
}) => {
  const [method, setMethod] = useState<"pearson" | "spearman">("pearson");
  const { correlations, benchmarkCorrelation, isLoading, isError, error, isDemo, refresh } =
    useStockCorrelations(ticker, method);

  const displayDemo = parentDemo || isDemo;

  if (isLoading) {
    return (
      <Card className="border-border">
        <CardHeader>
          <Skeleton className="h-6 w-48" />
          <Skeleton className="h-4 w-72" />
        </CardHeader>
        <CardContent>
          <Skeleton className="h-56 rounded-xl" />
        </CardContent>
      </Card>
    );
  }

  if (isError || !correlations) {
    return (
      <Card className="border-border">
        <CardContent className="py-8 text-center space-y-3">
          <AlertCircle className="w-8 h-8 text-financial-loss mx-auto" />
          <p className="text-sm font-semibold text-content">Unable to load correlation analytics</p>
          <p className="text-xs text-content-muted">{error || "Server response unavailable"}</p>
          <Button variant="outline" size="sm" onClick={() => refresh()}>
            Retry
          </Button>
        </CardContent>
      </Card>
    );
  }

  const { assets, matrix, top_pairs } = correlations;

  return (
    <Card className="border-border shadow-card">
      <CardHeader className="pb-3 border-b border-border/60 flex flex-col sm:flex-row sm:items-center justify-between gap-3">
        <div>
          <div className="flex items-center gap-2">
            <CardTitle className="text-lg font-bold flex items-center gap-2 text-content">
              <Network className="w-5 h-5 text-primary" />
              Cross-Asset Correlation Intelligence
            </CardTitle>
            {displayDemo && (
              <Badge variant="gold" size="sm">
                DEMO DATA
              </Badge>
            )}
            <Badge variant="primary" size="md">
              BENCHMARK ρ: {benchmarkCorrelation.toFixed(2)}
            </Badge>
          </div>
          <CardDescription className="text-xs text-content-muted">
            Rolling daily return co-movements with the NIFTY 50 benchmark and sector peers
          </CardDescription>
        </div>

        {/* Method Switcher */}
        <div className="flex items-center gap-2 self-end sm:self-center">
          <div className="flex items-center bg-surface-subtle p-1 rounded-xl border border-border">
            <button
              onClick={() => setMethod("pearson")}
              className={cn(
                "px-2.5 py-1 text-xs font-bold rounded-lg transition-all",
                method === "pearson"
                  ? "bg-primary text-white"
                  : "text-content-muted hover:text-content"
              )}
            >
              Pearson
            </button>
            <button
              onClick={() => setMethod("spearman")}
              className={cn(
                "px-2.5 py-1 text-xs font-bold rounded-lg transition-all",
                method === "spearman"
                  ? "bg-primary text-white"
                  : "text-content-muted hover:text-content"
              )}
            >
              Spearman Rank
            </button>
          </div>

          <button
            onClick={() => refresh()}
            className="p-1.5 rounded-lg text-content-muted hover:text-content hover:bg-surface-subtle transition-colors"
            title="Refresh Correlations"
          >
            <RefreshCw className="w-3.5 h-3.5" />
          </button>
        </div>
      </CardHeader>

      <CardContent className="pt-4 space-y-4">
        {/* Heatmap & Key Relationship Pairs */}
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-5 items-start">
          {/* Heatmap */}
          <div className="lg:col-span-8">
            <CorrelationHeatmap tickers={assets} matrix={matrix} />
          </div>

          {/* Top Correlation Relationships */}
          <div className="lg:col-span-4 space-y-3">
            <div className="p-3.5 rounded-xl bg-surface-subtle/70 border border-border space-y-2">
              <span className="text-xs font-bold text-content flex items-center gap-1.5">
                <Link2 className="w-4 h-4 text-primary" />
                Strongest Co-Movements
              </span>
              <p className="text-[11px] text-content-muted">
                Empirical pairs displaying highest directional synchronization in the 90-day window:
              </p>

              <div className="space-y-2 pt-1 font-tabular text-xs">
                {top_pairs && top_pairs.length > 0 ? (
                  top_pairs.slice(0, 4).map((p, idx) => (
                    <div
                      key={idx}
                      className="flex items-center justify-between p-2 rounded-lg bg-surface border border-border/80"
                    >
                      <span className="font-semibold text-content text-[11px]">
                        {p.asset_a} ↔ {p.asset_b}
                      </span>
                      <Badge
                        variant={p.correlation >= 0.7 ? "primary" : p.correlation >= 0.4 ? "gold" : "neutral"}
                        size="sm"
                      >
                        ρ = {p.correlation.toFixed(2)}
                      </Badge>
                    </div>
                  ))
                ) : (
                  <p className="text-xs text-content-muted">No high correlation pairs above 0.50 threshold.</p>
                )}
              </div>
            </div>

            <div className="p-3 rounded-xl bg-surface border border-border text-[11px] text-content-muted">
              <span className="font-semibold text-content">Diversification Insight:</span> Assets with correlation &lt; 0.40 provide higher portfolio risk mitigation against systematic market drawdowns.
            </div>
          </div>
        </div>
      </CardContent>
    </Card>
  );
};
