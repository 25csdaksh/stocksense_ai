"use client";

import React from "react";
import { cn } from "@/lib/utils";

export interface CorrelationHeatmapProps {
  tickers: string[];
  matrix: number[][];
  className?: string;
}

export const CorrelationHeatmap: React.FC<CorrelationHeatmapProps> = ({
  tickers,
  matrix,
  className,
}) => {
  const getColor = (val: number): string => {
    if (val === 1) return "bg-primary text-white font-bold";
    if (val >= 0.7) return "bg-primary/80 text-white";
    if (val >= 0.4) return "bg-secondary/60 text-white";
    if (val >= 0.1) return "bg-primary-light text-primary";
    if (val >= -0.1) return "bg-surface-subtle text-content";
    if (val >= -0.4) return "bg-accent-light text-accent-dark";
    return "bg-financial-loss-bg text-financial-loss font-semibold";
  };

  return (
    <div className={cn("overflow-x-auto border border-border rounded-xl bg-surface p-4", className)}>
      <div className="inline-block min-w-full">
        <table className="border-collapse text-center text-xs">
          <thead>
            <tr>
              <th className="p-2 border-b border-r border-border bg-surface-subtle" />
              {tickers.map((t) => (
                <th
                  key={t}
                  className="p-2.5 font-bold text-content border-b border-border bg-surface-subtle/50 text-[11px]"
                >
                  {t}
                </th>
              ))}
            </tr>
          </thead>
          <tbody>
            {tickers.map((rowTicker, rIdx) => (
              <tr key={rowTicker}>
                <td className="p-2.5 font-bold text-content text-left border-r border-border bg-surface-subtle/50 text-[11px]">
                  {rowTicker}
                </td>
                {tickers.map((_, cIdx) => {
                  const val = matrix[rIdx]?.[cIdx] ?? 0;
                  return (
                    <td
                      key={`${rIdx}-${cIdx}`}
                      className={cn(
                        "p-2.5 border border-border-subtle font-tabular transition-transform hover:scale-105 select-none",
                        getColor(val)
                      )}
                      title={`Correlation (${rowTicker}, ${tickers[cIdx]}): ${val.toFixed(2)}`}
                    >
                      {val.toFixed(2)}
                    </td>
                  );
                })}
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
};
