"use client";

import React from "react";
import { useStockDNA } from "@/hooks/useStockDNA";
import { StockRadarChart } from "@/components/charts/RadarChart";
import { Card, CardHeader, CardTitle, CardDescription, CardContent } from "@/components/common/Card";
import { Badge } from "@/components/common/Badge";
import { Skeleton } from "@/components/common/Skeleton";
import { Button } from "@/components/common/Button";
import { Brain, Sparkles, AlertCircle, RefreshCw, Layers } from "lucide-react";
import { cn } from "@/lib/utils";

export interface StockDNASectionProps {
  ticker: string;
  isDemo?: boolean;
}

export const StockDNASection: React.FC<StockDNASectionProps> = ({
  ticker,
  isDemo: parentDemo = false,
}) => {
  const { dna, isLoading, isError, error, isDemo, refresh } = useStockDNA(ticker);

  const displayDemo = parentDemo || isDemo;

  if (isLoading) {
    return (
      <Card className="border-border">
        <CardHeader>
          <Skeleton className="h-6 w-48" />
          <Skeleton className="h-4 w-72" />
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            <Skeleton className="h-64 rounded-xl" />
            <Skeleton className="h-64 rounded-xl" />
          </div>
        </CardContent>
      </Card>
    );
  }

  if (isError || !dna) {
    return (
      <Card className="border-border">
        <CardContent className="py-8 text-center space-y-3">
          <AlertCircle className="w-8 h-8 text-financial-loss mx-auto" />
          <p className="text-sm font-semibold text-content">Unable to load Stock DNA Profile</p>
          <p className="text-xs text-content-muted">{error || "Server response unavailable"}</p>
          <Button variant="outline" size="sm" onClick={() => refresh()}>
            Retry
          </Button>
        </CardContent>
      </Card>
    );
  }

  const scores = dna.factor_scores || {
    value: 50,
    growth: 50,
    quality: 50,
    momentum: 50,
    volatility: 50,
  };

  const factorList = [
    { label: "VALUE", score: Math.round(scores.value || 0), desc: "Earnings yield & book value multiple discount" },
    { label: "GROWTH", score: Math.round(scores.growth || 0), desc: "Topline revenue & net operating profit expansion" },
    { label: "QUALITY", score: Math.round(scores.quality || 0), desc: "High ROE, capital efficiency & low leverage" },
    { label: "MOMENTUM", score: Math.round(scores.momentum || 0), desc: "6-12 month price strength & benchmark alpha" },
    { label: "LOW VOLATILITY", score: Math.round(100 - (scores.volatility || 50)), desc: "Beta stability & drawdown resistance" },
  ];

  return (
    <Card className="border-border shadow-card">
      <CardHeader className="pb-3 border-b border-border/60 flex flex-col sm:flex-row sm:items-center justify-between gap-3">
        <div>
          <div className="flex items-center gap-2">
            <CardTitle className="text-lg font-bold flex items-center gap-2 text-content">
              <Brain className="w-5 h-5 text-primary" />
              5-Factor Quantitative Stock DNA
            </CardTitle>
            {displayDemo && (
              <Badge variant="gold" size="sm">
                DEMO DATA
              </Badge>
            )}
            <Badge variant="primary" size="md">
              {dna.dominant_persona || "Multi-Factor Compounder"}
            </Badge>
          </div>
          <CardDescription className="text-xs text-content-muted">
            Fama-French inspired multi-factor quantitative style breakdown
          </CardDescription>
        </div>

        <button
          onClick={() => refresh()}
          className="p-1.5 self-end sm:self-center rounded-lg text-content-muted hover:text-content hover:bg-surface-subtle transition-colors"
          title="Refresh Stock DNA"
        >
          <RefreshCw className="w-3.5 h-3.5" />
        </button>
      </CardHeader>

      <CardContent className="pt-4">
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-6 items-center">
          {/* Left: Recharts Radar Chart */}
          <div className="lg:col-span-6 flex flex-col items-center justify-center p-2 bg-surface-subtle/30 rounded-2xl border border-border/60">
            <StockRadarChart
              factors={{
                value: scores.value || 50,
                growth: scores.growth || 50,
                quality: scores.quality || 50,
                momentum: scores.momentum || 50,
                volatility: scores.volatility || 50,
              }}
              benchmarkFactors={{
                value: 50,
                growth: 50,
                quality: 50,
                momentum: 50,
                volatility: 50,
              }}
              height={280}
            />
            <div className="flex items-center gap-4 text-[11px] text-content-muted mt-2 font-medium">
              <span className="flex items-center gap-1.5">
                <span className="w-2.5 h-2.5 bg-primary rounded-sm inline-block" />
                {ticker} DNA
              </span>
              <span className="flex items-center gap-1.5">
                <span className="w-2.5 h-2.5 bg-accent rounded-sm inline-block" />
                NSE Universe Benchmark
              </span>
            </div>
          </div>

          {/* Right: Factor Metric Rows & Summary */}
          <div className="lg:col-span-6 space-y-4">
            <div className="space-y-2.5">
              {factorList.map((f) => (
                <div key={f.label} className="space-y-1">
                  <div className="flex justify-between items-center text-xs font-bold font-tabular">
                    <span className="text-content tracking-wide">{f.label}</span>
                    <span className="text-primary">{f.score} / 100</span>
                  </div>
                  {/* Progress bar */}
                  <div className="w-full bg-surface-subtle h-2 rounded-full overflow-hidden border border-border-subtle">
                    <div
                      className={cn(
                        "h-full rounded-full transition-all duration-500",
                        f.score >= 70 ? "bg-primary" : f.score >= 40 ? "bg-secondary" : "bg-accent"
                      )}
                      style={{ width: `${Math.min(100, Math.max(5, f.score))}%` }}
                    />
                  </div>
                </div>
              ))}
            </div>

            {/* Factual Explanation Box */}
            <div className="p-3.5 bg-surface-subtle/80 rounded-xl border border-border space-y-1 text-xs text-content-muted">
              <p className="font-semibold text-content text-[11px] uppercase tracking-wider">
                Persona Profile: {dna.dominant_persona}
              </p>
              <p className="leading-relaxed">
                {dna.summary || "Factor scores summarize the available quantitative characteristics across valuation, profitability, balance sheet quality, and market momentum."}
              </p>
              <p className="text-[10px] text-content-muted italic pt-1">
                Factor scores summarize the available quantitative characteristics. Not an investment recommendation.
              </p>
            </div>
          </div>
        </div>
      </CardContent>
    </Card>
  );
};
