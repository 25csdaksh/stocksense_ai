"use client";

import React from "react";
import {
  ResponsiveContainer,
  RadarChart as RechartsRadar,
  PolarGrid,
  PolarAngleAxis,
  PolarRadiusAxis,
  Radar,
  Tooltip,
} from "recharts";

export interface FactorScore {
  factor: string;
  score: number;
  benchmark?: number;
}

export interface StockRadarChartProps {
  factors: {
    value: number;
    growth: number;
    quality: number;
    momentum: number;
    volatility: number;
  };
  benchmarkFactors?: {
    value: number;
    growth: number;
    quality: number;
    momentum: number;
    volatility: number;
  };
  height?: number;
  className?: string;
}

export const StockRadarChart: React.FC<StockRadarChartProps> = ({
  factors,
  benchmarkFactors,
  height = 300,
  className,
}) => {
  const data: FactorScore[] = [
    { factor: "Value", score: factors.value, benchmark: benchmarkFactors?.value ?? 50 },
    { factor: "Growth", score: factors.growth, benchmark: benchmarkFactors?.growth ?? 50 },
    { factor: "Quality", score: factors.quality, benchmark: benchmarkFactors?.quality ?? 50 },
    { factor: "Momentum", score: factors.momentum, benchmark: benchmarkFactors?.momentum ?? 50 },
    { factor: "Low Volatility", score: 100 - factors.volatility, benchmark: benchmarkFactors ? 100 - benchmarkFactors.volatility : 50 },
  ];

  return (
    <div className={className} style={{ width: "100%", height }}>
      <ResponsiveContainer width="100%" height="100%">
        <RechartsRadar cx="50%" cy="50%" outerRadius="75%" data={data}>
          <PolarGrid stroke="#E3E7E3" />
          <PolarAngleAxis dataKey="factor" tick={{ fill: "#17211B", fontSize: 11, fontWeight: 600 }} />
          <PolarRadiusAxis angle={30} domain={[0, 100]} tick={{ fill: "#6B756E", fontSize: 9 }} />
          <Tooltip
            content={({
              active,
              payload,
            }: {
              active?: boolean;
              payload?: Array<{ payload: FactorScore }>;
            }) => {
              if (active && payload && payload.length) {
                const item = payload[0].payload;
                return (
                  <div className="bg-surface border border-border p-2.5 rounded-lg shadow-dropdown">
                    <p className="text-xs font-bold text-content">{item.factor}</p>
                    <p className="text-xs font-semibold text-primary mt-1">
                      Score: <span className="font-tabular font-bold">{item.score}/100</span>
                    </p>
                  </div>
                );
              }
              return null;
            }}
          />
          <Radar
            name="Stock DNA"
            dataKey="score"
            stroke="#12372A"
            fill="#12372A"
            fillOpacity={0.4}
          />
          {benchmarkFactors && (
            <Radar
              name="Benchmark"
              dataKey="benchmark"
              stroke="#C9A227"
              fill="#C9A227"
              fillOpacity={0.15}
            />
          )}
        </RechartsRadar>
      </ResponsiveContainer>
    </div>
  );
};
