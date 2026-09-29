"use client";

import React from "react";
import {
  ResponsiveContainer,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  Tooltip,
  CartesianGrid,
  ReferenceLine,
} from "recharts";
import { DistributionBin } from "@/types";

interface DistributionChartProps {
  data: DistributionBin[];
  var95?: number;
  height?: number;
}

export default function DistributionChart({ data, var95 = -8.5, height = 280 }: DistributionChartProps) {
  if (!data || data.length === 0) return null;

  return (
    <div className="w-full bg-white p-4 rounded-xl border border-border shadow-sm">
      <div className="flex items-center justify-between mb-3">
        <div>
          <h4 className="text-sm font-bold text-slate-900">Empirical Return Distribution</h4>
          <p className="text-xs text-slate-500">Simulated Terminal Return Density & Value-at-Risk</p>
        </div>
        <div className="flex items-center gap-2 font-mono text-xs">
          <span className="w-2.5 h-2.5 rounded-full bg-financial-loss inline-block"></span>
          <span className="text-slate-600 font-semibold">VaR 95%: {var95.toFixed(2)}%</span>
        </div>
      </div>

      <div style={{ width: "100%", height }}>
        <ResponsiveContainer>
          <BarChart data={data} margin={{ top: 10, right: 10, left: -10, bottom: 0 }}>
            <CartesianGrid strokeDasharray="3 3" stroke="#F1F5F9" vertical={false} />
            <XAxis
              dataKey="midpoint"
              tick={{ fill: "#64748B", fontSize: 10 }}
              tickLine={false}
              axisLine={{ stroke: "#E2E8F0" }}
              tickFormatter={(v) => `${v}%`}
            />
            <YAxis
              tick={{ fill: "#64748B", fontSize: 10 }}
              tickLine={false}
              axisLine={{ stroke: "#E2E8F0" }}
            />
            <Tooltip
              contentStyle={{
                backgroundColor: "#FFFFFF",
                borderColor: "#E2E8F0",
                borderRadius: "8px",
                fontSize: "12px",
              }}
              formatter={(value: any, name: string) => [value, "Path Frequency"]}
              labelFormatter={(label) => `Return ~ ${label}%`}
            />
            <ReferenceLine
              x={Number(var95.toFixed(1))}
              stroke="#D32F2F"
              strokeDasharray="4 4"
              strokeWidth={2}
              label={{ value: "VaR 95%", fill: "#D32F2F", fontSize: 10, position: "top" }}
            />
            <Bar dataKey="frequency" fill="#0A4D3C" radius={[4, 4, 0, 0]} opacity={0.85} />
          </BarChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
}
