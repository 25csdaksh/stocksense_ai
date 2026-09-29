"use client";

import React from "react";
import { AggregateSentimentStats } from "@/hooks/useNewsSentiment";
import { Gauge, TrendingUp, TrendingDown, Minus } from "lucide-react";
import { Badge } from "@/components/common/Badge";

interface NewsSentimentOverviewProps {
  stats: AggregateSentimentStats;
  isLoading: boolean;
}

export const NewsSentimentOverview: React.FC<NewsSentimentOverviewProps> = ({
  stats,
  isLoading,
}) => {
  if (isLoading) {
    return (
      <div className="bg-surface p-5 rounded-2xl border border-border shadow-card h-64 animate-pulse" />
    );
  }

  const regimeVariant =
    stats.overallRegime === "BULLISH"
      ? "gain"
      : stats.overallRegime === "BEARISH"
      ? "loss"
      : "primary";

  return (
    <div className="bg-surface p-5 rounded-2xl border border-border shadow-card space-y-4">
      <div className="flex items-center justify-between border-b border-border pb-3">
        <div className="flex items-center gap-2">
          <Gauge className="w-4 h-4 text-primary" />
          <h3 className="text-xs font-bold text-content uppercase tracking-wider">
            Aggregate Sentiment Monitor
          </h3>
        </div>
        <Badge variant={regimeVariant} size="sm">
          {stats.overallRegime} REGIME
        </Badge>
      </div>

      {/* Quick Score */}
      <div className="flex items-center justify-between p-3 bg-surface-subtle rounded-xl border border-border">
        <div>
          <span className="text-[10px] text-content-muted uppercase font-semibold">Mean Polarity Score</span>
          <p className="text-lg font-bold text-content font-tabular mt-0.5">
            {stats.averageScore > 0 ? `+` : ``}{stats.averageScore.toFixed(3)}
          </p>
        </div>
        <span className="text-xs text-content-muted font-medium">[-1.000 to +1.000 Scale]</span>
      </div>

      {/* Distribution Counts */}
      <div className="grid grid-cols-3 gap-2 text-center">
        <div className="p-2.5 rounded-xl bg-financial-gain/10 border border-financial-gain/20 space-y-0.5">
          <span className="text-[10px] font-bold text-financial-gain uppercase">Positive</span>
          <p className="text-base font-bold text-financial-gain font-tabular">{stats.positivePct}%</p>
          <span className="text-[10px] text-content-muted font-tabular">({stats.positiveCount} articles)</span>
        </div>

        <div className="p-2.5 rounded-xl bg-surface-subtle border border-border space-y-0.5">
          <span className="text-[10px] font-bold text-content-muted uppercase">Neutral</span>
          <p className="text-base font-bold text-content font-tabular">{stats.neutralPct}%</p>
          <span className="text-[10px] text-content-muted font-tabular">({stats.neutralCount} articles)</span>
        </div>

        <div className="p-2.5 rounded-xl bg-financial-loss/10 border border-financial-loss/20 space-y-0.5">
          <span className="text-[10px] font-bold text-financial-loss uppercase">Negative</span>
          <p className="text-base font-bold text-financial-loss font-tabular">{stats.negativePct}%</p>
          <span className="text-[10px] text-content-muted font-tabular">({stats.negativeCount} articles)</span>
        </div>
      </div>

      {/* Sentiment Stacked Bar */}
      <div className="space-y-1">
        <div className="w-full bg-border/40 h-2 rounded-full overflow-hidden flex">
          <div className="bg-financial-gain h-full" style={{ width: `${stats.positivePct}%` }} />
          <div className="bg-content-muted/40 h-full" style={{ width: `${stats.neutralPct}%` }} />
          <div className="bg-financial-loss h-full" style={{ width: `${stats.negativePct}%` }} />
        </div>
        <div className="flex justify-between text-[10px] text-content-muted">
          <span>Bullish Flow</span>
          <span>Bearish Flow</span>
        </div>
      </div>
    </div>
  );
};
