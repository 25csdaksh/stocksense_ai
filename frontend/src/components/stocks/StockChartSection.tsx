"use client";

import React, { useState } from "react";
import { CandlestickChart } from "@/components/charts/CandlestickChart";
import { useMarketChart, Timeframe } from "@/hooks/useMarketChart";
import { Card, CardHeader, CardTitle, CardDescription, CardContent } from "@/components/common/Card";
import { Badge } from "@/components/common/Badge";
import { Skeleton } from "@/components/common/Skeleton";
import { Button } from "@/components/common/Button";
import { BarChart2, RefreshCw, Layers, SlidersHorizontal, Eye } from "lucide-react";
import { cn } from "@/lib/utils";

export interface StockChartSectionProps {
  ticker: string;
  currency?: string;
  isDemo?: boolean;
}

const TIMEFRAMES: Timeframe[] = ["1D", "1W", "1M", "3M", "6M", "1Y"];

export const StockChartSection: React.FC<StockChartSectionProps> = ({
  ticker,
  currency = "INR",
  isDemo: parentDemo = false,
}) => {
  const { historyData, timeframe, setTimeframe, isLoading, isDemo, refresh } = useMarketChart(ticker);
  const [showOverlays, setShowOverlays] = useState(false);

  const displayDemo = parentDemo || isDemo;

  return (
    <Card className="shadow-card border-border">
      <CardHeader className="pb-3 border-b border-border/60 flex flex-col sm:flex-row sm:items-center justify-between gap-3">
        <div className="space-y-1">
          <div className="flex items-center gap-2">
            <CardTitle className="text-lg font-bold flex items-center gap-2 text-content">
              <BarChart2 className="w-5 h-5 text-primary" />
              Interactive OHLCV Price Action
            </CardTitle>
            {displayDemo && (
              <Badge variant="gold" size="sm">
                DEMO DATA
              </Badge>
            )}
          </div>
          <CardDescription className="text-xs text-content-muted">
            High-frequency candlestick bars and trading volume distribution
          </CardDescription>
        </div>

        {/* Timeframe selector toolbar */}
        <div className="flex items-center gap-1.5 bg-surface-subtle p-1 rounded-xl border border-border">
          {TIMEFRAMES.map((tf) => (
            <button
              key={tf}
              onClick={() => setTimeframe(tf)}
              className={cn(
                "px-3 py-1 text-xs font-bold rounded-lg transition-all",
                timeframe === tf
                  ? "bg-primary text-white shadow-sm"
                  : "text-content-muted hover:text-content hover:bg-surface"
              )}
            >
              {tf}
            </button>
          ))}
          <button
            onClick={() => refresh()}
            className="p-1.5 rounded-lg text-content-muted hover:text-content hover:bg-surface transition-colors ml-1"
            title="Refresh Price History"
            aria-label="Refresh Price History"
          >
            <RefreshCw className={cn("w-3.5 h-3.5", isLoading && "animate-spin text-primary")} />
          </button>
        </div>
      </CardHeader>

      <CardContent className="pt-4 space-y-4">
        {isLoading ? (
          <div className="h-[380px] w-full flex flex-col items-center justify-center space-y-3 bg-surface-subtle/40 rounded-xl">
            <Skeleton className="h-[320px] w-full rounded-xl" />
          </div>
        ) : historyData && historyData.length > 0 ? (
          <div className="space-y-3">
            {/* Lightweight Candlestick Chart */}
            <CandlestickChart data={historyData} height={380} currency={currency} />

            {/* Overlay indicators legend bar */}
            <div className="flex flex-wrap items-center justify-between text-[11px] text-content-muted pt-2 border-t border-border-subtle">
              <div className="flex items-center gap-4">
                <span className="flex items-center gap-1.5 font-medium">
                  <span className="w-2.5 h-2.5 bg-financial-gain rounded-sm inline-block" />
                  Bullish Bar
                </span>
                <span className="flex items-center gap-1.5 font-medium">
                  <span className="w-2.5 h-2.5 bg-financial-loss rounded-sm inline-block" />
                  Bearish Bar
                </span>
                <span className="flex items-center gap-1.5 font-medium">
                  <span className="w-2.5 h-2.5 bg-primary/30 rounded-sm inline-block" />
                  Volume Histogram
                </span>
              </div>

              <div className="text-[11px] font-medium text-content-muted">
                Interval: <span className="font-bold text-content">{timeframe === "1D" ? "15m / 1h" : "1D Daily"}</span> • Points: <span className="font-bold text-content">{historyData.length} bars</span>
              </div>
            </div>
          </div>
        ) : (
          <div className="h-64 flex flex-col items-center justify-center text-center p-6 border border-dashed border-border rounded-xl">
            <p className="text-sm font-semibold text-content">DATA UNAVAILABLE</p>
            <p className="text-xs text-content-muted mt-1">
              Historical OHLCV data is currently unavailable for {ticker}.
            </p>
            <Button variant="outline" size="sm" onClick={() => refresh()} className="mt-3">
              Retry
            </Button>
          </div>
        )}
      </CardContent>
    </Card>
  );
};
