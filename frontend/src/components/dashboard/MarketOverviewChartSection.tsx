"use client";

import React from "react";
import { useMarketChart, Timeframe } from "@/hooks/useMarketChart";
import { Card, CardHeader, CardTitle, CardContent } from "@/components/common/Card";
import { CandlestickChart } from "@/components/charts/CandlestickChart";
import { Skeleton } from "@/components/common/Skeleton";
import { Badge } from "@/components/common/Badge";
import { formatNumber, formatPercent } from "@/lib/utils";
import { BarChart2, TrendingUp, TrendingDown } from "lucide-react";

const TIMEFRAMES: Timeframe[] = ["1D", "1W", "1M", "3M", "6M", "1Y"];

const BENCHMARK_SELECTORS = [
  { ticker: "^NSEI", label: "NIFTY 50" },
  { ticker: "^BSESN", label: "SENSEX" },
  { ticker: "^NSEBANK", label: "NIFTY BANK" },
  { ticker: "RELIANCE.NS", label: "RELIANCE" },
  { ticker: "TCS.NS", label: "TCS" },
];

export const MarketOverviewChartSection: React.FC = () => {
  const { ticker, setTicker, timeframe, setTimeframe, historyData, isLoading, isDemo } =
    useMarketChart("^NSEI");

  const latestBar = historyData[historyData.length - 1];
  const firstBar = historyData[0];
  const netChange = latestBar && firstBar ? latestBar.close - firstBar.open : 0;
  const netChangePct =
    latestBar && firstBar && firstBar.open > 0
      ? (netChange / firstBar.open) * 100
      : 0;
  const isPositive = netChange >= 0;

  return (
    <Card className="border-border shadow-card">
      <CardHeader className="pb-3 flex flex-col md:flex-row md:items-center justify-between gap-3 border-b border-border">
        {/* Left Ticker & Active Selection */}
        <div className="flex flex-wrap items-center gap-2">
          <div className="flex items-center gap-2">
            <div className="p-1.5 rounded-lg bg-primary/10 text-primary">
              <BarChart2 className="w-4 h-4" />
            </div>
            <div>
              <CardTitle className="text-base font-bold text-content flex items-center gap-2">
                Market Structure Overview
                {isDemo && (
                  <Badge variant="gold" size="sm">
                    DEMO DATA
                  </Badge>
                )}
              </CardTitle>
            </div>
          </div>

          {/* Ticker Quick Switchers */}
          <div className="flex items-center bg-surface-subtle p-0.5 rounded-lg border border-border ml-0 sm:ml-2">
            {BENCHMARK_SELECTORS.map((item) => (
              <button
                key={item.ticker}
                onClick={() => setTicker(item.ticker)}
                className={`px-2.5 py-1 text-xs font-semibold rounded-md transition-all ${
                  ticker === item.ticker
                    ? "bg-surface text-primary shadow-xs border border-border"
                    : "text-content-muted hover:text-content"
                }`}
              >
                {item.label}
              </button>
            ))}
          </div>
        </div>

        {/* Right Timeframe Selectors */}
        <div className="flex items-center gap-1 bg-surface-subtle p-1 rounded-lg border border-border">
          {TIMEFRAMES.map((tf) => (
            <button
              key={tf}
              onClick={() => setTimeframe(tf)}
              className={`px-2.5 py-1 text-xs font-semibold rounded-md transition-all ${
                timeframe === tf
                  ? "bg-primary text-white shadow-xs"
                  : "text-content-muted hover:text-content hover:bg-surface/50"
              }`}
            >
              {tf}
            </button>
          ))}
        </div>
      </CardHeader>

      <CardContent className="p-4 sm:p-5">
        {/* Metric Bar */}
        {latestBar && (
          <div className="flex flex-wrap items-center justify-between gap-4 mb-4 pb-3 border-b border-border/60">
            <div className="flex items-baseline gap-3">
              <span className="text-2xl font-bold font-mono text-content">
                {formatNumber(latestBar.close)}
              </span>
              <div
                className={`flex items-center gap-1 text-xs font-bold font-mono ${
                  isPositive ? "text-gain" : "text-loss"
                }`}
              >
                {isPositive ? <TrendingUp className="w-3.5 h-3.5" /> : <TrendingDown className="w-3.5 h-3.5" />}
                <span>{isPositive ? "+" : ""}{formatNumber(netChange)}</span>
                <span>({isPositive ? "+" : ""}{formatPercent(netChangePct)})</span>
                <span className="text-content-muted font-normal ml-1">in {timeframe}</span>
              </div>
            </div>

            {/* High / Low / Volume Stats */}
            <div className="flex flex-wrap items-center gap-4 text-xs font-mono">
              <div>
                <span className="text-content-muted text-[11px] block">O</span>
                <span className="font-semibold text-content">{formatNumber(latestBar.open)}</span>
              </div>
              <div>
                <span className="text-content-muted text-[11px] block">H</span>
                <span className="font-semibold text-gain">{formatNumber(latestBar.high)}</span>
              </div>
              <div>
                <span className="text-content-muted text-[11px] block">L</span>
                <span className="font-semibold text-loss">{formatNumber(latestBar.low)}</span>
              </div>
              <div>
                <span className="text-content-muted text-[11px] block">Vol</span>
                <span className="font-semibold text-content">
                  {latestBar.volume > 10000000
                    ? `${(latestBar.volume / 10000000).toFixed(2)} Cr`
                    : `${(latestBar.volume / 100000).toFixed(1)} L`}
                </span>
              </div>
            </div>
          </div>
        )}

        {/* Chart Canvas */}
        {isLoading ? (
          <Skeleton variant="card" className="h-[380px] w-full rounded-xl" />
        ) : (
          <div className="w-full h-[380px]">
            <CandlestickChart data={historyData} height={380} />
          </div>
        )}
      </CardContent>
    </Card>
  );
};
