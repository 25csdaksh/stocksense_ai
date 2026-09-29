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
import { formatCurrency, formatNumber } from "@/lib/utils";
import { Currency } from "@/types";

export interface DataPoint {
  date: string;
  value: number;
  secondaryValue?: number;
  [key: string]: string | number | undefined;
}

export interface AreaLineChartProps {
  data: DataPoint[];
  dataKey?: string;
  color?: string;
  currency?: Currency;
  height?: number;
  showGrid?: boolean;
  className?: string;
}

export const AreaLineChart: React.FC<AreaLineChartProps> = ({
  data,
  dataKey = "value",
  color = "#12372A",
  currency = "INR",
  height = 280,
  showGrid = true,
  className,
}) => {
  const gradientId = `area-gradient-${Math.random().toString(36).substring(2, 7)}`;

  return (
    <div className={className} style={{ width: "100%", height }}>
      <ResponsiveContainer width="100%" height="100%">
        <AreaChart data={data} margin={{ top: 10, right: 10, left: 0, bottom: 0 }}>
          <defs>
            <linearGradient id={gradientId} x1="0" y1="0" x2="0" y2="1">
              <stop offset="5%" stopColor={color} stopOpacity={0.25} />
              <stop offset="95%" stopColor={color} stopOpacity={0.0} />
            </linearGradient>
          </defs>
          {showGrid && <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#E3E7E3" />}
          <XAxis
            dataKey="date"
            axisLine={false}
            tickLine={false}
            tick={{ fontSize: 11, fill: "#6B756E" }}
            dy={8}
          />
          <YAxis
            axisLine={false}
            tickLine={false}
            tick={{ fontSize: 11, fill: "#6B756E" }}
            tickFormatter={(val: number) =>
              currency
                ? formatCurrency(val, currency, { compact: true, decimals: 1 })
                : formatNumber(val, { compact: true })
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
              payload?: Array<{ value: number | string }>;
              label?: string;
            }) => {
              if (active && payload && payload.length) {
                const val = Number(payload[0].value);
                return (
                  <div className="bg-surface border border-border p-2.5 rounded-lg shadow-dropdown">
                    <p className="text-[11px] font-semibold text-content-muted">{label}</p>
                    <p className="text-sm font-bold text-content font-tabular mt-0.5">
                      {currency ? formatCurrency(val, currency) : formatNumber(val)}
                    </p>
                  </div>
                );
              }
              return null;
            }}
          />
          <Area
            type="monotone"
            dataKey={dataKey}
            stroke={color}
            strokeWidth={2}
            fillOpacity={1}
            fill={`url(#${gradientId})`}
          />
        </AreaChart>
      </ResponsiveContainer>
    </div>
  );
};
