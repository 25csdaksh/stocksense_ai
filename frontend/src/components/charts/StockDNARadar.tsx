"use client";

import React from "react";
import {
  ResponsiveContainer,
  RadarChart,
  PolarGrid,
  PolarAngleAxis,
  PolarRadiusAxis,
  Radar,
  Tooltip,
} from "recharts";
import { StockDNAFactor } from "@/types";

interface StockDNARadarProps {
  data: StockDNAFactor[];
  dominantPersona?: string;
  ticker?: string;
  height?: number;
}

export default function StockDNARadar({
  data,
  dominantPersona = "High Quality Compounder",
  ticker = "EQUITY",
  height = 320,
}: StockDNARadarProps) {
  if (!data || data.length === 0) return <div className="text-xs text-slate-400">No DNA factors calculated</div>;

  return (
    <div className="w-full bg-white p-4 rounded-xl border border-border shadow-sm flex flex-col justify-between">
      <div className="flex items-center justify-between mb-2">
        <div>
          <h4 className="text-sm font-bold text-slate-900">5-Factor Stock DNA Profile</h4>
          <p className="text-xs text-slate-500">{ticker} Quantitative Factor Radar</p>
        </div>
        <span className="px-2 py-0.5 rounded text-[10px] font-bold bg-gold-light text-gold-dark border border-gold-border font-mono uppercase">
          {dominantPersona}
        </span>
      </div>

      <div style={{ width: "100%", height }}>
        <ResponsiveContainer>
          <RadarChart cx="50%" cy="50%" outerRadius="75%" data={data}>
            <PolarGrid stroke="#E2E8F0" />
            <PolarAngleAxis
              dataKey="factor"
              tick={{ fill: "#334155", fontSize: 11, fontWeight: 600, fontFamily: "Inter" }}
            />
            <PolarRadiusAxis angle={30} domain={[0, 100]} stroke="#CBD5E1" tick={{ fontSize: 9 }} />
            <Radar
              name={ticker}
              dataKey="score"
              stroke="#0A4D3C"
              fill="#0A4D3C"
              fillOpacity={0.35}
            />
            <Tooltip
              contentStyle={{
                backgroundColor: "#FFFFFF",
                borderColor: "#E2E8F0",
                borderRadius: "8px",
                fontSize: "12px",
              }}
              formatter={(value: any) => [`${value} / 100`, "Factor Score"]}
            />
          </RadarChart>
        </ResponsiveContainer>
      </div>

      <div className="grid grid-cols-5 gap-1 pt-2 border-t border-slate-100 text-center text-[10px] font-mono">
        {data.map((f) => (
          <div key={f.factor} className="p-1 rounded bg-slate-50">
            <span className="text-slate-600 block truncate">{f.factor}</span>
            <span className="font-bold text-primary">{f.score}</span>
          </div>
        ))}
      </div>
    </div>
  );
}
