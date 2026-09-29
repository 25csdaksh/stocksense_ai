"use client";

import React from "react";
import { useMarketIndices } from "@/hooks/useMarketIndices";
import { Card, CardContent } from "@/components/common/Card";
import { Badge } from "@/components/common/Badge";
import { Button } from "@/components/common/Button";
import { Skeleton } from "@/components/common/Skeleton";
import { ErrorState } from "@/components/common/ErrorState";
import { formatNumber, formatPercent } from "@/lib/utils";
import { TrendingUp, TrendingDown, RefreshCw, Activity } from "lucide-react";

export const MarketIndicesSection: React.FC = () => {
  const { indices, marketStatus, isLoading, isError, isDemo, lastUpdated, refresh } =
    useMarketIndices();

  if (isLoading) {
    return (
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        {[1, 2, 3, 4].map((i) => (
          <Skeleton key={i} variant="card" className="h-28" />
        ))}
      </div>
    );
  }

  if (isError && indices.length === 0) {
    return (
      <ErrorState
        title="Market Data Feed Unavailable"
        message="Unable to reach the Indian Market exchange feed. Click below to retry."
        onRetry={refresh}
      />
    );
  }

  return (
    <div className="space-y-3">
      {/* Header Bar */}
      <div className="flex flex-wrap items-center justify-between gap-2">
        <div className="flex items-center gap-2.5">
          <h2 className="text-base font-bold text-content flex items-center gap-2">
            <Activity className="w-4 h-4 text-primary" />
            Market Benchmarks
          </h2>
          <span className="flex items-center gap-1.5 text-xs font-semibold px-2 py-0.5 rounded-full bg-gain/10 text-gain">
            <span className="w-1.5 h-1.5 rounded-full bg-gain animate-pulse" />
            {marketStatus?.is_open !== false ? "NSE/BSE Open" : "Market Closed"}
          </span>
          {isDemo && (
            <Badge variant="gold" size="sm">
              DEMO DATA
            </Badge>
          )}
        </div>

        <div className="flex items-center gap-2 text-xs text-content-muted">
          {lastUpdated && (
            <span>Updated {lastUpdated.toLocaleTimeString([], { hour: "2-digit", minute: "2-digit", second: "2-digit" })}</span>
          )}
          <Button
            variant="ghost"
            size="sm"
            onClick={refresh}
            className="h-7 px-2 text-xs text-content-muted hover:text-primary"
            leftIcon={<RefreshCw className="w-3.5 h-3.5" />}
          >
            Refresh
          </Button>
        </div>
      </div>

      {/* Index Cards Grid */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        {indices.map((idx) => {
          const isPositive = idx.change >= 0;
          return (
            <Card
              key={idx.symbol}
              hover
              className="border-border hover:border-primary/30 transition-all duration-200"
            >
              <CardContent className="p-4 flex flex-col justify-between h-full">
                <div className="flex items-center justify-between mb-2">
                  <div>
                    <span className="text-xs font-bold text-content-muted uppercase tracking-wider">
                      {idx.name}
                    </span>
                    <p className="text-[11px] text-content-muted/80 font-mono">{idx.symbol}</p>
                  </div>
                  <div
                    className={`p-1.5 rounded-lg ${
                      isPositive ? "bg-gain/10 text-gain" : "bg-loss/10 text-loss"
                    }`}
                  >
                    {isPositive ? (
                      <TrendingUp className="w-4 h-4" />
                    ) : (
                      <TrendingDown className="w-4 h-4" />
                    )}
                  </div>
                </div>

                <div className="flex items-baseline justify-between mt-1">
                  <span className="text-xl font-bold font-mono tracking-tight text-content">
                    {formatNumber(idx.price)}
                  </span>
                  <div
                    className={`flex items-center text-xs font-semibold font-mono ${
                      isPositive ? "text-gain" : "text-loss"
                    }`}
                  >
                    <span>{isPositive ? "+" : ""}{formatNumber(idx.change)}</span>
                    <span className="ml-1.5 px-1.5 py-0.5 rounded bg-surface-subtle">
                      {isPositive ? "+" : ""}{formatPercent(idx.change_pct)}
                    </span>
                  </div>
                </div>
              </CardContent>
            </Card>
          );
        })}
      </div>
    </div>
  );
};
