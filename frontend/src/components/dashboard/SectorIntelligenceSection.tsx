"use client";

import React from "react";
import { useSectors } from "@/hooks/useSectors";
import { Card, CardHeader, CardTitle, CardContent } from "@/components/common/Card";
import { Badge } from "@/components/common/Badge";
import { Skeleton } from "@/components/common/Skeleton";
import { formatPercent } from "@/lib/utils";
import { PieChart, TrendingUp, TrendingDown, Layers } from "lucide-react";

export const SectorIntelligenceSection: React.FC = () => {
  const { sectors, isLoading, isDemo } = useSectors();

  // Sort sectors by performance descending
  const sortedSectors = [...sectors].sort((a, b) => b.performance_pct - a.performance_pct);

  return (
    <Card className="border-border shadow-card">
      <CardHeader className="pb-3 border-b border-border flex flex-row items-center justify-between">
        <div className="flex items-center gap-2">
          <div className="p-1.5 rounded-lg bg-secondary/10 text-secondary">
            <PieChart className="w-4 h-4" />
          </div>
          <div>
            <CardTitle className="text-base font-bold text-content flex items-center gap-2">
              Sector Intelligence & Rotation
              {isDemo && (
                <Badge variant="gold" size="sm">
                  DEMO DATA
                </Badge>
              )}
            </CardTitle>
            <p className="text-xs text-content-muted mt-0.5">
              Relative performance, momentum scoring & market cap distribution
            </p>
          </div>
        </div>

        <span className="text-[11px] text-content-muted font-mono hidden sm:inline-block">
          Descriptive analytics only
        </span>
      </CardHeader>

      <CardContent className="p-4 sm:p-5">
        {isLoading ? (
          <div className="space-y-3">
            {[1, 2, 3, 4, 5].map((i) => (
              <Skeleton key={i} variant="text" className="h-10 w-full rounded-lg" />
            ))}
          </div>
        ) : (
          <div className="space-y-2.5">
            {sortedSectors.map((sec) => {
              const isPositive = sec.performance_pct >= 0;
              const momentumNorm = Math.min(100, Math.max(0, sec.momentum_score));

              return (
                <div
                  key={sec.sector}
                  className="p-3 rounded-xl bg-surface-subtle/50 hover:bg-surface border border-border/80 hover:border-primary/20 transition-all flex flex-col sm:flex-row sm:items-center justify-between gap-3"
                >
                  {/* Left: Sector Name & Top Contributor */}
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center gap-2">
                      <Layers className="w-3.5 h-3.5 text-primary shrink-0" />
                      <span className="text-xs sm:text-sm font-bold text-content truncate">
                        {sec.sector}
                      </span>
                      <span className="text-[10px] px-1.5 py-0.2 rounded bg-surface border border-border text-content-muted font-mono shrink-0">
                        Weight: {sec.market_cap_weight}%
                      </span>
                    </div>
                    <p className="text-[11px] text-content-muted mt-0.5 pl-5.5">
                      Lead driver: <span className="font-semibold text-content font-mono">{sec.top_stock}</span>
                    </p>
                  </div>

                  {/* Middle: Momentum Progress Bar */}
                  <div className="w-full sm:w-36 shrink-0 space-y-1">
                    <div className="flex justify-between text-[10px] font-mono text-content-muted">
                      <span>Momentum</span>
                      <span className="font-semibold text-primary">{sec.momentum_score.toFixed(1)}/100</span>
                    </div>
                    <div className="w-full h-1.5 bg-border rounded-full overflow-hidden">
                      <div
                        className="h-full bg-gradient-to-r from-secondary to-accent rounded-full transition-all duration-500"
                        style={{ width: `${momentumNorm}%` }}
                      />
                    </div>
                  </div>

                  {/* Right: Performance % */}
                  <div className="flex sm:flex-col items-center sm:items-end justify-between sm:justify-center shrink-0">
                    <div
                      className={`flex items-center gap-1 text-xs font-bold font-mono ${
                        isPositive ? "text-gain" : "text-loss"
                      }`}
                    >
                      {isPositive ? (
                        <TrendingUp className="w-3.5 h-3.5" />
                      ) : (
                        <TrendingDown className="w-3.5 h-3.5" />
                      )}
                      <span>{isPositive ? "+" : ""}{formatPercent(sec.performance_pct)}</span>
                    </div>
                    <span className="text-[10px] text-content-muted font-mono">1-Day Relative</span>
                  </div>
                </div>
              );
            })}

            <p className="text-[11px] text-content-muted text-center pt-2 italic">
              Sector momentum and performance rankings are generated strictly from historical price/volume distributions.
            </p>
          </div>
        )}
      </CardContent>
    </Card>
  );
};
