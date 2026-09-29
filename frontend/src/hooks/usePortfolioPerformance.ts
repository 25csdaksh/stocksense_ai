"use client";

import { useState, useMemo } from "react";

export type PerformanceTimeframe = "1W" | "1M" | "3M" | "6M" | "1Y" | "ALL";

export interface PerformanceDataPoint {
  date: string;
  portfolioValue: number;
  portfolioReturnPct: number;
  benchmarkValue?: number;
  benchmarkReturnPct?: number;
}

export function usePortfolioPerformance(currentTotalValue: number = 2845200, totalCost: number = 2489600) {
  const [timeframe, setTimeframe] = useState<PerformanceTimeframe>("6M");

  const { chartData, returnPct, benchmarkReturnPct, maxDrawdownPct, annualizedReturnPct } = useMemo(() => {
    const pointsCount =
      timeframe === "1W" ? 7 :
      timeframe === "1M" ? 30 :
      timeframe === "3M" ? 45 :
      timeframe === "6M" ? 60 :
      timeframe === "1Y" ? 90 : 120;

    const daysBack =
      timeframe === "1W" ? 7 :
      timeframe === "1M" ? 30 :
      timeframe === "3M" ? 90 :
      timeframe === "6M" ? 180 :
      timeframe === "1Y" ? 365 : 730;

    const baseReturnPct =
      timeframe === "1W" ? 1.2 :
      timeframe === "1M" ? 3.8 :
      timeframe === "3M" ? 8.4 :
      timeframe === "6M" ? 14.3 :
      timeframe === "1Y" ? 22.6 : 38.4;

    const benchmarkBaseReturn =
      timeframe === "1W" ? 0.7 :
      timeframe === "1M" ? 2.1 :
      timeframe === "3M" ? 5.8 :
      timeframe === "6M" ? 10.9 :
      timeframe === "1Y" ? 16.4 : 26.8;

    const startValue = currentTotalValue / (1 + baseReturnPct / 100);
    const benchmarkStartValue = currentTotalValue / (1 + benchmarkBaseReturn / 100);

    const now = new Date();
    const data: PerformanceDataPoint[] = [];

    let peakValue = startValue;
    let maxDd = 0;

    for (let i = 0; i < pointsCount; i++) {
      const progress = i / (pointsCount - 1);
      const pointDate = new Date(now.getTime() - (daysBack * (1 - progress)) * 24 * 60 * 60 * 1000);
      
      // Deterministic smooth curve with realistic financial volatility
      const cycleA = Math.sin(progress * Math.PI * 3.5) * 0.025;
      const cycleB = Math.cos(progress * Math.PI * 7) * 0.015;
      const drift = progress * (baseReturnPct / 100);
      
      const val = i === pointsCount - 1
        ? currentTotalValue
        : Math.round(startValue * (1 + drift + cycleA + cycleB));

      if (val > peakValue) peakValue = val;
      const dd = ((val - peakValue) / peakValue) * 100;
      if (dd < maxDd) maxDd = dd;

      const benchDrift = progress * (benchmarkBaseReturn / 100);
      const benchCycle = Math.sin(progress * Math.PI * 2.8) * 0.018;
      const benchVal = i === pointsCount - 1
        ? Math.round(benchmarkStartValue * (1 + benchmarkBaseReturn / 100))
        : Math.round(benchmarkStartValue * (1 + benchDrift + benchCycle));

      const portRet = Number((((val - startValue) / startValue) * 100).toFixed(2));
      const benchRet = Number((((benchVal - benchmarkStartValue) / benchmarkStartValue) * 100).toFixed(2));

      const formattedDate = pointDate.toLocaleDateString("en-IN", {
        month: "short",
        day: "numeric",
        year: timeframe === "1Y" || timeframe === "ALL" ? "2-digit" : undefined,
      });

      data.push({
        date: formattedDate,
        portfolioValue: val,
        portfolioReturnPct: portRet,
        benchmarkValue: benchVal,
        benchmarkReturnPct: benchRet,
      });
    }

    const annualized = daysBack > 0 ? (baseReturnPct / (daysBack / 365)) : baseReturnPct;

    return {
      chartData: data,
      returnPct: baseReturnPct,
      benchmarkReturnPct: benchmarkBaseReturn,
      maxDrawdownPct: Number(maxDd.toFixed(2)),
      annualizedReturnPct: Number(annualized.toFixed(2)),
    };
  }, [timeframe, currentTotalValue]);

  return {
    timeframe,
    setTimeframe,
    chartData,
    returnPct,
    benchmarkReturnPct,
    maxDrawdownPct,
    annualizedReturnPct,
    isModelDerived: true,
  };
}
