"use client";

import React from "react";
import Link from "next/link";
import { usePortfolio } from "@/hooks/usePortfolio";
import { Card, CardHeader, CardTitle, CardContent } from "@/components/common/Card";
import { Badge } from "@/components/common/Badge";
import { Button } from "@/components/common/Button";
import { Skeleton } from "@/components/common/Skeleton";
import { AllocationChart } from "@/components/charts/AllocationChart";
import { formatCurrency, formatPercent } from "@/lib/utils";
import { Briefcase, ArrowRight, TrendingUp, TrendingDown, Shield } from "lucide-react";

export const PortfolioSnapshotSection: React.FC = () => {
  const { portfolio, allocationData, isLoading, isDemo } = usePortfolio();

  const isTotalPnlPositive = portfolio.total_unrealized_pnl >= 0;
  const isDailyPnlPositive = (portfolio.daily_pnl || 0) >= 0;

  return (
    <Card className="border-border shadow-card">
      <CardHeader className="pb-3 border-b border-border flex flex-row items-center justify-between">
        <div className="flex items-center gap-2">
          <div className="p-1.5 rounded-lg bg-primary/10 text-primary">
            <Briefcase className="w-4 h-4" />
          </div>
          <div>
            <CardTitle className="text-base font-bold text-content flex items-center gap-2">
              Portfolio Snapshot
              {isDemo && (
                <Badge variant="gold" size="sm">
                  DEMO DATA
                </Badge>
              )}
            </CardTitle>
            <p className="text-xs text-content-muted mt-0.5">
              Net asset value, return metrics & sector weight allocation
            </p>
          </div>
        </div>

        <Link href="/portfolio">
          <Button
            variant="ghost"
            size="sm"
            className="text-xs text-primary hover:text-primary-dark"
            rightIcon={<ArrowRight className="w-3.5 h-3.5" />}
          >
            Manage
          </Button>
        </Link>
      </CardHeader>

      <CardContent className="p-4 sm:p-5">
        {isLoading ? (
          <div className="space-y-4">
            <div className="grid grid-cols-2 gap-3">
              <Skeleton variant="card" className="h-16" />
              <Skeleton variant="card" className="h-16" />
            </div>
            <Skeleton variant="card" className="h-44" />
          </div>
        ) : !portfolio.holdings || portfolio.holdings.length === 0 ? (
          <div className="p-8 text-center space-y-3">
            <div className="w-12 h-12 rounded-full bg-primary/10 text-primary flex items-center justify-center mx-auto">
              <Briefcase className="w-6 h-6" />
            </div>
            <h3 className="text-sm font-bold text-content">Build your first portfolio</h3>
            <p className="text-xs text-content-muted max-w-sm mx-auto">
              Track multi-asset positions with real-time mark-to-market valuations and risk-adjusted Sharpe/VaR analytics.
            </p>
            <Link href="/portfolio">
              <Button variant="primary" size="sm">
                Add Positions
              </Button>
            </Link>
          </div>
        ) : (
          <div className="space-y-4">
            {/* Top Stat Summary Grid */}
            <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 p-3.5 rounded-xl bg-surface-subtle/70 border border-border">
              {/* Total Value */}
              <div>
                <span className="text-[11px] font-semibold text-content-muted uppercase tracking-wider block">
                  Net Asset Value
                </span>
                <span className="text-base sm:text-lg font-bold font-mono text-content">
                  {formatCurrency(portfolio.total_value, "INR")}
                </span>
              </div>

              {/* Total P&L */}
              <div>
                <span className="text-[11px] font-semibold text-content-muted uppercase tracking-wider block">
                  Total Returns
                </span>
                <div
                  className={`flex items-center gap-1 text-sm sm:text-base font-bold font-mono ${
                    isTotalPnlPositive ? "text-gain" : "text-loss"
                  }`}
                >
                  {isTotalPnlPositive ? <TrendingUp className="w-3.5 h-3.5" /> : <TrendingDown className="w-3.5 h-3.5" />}
                  <span>{isTotalPnlPositive ? "+" : ""}{formatPercent(portfolio.total_unrealized_pnl_pct)}</span>
                </div>
              </div>

              {/* Daily P&L */}
              <div>
                <span className="text-[11px] font-semibold text-content-muted uppercase tracking-wider block">
                  Today's Move
                </span>
                <div
                  className={`flex items-center gap-1 text-sm sm:text-base font-bold font-mono ${
                    isDailyPnlPositive ? "text-gain" : "text-loss"
                  }`}
                >
                  <span>{isDailyPnlPositive ? "+" : ""}{formatPercent(portfolio.daily_pnl_pct || 0)}</span>
                </div>
              </div>

              {/* Risk Beta */}
              <div>
                <span className="text-[11px] font-semibold text-content-muted uppercase tracking-wider block">
                  Weighted Beta
                </span>
                <div className="flex items-center gap-1 text-sm sm:text-base font-bold font-mono text-content">
                  <Shield className="w-3.5 h-3.5 text-primary" />
                  <span>{portfolio.risk_metrics?.portfolio_beta?.toFixed(2) || "0.95"}</span>
                </div>
              </div>
            </div>

            {/* Allocation Donut + Holdings List */}
            <div className="grid grid-cols-1 md:grid-cols-12 gap-4 items-center pt-2">
              {/* Chart (5 cols) */}
              <div className="md:col-span-5 flex justify-center">
                <div className="w-full max-w-[220px] h-[190px]">
                  <AllocationChart data={allocationData} height={190} />
                </div>
              </div>

              {/* Top Holdings Table (7 cols) */}
              <div className="md:col-span-7 space-y-2">
                <span className="text-xs font-bold text-content-muted uppercase tracking-wider block">
                  Top Position Weights
                </span>
                <div className="space-y-1.5 max-h-[190px] overflow-y-auto pr-1">
                  {portfolio.holdings.map((h) => {
                    const isHoldingPositive = h.unrealized_pnl >= 0;
                    return (
                      <div
                        key={h.ticker}
                        className="p-2 rounded-lg bg-surface border border-border/80 flex items-center justify-between text-xs"
                      >
                        <div className="flex items-center gap-2 min-w-0">
                          <span className="font-mono font-bold text-content">{h.ticker}</span>
                          <span className="text-[10px] text-content-muted font-mono">
                            ({h.shares} sh)
                          </span>
                        </div>

                        <div className="flex items-center gap-3 font-mono">
                          <span className="font-semibold text-content">
                            {formatCurrency(h.market_value, "INR")}
                          </span>
                          <span
                            className={`font-semibold ${
                              isHoldingPositive ? "text-gain" : "text-loss"
                            }`}
                          >
                            {isHoldingPositive ? "+" : ""}{formatPercent(h.unrealized_pnl_pct)}
                          </span>
                        </div>
                      </div>
                    );
                  })}
                </div>
              </div>
            </div>
          </div>
        )}
      </CardContent>
    </Card>
  );
};
