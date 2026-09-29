"use client";

import React from "react";
import { ResponsiveContainer, PieChart, Pie, Cell, Tooltip } from "recharts";
import { formatPercent, formatCurrency } from "@/lib/utils";
import { Currency } from "@/types";

export interface AllocationItem {
  name: string;
  value: number;
  weight?: number; // 0 - 100
  color?: string;
}

export interface AllocationChartProps {
  data: AllocationItem[];
  currency?: Currency;
  height?: number;
  className?: string;
}

const DEFAULT_COLORS = [
  "#12372A",
  "#2F5D50",
  "#C9A227",
  "#437B6D",
  "#8E9992",
  "#A38020",
  "#6B756E",
  "#0D824D",
];

export const AllocationChart: React.FC<AllocationChartProps> = ({
  data,
  currency = "INR",
  height = 240,
  className,
}) => {
  return (
    <div className={className} style={{ width: "100%", height }}>
      <ResponsiveContainer width="100%" height="100%">
        <PieChart>
          <Pie
            data={data}
            cx="50%"
            cy="50%"
            innerRadius={60}
            outerRadius={85}
            paddingAngle={2}
            dataKey="value"
          >
            {data.map((entry, index) => (
              <Cell
                key={`cell-${index}`}
                fill={entry.color || DEFAULT_COLORS[index % DEFAULT_COLORS.length]}
                stroke="#FFFFFF"
                strokeWidth={2}
              />
            ))}
          </Pie>
          <Tooltip
            content={({ active, payload }: { active?: boolean; payload?: Array<{ payload: AllocationItem }> }) => {
              if (active && payload && payload.length) {
                const item = payload[0].payload;
                return (
                  <div className="bg-surface border border-border p-2.5 rounded-lg shadow-dropdown">
                    <p className="text-xs font-bold text-content">{item.name}</p>
                    <p className="text-xs font-semibold text-content-muted mt-0.5">
                      {formatCurrency(item.value, currency)} (
                      <span className="text-primary font-bold">
                        {formatPercent(item.weight)}
                      </span>
                      )
                    </p>
                  </div>
                );
              }
              return null;
            }}
          />
        </PieChart>
      </ResponsiveContainer>
    </div>
  );
};
