"use client";

import React, { useState } from "react";
import { Card, CardHeader, CardTitle, CardDescription, CardContent } from "@/components/common/Card";
import { AllocationChart, AllocationItem } from "@/components/charts/AllocationChart";
import { formatCurrency, formatPercent } from "@/lib/utils";
import { PieChart, Layers, Building2, Briefcase } from "lucide-react";

export interface PortfolioAllocationProps {
  stockAllocation: AllocationItem[];
  sectorAllocation: AllocationItem[];
  assetClassAllocation: AllocationItem[];
  totalValue: number;
}

export type AllocationViewMode = "stock" | "sector" | "asset_class";

export const PortfolioAllocation: React.FC<PortfolioAllocationProps> = ({
  stockAllocation,
  sectorAllocation,
  assetClassAllocation,
  totalValue,
}) => {
  const [viewMode, setViewMode] = useState<AllocationViewMode>("stock");

  const currentData =
    viewMode === "stock"
      ? stockAllocation
      : viewMode === "sector"
      ? sectorAllocation
      : assetClassAllocation;

  const topHolding = stockAllocation[0];
  const largestSector = sectorAllocation[0];
  const top3Concentration = stockAllocation
    .slice(0, 3)
    .reduce((acc, item) => acc + (item.weight || 0), 0);

  return (
    <Card className="flex flex-col justify-between">
      <CardHeader className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-3 pb-2">
        <div>
          <CardTitle className="flex items-center gap-2">
            <PieChart className="w-4 h-4 text-primary" />
            Asset & Sector Allocation
          </CardTitle>
          <CardDescription>Capital distribution across holdings and industries</CardDescription>
        </div>

        {/* View Mode Toggle */}
        <div className="flex items-center gap-1 bg-surface-subtle p-1 rounded-lg border border-border">
          <button
            onClick={() => setViewMode("stock")}
            className={`px-2.5 py-1 text-xs font-semibold rounded flex items-center gap-1.5 transition-all ${
              viewMode === "stock"
                ? "bg-primary text-white shadow-xs"
                : "text-content-muted hover:text-content hover:bg-surface"
            }`}
          >
            <Briefcase className="w-3 h-3" />
            By Stock
          </button>
          <button
            onClick={() => setViewMode("sector")}
            className={`px-2.5 py-1 text-xs font-semibold rounded flex items-center gap-1.5 transition-all ${
              viewMode === "sector"
                ? "bg-primary text-white shadow-xs"
                : "text-content-muted hover:text-content hover:bg-surface"
            }`}
          >
            <Building2 className="w-3 h-3" />
            By Sector
          </button>
          <button
            onClick={() => setViewMode("asset_class")}
            className={`px-2.5 py-1 text-xs font-semibold rounded flex items-center gap-1.5 transition-all ${
              viewMode === "asset_class"
                ? "bg-primary text-white shadow-xs"
                : "text-content-muted hover:text-content hover:bg-surface"
            }`}
          >
            <Layers className="w-3 h-3" />
            By Asset Class
          </button>
        </div>
      </CardHeader>

      <CardContent className="space-y-4">
        {/* Top allocation metric callouts */}
        <div className="grid grid-cols-3 gap-2 p-2.5 bg-surface-subtle/60 rounded-xl border border-border text-center">
          <div>
            <span className="text-[10px] text-content-muted block uppercase font-bold tracking-wider">
              Top Holding
            </span>
            <span className="text-xs font-bold text-content truncate block">
              {topHolding ? `${topHolding.name} (${topHolding.weight}%)` : "N/A"}
            </span>
          </div>

          <div className="border-x border-border">
            <span className="text-[10px] text-content-muted block uppercase font-bold tracking-wider">
              Largest Sector
            </span>
            <span className="text-xs font-bold text-content truncate block">
              {largestSector ? `${largestSector.name} (${largestSector.weight}%)` : "N/A"}
            </span>
          </div>

          <div>
            <span className="text-[10px] text-content-muted block uppercase font-bold tracking-wider">
              Top 3 Weight
            </span>
            <span className="text-xs font-bold text-primary block">
              {formatPercent(top3Concentration)}
            </span>
          </div>
        </div>

        {/* Chart + Legend */}
        <div className="grid grid-cols-1 md:grid-cols-12 gap-4 items-center">
          <div className="md:col-span-6 flex justify-center">
            <AllocationChart data={currentData} height={210} />
          </div>

          <div className="md:col-span-6 space-y-2 max-h-56 overflow-y-auto pr-1">
            {currentData.map((item, idx) => (
              <div
                key={`${item.name}-${idx}`}
                className="flex items-center justify-between p-2 rounded-lg hover:bg-surface-subtle transition-colors text-xs border border-transparent hover:border-border"
              >
                <div className="flex items-center gap-2 min-w-0">
                  <span
                    className="w-2.5 h-2.5 rounded-full flex-shrink-0"
                    style={{ backgroundColor: item.color }}
                  />
                  <span className="font-semibold text-content truncate">{item.name}</span>
                </div>
                <div className="flex items-center gap-2 flex-shrink-0">
                  <span className="font-tabular text-content-muted">
                    {formatCurrency(item.value, "INR", { compact: true })}
                  </span>
                  <span className="font-bold text-primary font-tabular w-12 text-right">
                    {formatPercent(item.weight)}
                  </span>
                </div>
              </div>
            ))}
          </div>
        </div>
      </CardContent>
    </Card>
  );
};
