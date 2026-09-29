"use client";

import React from "react";
import Link from "next/link";
import { useWatchlist } from "@/hooks/useWatchlist";
import { Card, CardHeader, CardTitle, CardContent } from "@/components/common/Card";
import { Badge } from "@/components/common/Badge";
import { Button } from "@/components/common/Button";
import { Skeleton } from "@/components/common/Skeleton";
import { EmptyState } from "@/components/common/EmptyState";
import { formatCurrency, formatPercent, formatNumber } from "@/lib/utils";
import { Bookmark, ArrowRight, TrendingUp, TrendingDown, ExternalLink } from "lucide-react";

export const WatchlistSnapshotSection: React.FC = () => {
  const { watchlist, isLoading, isDemo } = useWatchlist();

  return (
    <Card className="border-border shadow-card">
      <CardHeader className="pb-3 border-b border-border flex flex-row items-center justify-between">
        <div className="flex items-center gap-2">
          <div className="p-1.5 rounded-lg bg-primary/10 text-primary">
            <Bookmark className="w-4 h-4" />
          </div>
          <div>
            <CardTitle className="text-base font-bold text-content flex items-center gap-2">
              Watchlist Snapshot
              {isDemo && (
                <Badge variant="gold" size="sm">
                  DEMO DATA
                </Badge>
              )}
            </CardTitle>
            <p className="text-xs text-content-muted mt-0.5">
              Live quotes and technical alert statuses for tracked assets
            </p>
          </div>
        </div>

        <Link href="/watchlist">
          <Button
            variant="ghost"
            size="sm"
            className="text-xs text-primary hover:text-primary-dark"
            rightIcon={<ArrowRight className="w-3.5 h-3.5" />}
          >
            View All
          </Button>
        </Link>
      </CardHeader>

      <CardContent className="p-0">
        {isLoading ? (
          <div className="p-4 space-y-3">
            {[1, 2, 3, 4].map((i) => (
              <Skeleton key={i} variant="text" className="h-10 w-full" />
            ))}
          </div>
        ) : watchlist.length === 0 ? (
          <div className="p-6">
            <EmptyState
              title="No stocks added yet"
              description="Start tracking your core investment ideas, sector leaders, and volatility candidates."
              actionLabel="Explore Stocks"
              onAction={() => (window.location.href = "/stocks")}
            />
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs border-collapse">
              <thead>
                <tr className="border-b border-border bg-surface-subtle/50 text-content-muted font-semibold uppercase text-[10px] tracking-wider">
                  <th className="py-2.5 px-4">Ticker</th>
                  <th className="py-2.5 px-3">Company</th>
                  <th className="py-2.5 px-3 text-right">Price</th>
                  <th className="py-2.5 px-3 text-right">Change</th>
                  <th className="py-2.5 px-3 text-right hidden sm:table-cell">Volume</th>
                  <th className="py-2.5 px-4 text-center">Status</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-border/60">
                {watchlist.slice(0, 5).map((item) => {
                  const isPositive = item.change >= 0;
                  return (
                    <tr
                      key={item.ticker}
                      className="hover:bg-surface-subtle/60 transition-colors group cursor-pointer"
                      onClick={() => (window.location.href = `/stocks/${encodeURIComponent(item.ticker)}`)}
                    >
                      {/* Ticker */}
                      <td className="py-3 px-4 font-mono font-bold text-primary group-hover:text-primary-dark flex items-center gap-1.5">
                        <span>{item.ticker}</span>
                        <ExternalLink className="w-3 h-3 text-content-muted opacity-0 group-hover:opacity-100 transition-opacity" />
                      </td>

                      {/* Company */}
                      <td className="py-3 px-3 text-content-muted font-medium max-w-[140px] truncate">
                        {item.company_name}
                      </td>

                      {/* Price */}
                      <td className="py-3 px-3 text-right font-mono font-semibold text-content">
                        {formatCurrency(item.price, "INR")}
                      </td>

                      {/* Change */}
                      <td className="py-3 px-3 text-right font-mono">
                        <div
                          className={`inline-flex items-center gap-0.5 font-semibold ${
                            isPositive ? "text-gain" : "text-loss"
                          }`}
                        >
                          {isPositive ? <TrendingUp className="w-3 h-3" /> : <TrendingDown className="w-3 h-3" />}
                          <span>{isPositive ? "+" : ""}{formatPercent(item.change_pct)}</span>
                        </div>
                      </td>

                      {/* Volume */}
                      <td className="py-3 px-3 text-right font-mono text-content-muted hidden sm:table-cell">
                        {item.volume > 10000000
                          ? `${(item.volume / 10000000).toFixed(2)} Cr`
                          : `${(item.volume / 100000).toFixed(1)} L`}
                      </td>

                      {/* Status */}
                      <td className="py-3 px-4 text-center">
                        <Badge
                          variant={
                            item.status === "ACTIVE"
                              ? "gain"
                              : item.status === "ALERT"
                              ? "loss"
                              : "neutral"
                          }
                          size="sm"
                          className="font-mono text-[10px]"
                        >
                          {item.status}
                        </Badge>
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        )}
      </CardContent>
    </Card>
  );
};
