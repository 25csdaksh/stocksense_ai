"use client";

import React from "react";
import { Card, CardHeader, CardTitle, CardDescription, CardContent } from "@/components/common/Card";
import { CorrelationHeatmap } from "@/components/charts/CorrelationHeatmap";
import { Badge } from "@/components/common/Badge";
import { usePortfolioCorrelation } from "@/hooks/usePortfolioCorrelation";
import { Network, RefreshCw } from "lucide-react";

export interface PortfolioCorrelationProps {
  tickers: string[];
}

export const PortfolioCorrelation: React.FC<PortfolioCorrelationProps> = ({ tickers }) => {
  const {
    method,
    setMethod,
    displayTickers,
    displayMatrix,
    highestPair,
    lowestPair,
    averageCorrelation,
    isLoading,
  } = usePortfolioCorrelation(tickers);

  const hasData = displayTickers.length >= 2 && displayMatrix.length >= 2;

  return (
    <Card>
      <CardHeader className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-3 pb-2">
        <div>
          <div className="flex items-center gap-2">
            <CardTitle className="flex items-center gap-2">
              <Network className="w-4 h-4 text-primary" />
              Intra-Portfolio Correlation Matrix
            </CardTitle>
            <Badge variant="neutral" size="sm" className="font-mono text-[10px] uppercase">
              {method}
            </Badge>
          </div>
          <CardDescription>
            Pairwise rolling co-movement across portfolio constituents.
          </CardDescription>
        </div>

        {/* Method Toggle */}
        <div className="flex items-center gap-1 bg-surface-subtle p-1 rounded-lg border border-border">
          <button
            onClick={() => setMethod("pearson")}
            className={`px-2.5 py-1 text-xs font-semibold rounded transition-all ${
              method === "pearson"
                ? "bg-primary text-white shadow-xs"
                : "text-content-muted hover:text-content hover:bg-surface"
            }`}
          >
            Pearson
          </button>
          <button
            onClick={() => setMethod("spearman")}
            className={`px-2.5 py-1 text-xs font-semibold rounded transition-all ${
              method === "spearman"
                ? "bg-primary text-white shadow-xs"
                : "text-content-muted hover:text-content hover:bg-surface"
            }`}
          >
            Spearman (Rank)
          </button>
        </div>
      </CardHeader>

      <CardContent className="space-y-4">
        {isLoading ? (
          <div className="h-48 flex items-center justify-center text-xs text-content-muted gap-2">
            <RefreshCw className="w-4 h-4 animate-spin text-primary" />
            Computing pairwise correlation matrix...
          </div>
        ) : !hasData ? (
          <div className="p-8 text-center bg-surface-subtle/50 rounded-xl border border-dashed border-border text-xs text-content-muted">
            Insufficient historical data to compute multi-asset correlation matrix.
          </div>
        ) : (
          <>
            {/* Pair highlights summary */}
            <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
              <div className="p-3 bg-surface-subtle/70 rounded-xl border border-border space-y-1">
                <span className="text-[10px] uppercase font-bold text-content-muted tracking-wider block">
                  Highest Correlated Pair
                </span>
                <div className="flex items-center justify-between">
                  <span className="text-xs font-bold text-content truncate">
                    {highestPair.pair[0]} &amp; {highestPair.pair[1]}
                  </span>
                  <span className="text-xs font-bold font-tabular text-financial-gain">
                    +{highestPair.correlation.toFixed(2)}
                  </span>
                </div>
                <p className="text-[10px] text-content-muted truncate">{highestPair.description}</p>
              </div>

              <div className="p-3 bg-surface-subtle/70 rounded-xl border border-border space-y-1">
                <span className="text-[10px] uppercase font-bold text-content-muted tracking-wider block">
                  Lowest / Buffer Pair
                </span>
                <div className="flex items-center justify-between">
                  <span className="text-xs font-bold text-content truncate">
                    {lowestPair.pair[0]} &amp; {lowestPair.pair[1]}
                  </span>
                  <span className="text-xs font-bold font-tabular text-primary">
                    +{lowestPair.correlation.toFixed(2)}
                  </span>
                </div>
                <p className="text-[10px] text-content-muted truncate">{lowestPair.description}</p>
              </div>

              <div className="p-3 bg-surface-subtle/70 rounded-xl border border-border space-y-1">
                <span className="text-[10px] uppercase font-bold text-content-muted tracking-wider block">
                  Average Intra Correlation
                </span>
                <div className="flex items-center justify-between">
                  <span className="text-xs font-bold text-content">Portfolio Mean</span>
                  <span className="text-xs font-bold font-tabular text-content">
                    +{averageCorrelation.toFixed(2)}
                  </span>
                </div>
                <p className="text-[10px] text-content-muted">
                  Cross-asset mean correlation across {displayTickers.length} holdings
                </p>
              </div>
            </div>

            {/* Matrix Heatmap */}
            <CorrelationHeatmap
              tickers={displayTickers}
              matrix={displayMatrix}
              className="mt-2"
            />
          </>
        )}
      </CardContent>
    </Card>
  );
};
