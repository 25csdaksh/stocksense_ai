"use client";

import React from "react";
import { Card, CardHeader, CardTitle, CardDescription, CardContent } from "@/components/common/Card";
import { Badge } from "@/components/common/Badge";
import { formatPercent } from "@/lib/utils";
import { ConcentrationMetrics } from "@/types";
import { Globe, Layers, Building2, ShieldCheck, Network } from "lucide-react";

export interface PortfolioDiversificationProps {
  holdingsCount: number;
  sectorCount: number;
  concentration: ConcentrationMetrics;
  averageCorrelation: number;
}

export const PortfolioDiversification: React.FC<PortfolioDiversificationProps> = ({
  holdingsCount,
  sectorCount,
  concentration,
  averageCorrelation,
}) => {
  const enc = concentration.hhi_index > 0 ? (10000 / concentration.hhi_index).toFixed(1) : holdingsCount.toString();

  const metrics = [
    {
      label: "Total Holdings",
      value: `${holdingsCount} Stocks`,
      sub: "Active individual equities",
      icon: <Layers className="w-4 h-4 text-primary" />,
    },
    {
      label: "Sector Breadth",
      value: `${sectorCount} Sectors`,
      sub: `Leading: ${concentration.largest_sector_name}`,
      icon: <Building2 className="w-4 h-4 text-secondary" />,
    },
    {
      label: "Top Holding Weight",
      value: formatPercent(concentration.top_1_weight_pct),
      sub: concentration.top_1_ticker,
      icon: <ShieldCheck className="w-4 h-4 text-accent" />,
    },
    {
      label: "Avg Asset Correlation",
      value: `+${averageCorrelation.toFixed(2)}`,
      sub: "Mean pairwise synchronicity",
      icon: <Network className="w-4 h-4 text-primary-dark" />,
    },
    {
      label: "Effective Constituents (ENC)",
      value: `${enc} Eq. Stocks`,
      sub: "HHI-weighted effective depth",
      icon: <Globe className="w-4 h-4 text-content" />,
    },
  ];

  return (
    <Card>
      <CardHeader className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-2 pb-2">
        <div>
          <div className="flex items-center gap-2">
            <CardTitle className="flex items-center gap-2">
              <Globe className="w-4 h-4 text-primary" />
              Portfolio Diversification Structure
            </CardTitle>
            <Badge variant="neutral" size="sm">
              Multi-Sector
            </Badge>
          </div>
          <CardDescription>
            Quantitative balance across asset count, sector dispersion, and effective breadth.
          </CardDescription>
        </div>
      </CardHeader>

      <CardContent>
        <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-5 gap-3">
          {metrics.map((m, idx) => (
            <div
              key={idx}
              className="p-3 bg-surface-subtle/60 rounded-xl border border-border space-y-1 hover:bg-surface-subtle transition-all"
            >
              <div className="flex items-center justify-between text-content-muted">
                <span className="text-[11px] font-semibold truncate">{m.label}</span>
                {m.icon}
              </div>
              <div className="text-base font-bold text-content font-tabular">{m.value}</div>
              <div className="text-[10px] text-content-muted truncate">{m.sub}</div>
            </div>
          ))}
        </div>
      </CardContent>
    </Card>
  );
};
