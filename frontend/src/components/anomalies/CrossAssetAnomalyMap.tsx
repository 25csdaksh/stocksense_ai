"use client";

import React from "react";
import { Card, CardHeader, CardTitle, CardDescription, CardContent } from "@/components/common/Card";
import { Badge } from "@/components/common/Badge";
import { Network, ArrowRight, Zap, AlertTriangle } from "lucide-react";

export interface CrossAssetAnomalyMapProps {
  anomaliesCount: number;
}

const CORRELATION_ANOMALIES = [
  {
    assetA: "INFY.NS",
    assetB: "TCS.NS",
    sector: "Information Technology",
    historicalCorr: 0.84,
    currentCorr: -0.68,
    divergence: "1.52 pts",
    status: "SEVERE_DECOUPLING",
    explanation: "Earnings guidance divergence caused temporary decoupling in pairwise return co-movement.",
  },
  {
    assetA: "HDFCBANK.NS",
    assetB: "ICICIBANK.NS",
    sector: "Banking / Financials",
    historicalCorr: 0.78,
    currentCorr: 0.32,
    divergence: "0.46 pts",
    status: "MODERATE_DIVERGENCE",
    explanation: "Credit deposit ratio positioning triggered asymmetric trading velocity.",
  },
  {
    assetA: "RELIANCE.NS",
    assetB: "NIFTY 50",
    sector: "Benchmark Beta",
    historicalCorr: 0.82,
    currentCorr: 0.94,
    divergence: "+0.12 pts",
    status: "EXCESS_SYNCHRONICITY",
    explanation: "Index heavy-weight concentration driving broader market momentum.",
  },
];

export const CrossAssetAnomalyMap: React.FC<CrossAssetAnomalyMapProps> = ({ anomaliesCount }) => {
  return (
    <Card>
      <CardHeader className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-2 pb-2">
        <div>
          <div className="flex items-center gap-2">
            <CardTitle className="flex items-center gap-2">
              <Network className="w-4 h-4 text-primary" />
              Cross-Asset Correlation &amp; Decoupling Map
            </CardTitle>
            <Badge variant="neutral" size="sm">
              Rolling 30D Window
            </Badge>
          </div>
          <CardDescription>
            Unusual correlation breaks, sector de-linkages, and systemic co-movement anomalies.
          </CardDescription>
        </div>
      </CardHeader>

      <CardContent className="space-y-3">
        <div className="space-y-2.5">
          {CORRELATION_ANOMALIES.map((pair, idx) => {
            const isSevere = pair.status === "SEVERE_DECOUPLING";

            return (
              <div
                key={idx}
                className="p-3.5 bg-surface-subtle/70 rounded-xl border border-border hover:bg-surface-subtle transition-all space-y-2"
              >
                <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2">
                  <div className="flex items-center gap-2">
                    <span className="font-bold text-content text-xs">{pair.assetA}</span>
                    <span className="text-content-muted text-xs">↔</span>
                    <span className="font-bold text-content text-xs">{pair.assetB}</span>
                    <Badge variant="neutral" size="sm" className="text-[9px]">
                      {pair.sector}
                    </Badge>
                  </div>

                  <div className="flex items-center gap-3 text-xs">
                    <span className="text-content-muted text-[11px]">
                      Hist: <strong className="text-content font-mono">+{pair.historicalCorr}</strong>
                    </span>
                    <span className="text-content-muted text-[11px]">
                      Spot: <strong className={`font-mono ${pair.currentCorr < 0 ? "text-financial-loss" : "text-content"}`}>{pair.currentCorr > 0 ? `+${pair.currentCorr}` : pair.currentCorr}</strong>
                    </span>
                    <Badge
                      variant={isSevere ? "loss" : "gold"}
                      size="sm"
                      className="font-bold text-[9px]"
                    >
                      {pair.divergence} Break
                    </Badge>
                  </div>
                </div>

                <p className="text-xs text-content-muted leading-relaxed">{pair.explanation}</p>
              </div>
            );
          })}
        </div>
      </CardContent>
    </Card>
  );
};
