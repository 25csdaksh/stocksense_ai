"use client";

import React from "react";
import {
  ResponsiveContainer,
  ComposedChart,
  Area,
  Line,
  XAxis,
  YAxis,
  Tooltip,
  Legend,
  CartesianGrid,
} from "recharts";
import { FanChartPoint } from "@/types";

interface FanChartProps {
  data: FanChartPoint[];
  height?: number;
}

export default function FanChart({ data, height = 360 }: FanChartProps) {
  if (!data || data.length === 0) return <div className="text-sm text-slate-500">No simulation data available</div>;

  return (
    <div className="w-full bg-white p-4 rounded-xl border border-border shadow-sm">
      <div className="flex items-center justify-between mb-4">
        <div>
          <h4 className="text-sm font-bold text-slate-900">Monte Carlo Fan Chart Projection</h4>
          <p className="text-xs text-slate-500">
            10th to 90th percentile trajectories under Merton Jump Diffusion
          </p>
        </div>
        <div className="flex items-center gap-2">
          <span className="px-2 py-0.5 rounded text-[10px] font-mono font-bold bg-emerald-50 text-primary border border-emerald-200">
            P50 MEDIAN PATH
          </span>
        </div>
      </div>

      <div style={{ width: "100%", height }}>
        <ResponsiveContainer>
          <ComposedChart data={data} margin={{ top: 10, right: 20, left: 10, bottom: 0 }}>
            <CartesianGrid strokeDasharray="3 3" stroke="#F1F5F9" />
            <XAxis
              dataKey="day"
              tick={{ fill: "#64748B", fontSize: 11, fontFamily: "Inter" }}
              tickLine={false}
              axisLine={{ stroke: "#E2E8F0" }}
              unit="d"
            />
            <YAxis
              domain={["auto", "auto"]}
              tick={{ fill: "#64748B", fontSize: 11, fontFamily: "Inter" }}
              tickLine={false}
              axisLine={{ stroke: "#E2E8F0" }}
              tickFormatter={(v) => `$${v}`}
            />
            <Tooltip
              contentStyle={{
                backgroundColor: "#FFFFFF",
                borderColor: "#E2E8F0",
                borderRadius: "8px",
                fontSize: "12px",
                boxShadow: "0 4px 6px -1px rgba(0,0,0,0.1)",
              }}
              formatter={(value: any, name: string) => [`$${Number(value).toFixed(2)}`, name.toUpperCase()]}
              labelFormatter={(label) => `Day ${label}`}
            />
            <Legend
              wrapperStyle={{ fontSize: "11px", paddingTop: "10px" }}
              formatter={(value) => <span className="text-slate-600 font-medium">{value}</span>}
            />

            {/* Percentile Bands */}
            <Area
              type="monotone"
              dataKey="p90"
              stroke="none"
              fill="#0A4D3C"
              fillOpacity={0.08}
              name="90th Percentile (Bullish Tail)"
            />
            <Area
              type="monotone"
              dataKey="p75"
              stroke="none"
              fill="#0A4D3C"
              fillOpacity={0.14}
              name="75th Percentile"
            />
            <Area
              type="monotone"
              dataKey="p25"
              stroke="none"
              fill="#0A4D3C"
              fillOpacity={0.14}
              name="25th Percentile"
            />
            <Area
              type="monotone"
              dataKey="p10"
              stroke="none"
              fill="#0A4D3C"
              fillOpacity={0.08}
              name="10th Percentile (Bearish Tail)"
            />

            {/* P50 Median Line */}
            <Line
              type="monotone"
              dataKey="p50"
              stroke="#0A4D3C"
              strokeWidth={2.5}
              dot={false}
              name="P50 Median Path"
            />
          </ComposedChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
}
