"use client";

import React, { useState } from "react";
import { MonteCarloResponse, DistributionBin } from "@/types";
import { formatNumber } from "@/lib/utils";
import { BarChart2, TrendingUp, TrendingDown, Percent } from "lucide-react";

interface ScenarioDistributionChartProps {
  data: MonteCarloResponse | null;
  isLoading: boolean;
}

export const ScenarioDistributionChart: React.FC<ScenarioDistributionChartProps> = ({
  data,
  isLoading,
}) => {
  const [hoveredBin, setHoveredBin] = useState<DistributionBin | null>(null);

  if (isLoading || !data || !data.distribution_histogram || data.distribution_histogram.length === 0) {
    return null;
  }

  const maxFrequency = Math.max(...data.distribution_histogram.map((b) => b.frequency), 1);

  return (
    <div className="bg-surface p-5 rounded-2xl border border-border shadow-card space-y-4">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2 border-b border-border pb-3">
        <div className="flex items-center gap-2">
          <BarChart2 className="w-4 h-4 text-primary" />
          <h3 className="text-sm font-bold text-content uppercase tracking-wider">
            Terminal Return Distribution (Monte Carlo Histogram)
          </h3>
        </div>
        <span className="text-[11px] text-content-muted">
          {data.distribution_histogram.length} Frequency Bins Across {data.iterations.toLocaleString()} Paths
        </span>
      </div>

      {/* Probabilities Row */}
      <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
        <div className="p-3 bg-surface-subtle/70 rounded-xl border border-border flex items-center justify-between">
          <div>
            <span className="text-[10px] text-content-muted uppercase font-semibold">Probability of Profit</span>
            <p className="text-base font-bold text-financial-gain font-tabular mt-0.5">
              {data.probability_of_profit_pct.toFixed(1)}%
            </p>
          </div>
          <TrendingUp className="w-5 h-5 text-financial-gain/70" />
        </div>

        <div className="p-3 bg-surface-subtle/70 rounded-xl border border-border flex items-center justify-between">
          <div>
            <span className="text-[10px] text-content-muted uppercase font-semibold">Loss &gt; 10% Probability</span>
            <p className="text-base font-bold text-financial-loss font-tabular mt-0.5">
              {data.prob_loss_exceeding_10pct.toFixed(1)}%
            </p>
          </div>
          <TrendingDown className="w-5 h-5 text-financial-loss/70" />
        </div>

        <div className="p-3 bg-surface-subtle/70 rounded-xl border border-border flex items-center justify-between">
          <div>
            <span className="text-[10px] text-content-muted uppercase font-semibold">Gain &gt; 20% Probability</span>
            <p className="text-base font-bold text-primary font-tabular mt-0.5">
              {data.prob_gain_exceeding_20pct.toFixed(1)}%
            </p>
          </div>
          <Percent className="w-5 h-5 text-primary/70" />
        </div>
      </div>

      {/* Histogram Display */}
      <div className="space-y-2 pt-2">
        <div className="h-48 flex items-end gap-1 sm:gap-1.5 w-full px-2 pt-6 pb-1 bg-surface-subtle/40 rounded-xl border border-border relative">
          {hoveredBin && (
            <div className="absolute top-2 left-4 bg-surface border border-border px-3 py-1 rounded-lg shadow-dropdown text-xs z-10">
              <span className="font-semibold text-content">{hoveredBin.range_label}: </span>
              <span className="font-bold text-primary font-tabular">
                {hoveredBin.frequency.toLocaleString()} paths ({((hoveredBin.frequency / data.iterations) * 100).toFixed(1)}%)
              </span>
            </div>
          )}

          {data.distribution_histogram.map((bin, idx) => {
            const heightPct = Math.max(4, (bin.frequency / maxFrequency) * 100);
            const isPositive = bin.midpoint >= 0;

            return (
              <div
                key={idx}
                className="flex-1 h-full flex flex-col justify-end items-center group relative cursor-pointer"
                onMouseEnter={() => setHoveredBin(bin)}
                onMouseLeave={() => setHoveredBin(null)}
              >
                <div
                  className={`w-full rounded-t transition-all duration-200 group-hover:opacity-100 ${
                    isPositive
                      ? "bg-primary group-hover:bg-[#2F5D50]"
                      : "bg-[#E05252] group-hover:bg-[#B91C1C]"
                  }`}
                  style={{
                    height: `${heightPct}%`,
                    opacity: hoveredBin === bin ? 1 : 0.85,
                  }}
                />
              </div>
            );
          })}
        </div>

        {/* X-Axis Labels */}
        <div className="flex justify-between text-[10px] text-content-muted font-tabular px-2">
          <span>{data.distribution_histogram[0]?.range_label.split(" to ")[0]}</span>
          <span>Return Range (0.0% Break-even)</span>
          <span>{data.distribution_histogram[data.distribution_histogram.length - 1]?.range_label.split(" to ")[1]}</span>
        </div>
      </div>
    </div>
  );
};
