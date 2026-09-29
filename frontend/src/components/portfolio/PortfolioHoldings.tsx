"use client";

import React, { useState, useMemo } from "react";
import Link from "next/link";
import { Card, CardHeader, CardTitle, CardDescription, CardContent } from "@/components/common/Card";
import { Badge } from "@/components/common/Badge";
import { formatCurrency, formatPercent } from "@/lib/utils";
import { PortfolioHolding } from "@/types";
import {
  ChevronDown,
  Bookmark,
  BookmarkCheck,
  ExternalLink,
  Search,
  TrendingUp,
  TrendingDown,
  Layers,
} from "lucide-react";

export interface PortfolioHoldingsProps {
  holdings: PortfolioHolding[];
  watchlistTickers: Set<string>;
  onToggleWatchlist: (ticker: string) => void;
  onSelectHolding: (holding: PortfolioHolding) => void;
  isLoading?: boolean;
}

type SortField = "market_value" | "unrealized_pnl" | "unrealized_pnl_pct" | "weight_pct" | "ticker";
type SortDirection = "asc" | "desc";

export const PortfolioHoldings: React.FC<PortfolioHoldingsProps> = ({
  holdings,
  watchlistTickers,
  onToggleWatchlist,
  onSelectHolding,
}) => {
  const [searchQuery, setSearchQuery] = useState<string>("");
  const [sortField, setSortField] = useState<SortField>("market_value");
  const [sortDir, setSortDir] = useState<SortDirection>("desc");

  const handleSort = (field: SortField) => {
    if (sortField === field) {
      setSortDir((prev) => (prev === "asc" ? "desc" : "asc"));
    } else {
      setSortField(field);
      setSortDir("desc");
    }
  };

  const filteredAndSorted = useMemo(() => {
    let list = [...holdings];

    if (searchQuery.trim()) {
      const q = searchQuery.toLowerCase();
      list = list.filter(
        (h) =>
          h.ticker.toLowerCase().includes(q) ||
          (h.company_name && h.company_name.toLowerCase().includes(q)) ||
          (h.sector && h.sector.toLowerCase().includes(q))
      );
    }

    list.sort((a, b) => {
      let valA: number | string = a[sortField] ?? 0;
      let valB: number | string = b[sortField] ?? 0;

      if (typeof valA === "string") {
        return sortDir === "asc"
          ? valA.localeCompare(valB as string)
          : (valB as string).localeCompare(valA);
      }

      return sortDir === "asc" ? (valA as number) - (valB as number) : (valB as number) - (valA as number);
    });

    return list;
  }, [holdings, searchQuery, sortField, sortDir]);

  return (
    <Card className="overflow-hidden">
      <CardHeader className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-3 pb-3">
        <div>
          <div className="flex items-center gap-2">
            <CardTitle className="flex items-center gap-2">
              <Layers className="w-4 h-4 text-primary" />
              Institutional Holdings Intelligence
            </CardTitle>
            <Badge variant="neutral" size="sm">
              {holdings.length} Assets
            </Badge>
          </div>
          <CardDescription>
            Live real-time position tracking, weights, cost basis, and profit distribution.
          </CardDescription>
        </div>

        {/* Search Bar */}
        <div className="relative w-full sm:w-64">
          <Search className="w-4 h-4 text-content-muted absolute left-3 top-1/2 -translate-y-1/2" />
          <input
            type="text"
            placeholder="Search holdings or sector..."
            value={searchQuery}
            onChange={(e: React.ChangeEvent<HTMLInputElement>) => setSearchQuery(e.target.value)}
            className="w-full pl-9 pr-3 py-1.5 text-xs rounded-lg border border-border bg-surface-subtle focus:bg-surface focus:outline-none focus:ring-1 focus:ring-primary text-content transition-all"
          />
        </div>
      </CardHeader>

      <CardContent className="p-0">
        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs border-collapse">
            <thead>
              <tr className="border-b border-border bg-surface-subtle/50 text-content-muted font-semibold">
                <th
                  onClick={() => handleSort("ticker")}
                  className="p-3.5 pl-4 cursor-pointer hover:text-content select-none"
                >
                  <div className="flex items-center gap-1.5">
                    <span>Symbol / Asset</span>
                    <ChevronDown className="w-3 h-3" />
                  </div>
                </th>
                <th className="p-3.5 text-right font-medium">Qty</th>
                <th className="p-3.5 text-right font-medium">Avg Cost</th>
                <th className="p-3.5 text-right font-medium">Spot Price</th>
                <th
                  onClick={() => handleSort("market_value")}
                  className="p-3.5 text-right cursor-pointer hover:text-content select-none"
                >
                  <div className="flex items-center justify-end gap-1.5">
                    <span>Market Value</span>
                    <ChevronDown className="w-3 h-3" />
                  </div>
                </th>
                <th className="p-3.5 text-right font-medium">1-Day Chg</th>
                <th
                  onClick={() => handleSort("unrealized_pnl")}
                  className="p-3.5 text-right cursor-pointer hover:text-content select-none"
                >
                  <div className="flex items-center justify-end gap-1.5">
                    <span>Unrealized P&L</span>
                    <ChevronDown className="w-3 h-3" />
                  </div>
                </th>
                <th
                  onClick={() => handleSort("unrealized_pnl_pct")}
                  className="p-3.5 text-right cursor-pointer hover:text-content select-none"
                >
                  <div className="flex items-center justify-end gap-1.5">
                    <span>Return %</span>
                    <ChevronDown className="w-3 h-3" />
                  </div>
                </th>
                <th
                  onClick={() => handleSort("weight_pct")}
                  className="p-3.5 text-right cursor-pointer hover:text-content select-none"
                >
                  <div className="flex items-center justify-end gap-1.5">
                    <span>Weight</span>
                    <ChevronDown className="w-3 h-3" />
                  </div>
                </th>
                <th className="p-3.5 pr-4 text-center font-medium">Actions</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-border/60">
              {filteredAndSorted.map((holding) => {
                const isGain = (holding.unrealized_pnl ?? 0) >= 0;
                const isInWatchlist = watchlistTickers.has(holding.ticker);

                return (
                  <tr
                    key={holding.ticker}
                    className="hover:bg-surface-subtle/70 transition-colors group cursor-pointer"
                    onClick={() => onSelectHolding(holding)}
                  >
                    {/* Symbol / Asset */}
                    <td className="p-3.5 pl-4">
                      <div className="flex items-center gap-2.5">
                        <div className="w-7 h-7 rounded-lg bg-primary-light flex items-center justify-center text-primary font-bold text-[11px] flex-shrink-0">
                          {holding.ticker.slice(0, 2)}
                        </div>
                        <div>
                          <div className="flex items-center gap-1.5">
                            <span className="font-bold text-content hover:text-primary transition-colors">
                              {holding.ticker}
                            </span>
                            {holding.sector && (
                              <Badge variant="neutral" size="sm" className="text-[9px] py-0 px-1">
                                {holding.sector}
                              </Badge>
                            )}
                          </div>
                          <p className="text-[11px] text-content-muted truncate max-w-[160px]">
                            {holding.company_name || holding.ticker}
                          </p>
                        </div>
                      </div>
                    </td>

                    {/* Quantity */}
                    <td className="p-3.5 text-right font-tabular text-content font-medium">
                      {holding.shares}
                    </td>

                    {/* Avg Cost */}
                    <td className="p-3.5 text-right font-tabular text-content-muted">
                      {formatCurrency(holding.avg_price, "INR")}
                    </td>

                    {/* Current Price */}
                    <td className="p-3.5 text-right font-tabular text-content font-bold">
                      {formatCurrency(holding.current_price, "INR")}
                    </td>

                    {/* Market Value */}
                    <td className="p-3.5 text-right font-tabular text-content font-bold">
                      {formatCurrency(holding.market_value, "INR")}
                    </td>

                    {/* 1-Day Chg */}
                    <td className="p-3.5 text-right font-tabular text-financial-gain font-medium">
                      +{holding.daily_change_pct || 0.8}%
                    </td>

                    {/* Unrealized P&L */}
                    <td
                      className={`p-3.5 text-right font-tabular font-bold ${
                        isGain ? "text-financial-gain" : "text-financial-loss"
                      }`}
                    >
                      <span className="flex items-center justify-end gap-0.5">
                        {isGain ? <TrendingUp className="w-3 h-3" /> : <TrendingDown className="w-3 h-3" />}
                        {isGain ? "+" : ""}
                        {formatCurrency(holding.unrealized_pnl, "INR")}
                      </span>
                    </td>

                    {/* Return % */}
                    <td
                      className={`p-3.5 text-right font-tabular font-bold ${
                        isGain ? "text-financial-gain" : "text-financial-loss"
                      }`}
                    >
                      {formatPercent(holding.unrealized_pnl_pct)}
                    </td>

                    {/* Weight % */}
                    <td className="p-3.5 text-right">
                      <div className="flex items-center justify-end gap-2">
                        <div className="w-12 h-1.5 rounded-full bg-border overflow-hidden hidden sm:block">
                          <div
                            className="h-full bg-primary rounded-full"
                            style={{ width: `${Math.min(100, holding.weight_pct * 2.5)}%` }}
                          />
                        </div>
                        <span className="font-bold text-primary font-tabular">
                          {formatPercent(holding.weight_pct)}
                        </span>
                      </div>
                    </td>

                    {/* Actions */}
                    <td
                      className="p-3.5 pr-4 text-center"
                      onClick={(e: React.MouseEvent) => e.stopPropagation()}
                    >
                      <div className="flex items-center justify-center gap-1">
                        <button
                          onClick={() => onToggleWatchlist(holding.ticker)}
                          title={isInWatchlist ? "Remove from Watchlist" : "Add to Watchlist"}
                          className={`p-1.5 rounded-lg border transition-all ${
                            isInWatchlist
                              ? "bg-primary-light border-primary/30 text-primary"
                              : "border-border text-content-muted hover:text-content hover:bg-surface-subtle"
                          }`}
                        >
                          {isInWatchlist ? (
                            <BookmarkCheck className="w-3.5 h-3.5" />
                          ) : (
                            <Bookmark className="w-3.5 h-3.5" />
                          )}
                        </button>
                        <Link
                          href={`/stocks/${encodeURIComponent(holding.ticker)}`}
                          title="Open Stock Intelligence Workspace"
                          className="p-1.5 rounded-lg border border-border text-content-muted hover:text-primary hover:border-primary/40 hover:bg-surface-subtle transition-all"
                        >
                          <ExternalLink className="w-3.5 h-3.5" />
                        </Link>
                      </div>
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      </CardContent>
    </Card>
  );
};
