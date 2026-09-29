"use client";

import React from "react";
import {
  ResponsiveContainer,
  AreaChart,
  Area,
  Line,
  XAxis,
  YAxis,
  Tooltip,
  CartesianGrid,
} from "recharts";
import { Card, CardHeader, CardTitle, CardDescription, CardContent } from "@/components/common/Card";
import { Badge } from "@/components/common/Badge";
import { formatCurrency, formatPercent } from "@/lib/utils";
import {
  usePortfolioPerformance,
  PerformanceTimeframe,
} from "@/hooks/usePortfolioPerformance";
import { TrendingUp, ShieldCheck, BarChart3, Activity } from "lucide-react";

export interface PortfolioPerformanceProps {
  currentTotalValue: number;
  totalCost: number;
}

const TIMEFRAMES: PerformanceTimeframe[] = ["1W", "1M", "3M", "6M", "1Y", "ALL"];

export const PortfolioPerformance: React.FC<PortfolioPerformanceProps> = ({
  currentTotalValue,
  totalCost,
}) => {
  const {
    timeframe,
    setTimeframe,
    chartData,
    returnPct,
    benchmarkReturnPct,
    maxDrawdownPct,
  } = usePortfolioPerformance(currentTotalValue, totalCost);

  const alpha = Number((returnPct - benchmarkReturnPct).toFixed(2));

  return (
    <Card className="overflow-hidden">
      <CardHeader className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-3">
        <div>
          <div className="flex items-center gap-2">
            <CardTitle className="flex items-center gap-2">
              <BarChart3 className="w-4 h-4 text-primary" />
              Portfolio Performance &amp; Benchmark Relative Alpha
            </CardTitle>
            <Badge variant="neutral" size="sm" className="text-[10px] uppercase font-bold tracking-wider">
              Model-Derived Metric
            </Badge>
          </div>
          <CardDescription>
            Cumulative equity trajectory compared against NIFTY 50 total return benchmark.
          </CardDescription>
        </div>

        {/* Timeframe Buttons */}
        <div className="flex items-center gap-1 bg-surface-subtle p-1 rounded-lg border border-border">
          {TIMEFRAMES.map((tf) => (
            <button
              key={tf}
              onClick={() => setTimeframe(tf)}
              className={`px-2.5 py-1 text-xs font-semibold rounded transition-all ${
                timeframe === tf
                  ? "bg-primary text-white shadow-xs"
                  : "text-content-muted hover:text-content hover:bg-surface"
              }`}
            >
              {tf}
            </button>
          ))}
        </div>
      </CardHeader>

      <CardContent className="space-y-4">
        {/* Performance Metric Summary Bar */}
        <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 p-3 bg-surface-subtle/50 rounded-xl border border-border">
          <div>
            <span className="text-[11px] text-content-muted font-medium block">Portfolio Return</span>
            <span className="text-base font-bold font-tabular text-financial-gain flex items-center gap-1">
              <TrendingUp className="w-3.5 h-3.5" />
              {formatPercent(returnPct)}
            </span>
          </div>

          <div>
            <span className="text-[11px] text-content-muted font-medium block">NIFTY 50 Benchmark</span>
            <span className="text-base font-bold font-tabular text-content-muted flex items-center gap-1">
              <Activity className="w-3.5 h-3.5" />
              {formatPercent(benchmarkReturnPct)}
            </span>
          </div>

          <div>
            <span className="text-[11px] text-content-muted font-medium block">Excess Alpha (α)</span>
            <span
              className={`text-base font-bold font-tabular ${
                alpha >= 0 ? "text-financial-gain" : "text-financial-loss"
              }`}
            >
              {alpha >= 0 ? `+${alpha}%` : `${alpha}%`}
            </span>
          </div>

          <div>
            <span className="text-[11px] text-content-muted font-medium block">Period Max Drawdown</span>
            <span className="text-base font-bold font-tabular text-financial-loss flex items-center gap-1">
              <ShieldCheck className="w-3.5 h-3.5" />
              {formatPercent(maxDrawdownPct)}
            </span>
          </div>
        </div>

        {/* Legend Indicator Bar */}
        <div className="flex items-center justify-end gap-4 text-xs font-medium text-content-muted pt-1">
          <div className="flex items-center gap-1.5">
            <span className="w-2.5 h-2.5 rounded-full bg-primary" />
            <span className="text-content font-semibold">Portfolio Equity</span>
          </div>
          <div className="flex items-center gap-1.5">
            <span className="w-2.5 h-0.5 bg-slate-400 border border-slate-400" />
            <span>NIFTY 50 Benchmark</span>
          </div>
        </div>

        {/* Equity Curve Chart */}
        <div className="h-72 w-full">
          <ResponsiveContainer width="100%" height="100%">
            <AreaChart data={chartData} margin={{ top: 10, right: 10, left: 0, bottom: 0 }}>
              <defs>
                <linearGradient id="portfolioGrad" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="5%" stopColor="#12372A" stopOpacity={0.25} />
                  <stop offset="95%" stopColor="#12372A" stopOpacity={0.0} />
                </linearGradient>
              </defs>
              <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#E3E7E3" />
              <XAxis
                dataKey="date"
                axisLine={false}
                tickLine={false}
                tick={{ fontSize: 11, fill: "#6B756E" }}
                dy={6}
              />
              <YAxis
                axisLine={false}
                tickLine={false}
                tick={{ fontSize: 11, fill: "#6B756E" }}
                tickFormatter={(v: number) =>
                  formatCurrency(v, "INR", { compact: true, decimals: 1 })
                }
                domain={["auto", "auto"]}
              />
              <Tooltip
                content={({
                  active,
                  payload,
                  label,
                }: {
                  active?: boolean;
                  payload?: Array<{ value: number | string; dataKey: string }>;
                  label?: string;
                }) => {
                  if (active && payload && payload.length) {
                    const portVal = Number(payload.find((p) => p.dataKey === "portfolioValue")?.value || 0);
                    const benchVal = Number(payload.find((p) => p.dataKey === "benchmarkValue")?.value || 0);
                    return (
                      <div className="bg-surface border border-border p-3 rounded-lg shadow-dropdown space-y-1.5">
                        <p className="text-[11px] font-semibold text-content-muted border-b border-border pb-1">
                          {label}
                        </p>
                        <div className="flex items-center justify-between gap-4 text-xs">
                          <span className="flex items-center gap-1.5 font-medium text-primary">
                            <span className="w-2 h-2 rounded-full bg-primary" />
                            Portfolio:
                          </span>
                          <span className="font-bold text-content font-tabular">
                            {formatCurrency(portVal, "INR")}
                          </span>
                        </div>
                        <div className="flex items-center justify-between gap-4 text-xs">
                          <span className="flex items-center gap-1.5 font-medium text-content-muted">
                            <span className="w-2 h-2 rounded-full bg-slate-400" />
                            NIFTY 50 Base:
                          </span>
                          <span className="font-bold text-content-muted font-tabular">
                            {formatCurrency(benchVal, "INR")}
                          </span>
                        </div>
                      </div>
                    );
                  }
                  return null;
                }}
              />
              <Area
                name="Portfolio Equity"
                type="monotone"
                dataKey="portfolioValue"
                stroke="#12372A"
                strokeWidth={2.5}
                fillOpacity={1}
                fill="url(#portfolioGrad)"
              />
              <Line
                name="NIFTY 50 Benchmark"
                type="monotone"
                dataKey="benchmarkValue"
                stroke="#94A3B8"
                strokeWidth={1.75}
                strokeDasharray="4 4"
                dot={false}
              />
            </AreaChart>
          </ResponsiveContainer>
        </div>
      </CardContent>
    </Card>
  );
};
