"use client";

import React from "react";
import {
  ResponsiveContainer,
  AreaChart,
  Area,
  XAxis,
  YAxis,
  Tooltip,
  CartesianGrid,
} from "recharts";
import { MonteCarloResponse } from "@/types";
import { formatCurrency, formatNumber } from "@/lib/utils";
import { HelpCircle, Activity } from "lucide-react";

interface MonteCarloSimulationProps {
  data: MonteCarloResponse | null;
  isLoading: boolean;
}

export const MonteCarloSimulation: React.FC<MonteCarloSimulationProps> = ({ data, isLoading }) => {
  if (isLoading) {
    return (
      <div className="bg-surface p-6 rounded-2xl border border-border shadow-card h-96 flex flex-col items-center justify-center space-y-3">
        <div className="w-8 h-8 border-2 border-primary border-t-transparent rounded-full animate-spin" />
        <p className="text-xs text-content-muted">Executing 5,000+ stochastic price trajectories...</p>
      </div>
    );
  }

  if (!data || !data.fan_chart || data.fan_chart.length === 0) {
    return (
      <div className="bg-surface p-6 rounded-2xl border border-border shadow-card h-96 flex items-center justify-center text-xs text-content-muted">
        No Monte Carlo simulation data available. Configure parameters and click "Run Scenario".
      </div>
    );
  }

  return (
    <div className="bg-surface p-5 rounded-2xl border border-border shadow-card space-y-4">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2 border-b border-border pb-3">
        <div>
          <div className="flex items-center gap-2">
            <Activity className="w-4 h-4 text-primary" />
            <h3 className="text-sm font-bold text-content uppercase tracking-wider">
              Stochastic Fan Chart (Merton Jump Diffusion)
            </h3>
          </div>
          <p className="text-[11px] text-content-muted mt-0.5">
            {data.iterations.toLocaleString()} simulated paths over {data.days} trading days with Poisson jump dynamics.
          </p>
        </div>

        <div className="flex items-center gap-1.5 text-[11px] text-content-muted bg-surface-subtle px-2.5 py-1 rounded-lg border border-border">
          <HelpCircle className="w-3.5 h-3.5 text-secondary" />
          <span>Quantile Bands: p10 (Bearish) to p90 (Bullish)</span>
        </div>
      </div>

      {/* Quick Summary Strip */}
      <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
        <div className="p-3 bg-surface-subtle/70 rounded-xl border border-border">
          <span className="text-[10px] text-content-muted uppercase font-semibold">Initial Asset Price</span>
          <p className="text-sm font-bold text-content font-tabular mt-0.5">
            {formatCurrency(data.initial_price, "INR")}
          </p>
        </div>

        <div className="p-3 bg-surface-subtle/70 rounded-xl border border-border">
          <span className="text-[10px] text-content-muted uppercase font-semibold">Terminal P50 (Median)</span>
          <p className="text-sm font-bold text-primary font-tabular mt-0.5">
            {formatCurrency(data.expected_terminal_price_p50, "INR")}
          </p>
        </div>

        <div className="p-3 bg-surface-subtle/70 rounded-xl border border-border">
          <span className="text-[10px] text-content-muted uppercase font-semibold">Terminal P10 (Downside)</span>
          <p className="text-sm font-bold text-financial-loss font-tabular mt-0.5">
            {formatCurrency(data.terminal_p10_price, "INR")}
          </p>
        </div>

        <div className="p-3 bg-surface-subtle/70 rounded-xl border border-border">
          <span className="text-[10px] text-content-muted uppercase font-semibold">Terminal P90 (Upside)</span>
          <p className="text-sm font-bold text-financial-gain font-tabular mt-0.5">
            {formatCurrency(data.terminal_p90_price, "INR")}
          </p>
        </div>
      </div>

      {/* Fan Chart Recharts Container */}
      <div className="h-80 w-full pt-2">
        <ResponsiveContainer width="100%" height="100%">
          <AreaChart data={data.fan_chart} margin={{ top: 10, right: 10, left: 10, bottom: 0 }}>
            <defs>
              <linearGradient id="p90Gradient" x1="0" y1="0" x2="0" y2="1">
                <stop offset="5%" stopColor="#2F5D50" stopOpacity={0.25} />
                <stop offset="95%" stopColor="#2F5D50" stopOpacity={0.05} />
              </linearGradient>
              <linearGradient id="p75Gradient" x1="0" y1="0" x2="0" y2="1">
                <stop offset="5%" stopColor="#12372A" stopOpacity={0.35} />
                <stop offset="95%" stopColor="#12372A" stopOpacity={0.10} />
              </linearGradient>
            </defs>

            <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#E3E7E3" />

            <XAxis
              dataKey="day"
              tickLine={false}
              axisLine={false}
              tick={{ fontSize: 11, fill: "#6B756E" }}
              tickFormatter={(v: number) => `Day ${v}`}
            />

            <YAxis
              tickLine={false}
              axisLine={false}
              tick={{ fontSize: 11, fill: "#6B756E" }}
              domain={["auto", "auto"]}
              tickFormatter={(v: number) => `₹${formatNumber(v, { compact: true })}`}
            />

            <Tooltip
              content={({
                active,
                payload,
                label,
              }: {
                active?: boolean;
                payload?: Array<{ value: number | string; name: string; color: string }>;
                label?: string;
              }) => {
                if (active && payload && payload.length) {
                  return (
                    <div className="bg-surface border border-border p-3 rounded-xl shadow-dropdown text-xs space-y-1">
                      <p className="font-bold text-content border-b border-border pb-1">Day {label}</p>
                      {payload.map((item, idx) => (
                        <div key={idx} className="flex items-center justify-between gap-4">
                          <span className="text-content-muted uppercase text-[10px]" style={{ color: item.color }}>
                            {item.name}:
                          </span>
                          <span className="font-bold font-tabular text-content">
                            {formatCurrency(Number(item.value), "INR")}
                          </span>
                        </div>
                      ))}
                    </div>
                  );
                }
                return null;
              }}
            />

            <Area
              type="monotone"
              dataKey="p90"
              name="p90 (Upper 90th %ile)"
              stroke="#2F5D50"
              strokeWidth={1}
              fillOpacity={1}
              fill="url(#p90Gradient)"
            />

            <Area
              type="monotone"
              dataKey="p75"
              name="p75 (Upper Quartile)"
              stroke="#12372A"
              strokeWidth={1.5}
              fillOpacity={1}
              fill="url(#p75Gradient)"
            />

            <Area
              type="monotone"
              dataKey="p50"
              name="p50 (Median Path)"
              stroke="#C9A227"
              strokeWidth={2.5}
              fillOpacity={0}
            />

            <Area
              type="monotone"
              dataKey="p25"
              name="p25 (Lower Quartile)"
              stroke="#E05252"
              strokeWidth={1.5}
              fillOpacity={0}
            />

            <Area
              type="monotone"
              dataKey="p10"
              name="p10 (Lower 10th %ile)"
              stroke="#B91C1C"
              strokeWidth={1}
              fillOpacity={0}
            />
          </AreaChart>
        </ResponsiveContainer>
      </div>

      {/* Quantile Bands Legend */}
      <div className="flex flex-wrap items-center justify-center gap-4 pt-2 border-t border-border text-[11px] text-content-muted">
        <div className="flex items-center gap-1.5">
          <span className="w-2.5 h-2.5 rounded-full bg-[#2F5D50]" />
          <span>p90 (Upper 90th)</span>
        </div>
        <div className="flex items-center gap-1.5">
          <span className="w-2.5 h-2.5 rounded-full bg-[#12372A]" />
          <span>p75 (Upper Quartile)</span>
        </div>
        <div className="flex items-center gap-1.5">
          <span className="w-2.5 h-2.5 rounded-full bg-[#C9A227]" />
          <span>p50 (Median Drift)</span>
        </div>
        <div className="flex items-center gap-1.5">
          <span className="w-2.5 h-2.5 rounded-full bg-[#E05252]" />
          <span>p25 (Lower Quartile)</span>
        </div>
        <div className="flex items-center gap-1.5">
          <span className="w-2.5 h-2.5 rounded-full bg-[#B91C1C]" />
          <span>p10 (10th Percentile)</span>
        </div>
      </div>
    </div>
  );
};

