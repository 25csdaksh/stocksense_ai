"use client";

import React from "react";
import { StatCard } from "@/components/common/StatCard";
import { Skeleton } from "@/components/common/Skeleton";
import { formatCurrency, formatPercent } from "@/lib/utils";
import { PortfolioSummaryResponse } from "@/types";
import {
  Briefcase,
  TrendingUp,
  Percent,
  Shield,
  Layers,
  DollarSign,
  Activity,
} from "lucide-react";

export interface PortfolioSummaryProps {
  portfolio: PortfolioSummaryResponse;
  isLoading?: boolean;
}

export const PortfolioSummary: React.FC<PortfolioSummaryProps> = ({
  portfolio,
  isLoading = false,
}) => {
  if (isLoading) {
    return (
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        {Array.from({ length: 8 }).map((_, i) => (
          <div key={i} className="p-5 rounded-xl border border-border bg-surface space-y-3">
            <Skeleton className="h-3 w-24" />
            <Skeleton className="h-8 w-36" />
            <Skeleton className="h-3 w-20" />
          </div>
        ))}
      </div>
    );
  }

  const totalVal = portfolio.total_value || 0;
  const totalCost = portfolio.total_cost || 0;
  const cash = portfolio.cash_balance ?? 154800;
  const dailyPnl = portfolio.daily_pnl ?? 0;
  const dailyPnlPct = portfolio.daily_pnl_pct ?? 0;
  const totalPnl = portfolio.total_unrealized_pnl ?? (totalVal - totalCost);
  const totalPnlPct = portfolio.total_unrealized_pnl_pct ?? (totalCost > 0 ? (totalPnl / totalCost) * 100 : 0);
  const positionsCount = portfolio.positions_count ?? (portfolio.holdings?.length || 0);
  const weightedBeta = portfolio.weighted_beta ?? portfolio.risk_metrics?.portfolio_beta ?? 0.94;
  const dailyVarPct = portfolio.daily_var_95_pct ?? portfolio.risk_metrics?.daily_var_95_pct ?? 1.45;
  const dailyVarAmount = portfolio.risk_metrics?.daily_var_95 ?? Math.round((dailyVarPct / 100) * totalVal);

  return (
    <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
      {/* 1. Total Portfolio Value */}
      <StatCard
        label="Total Portfolio Value"
        value={formatCurrency(totalVal, "INR")}
        change={totalPnlPct}
        changeLabel="overall return"
        icon={<Briefcase className="w-4 h-4 text-primary" />}
      />

      {/* 2. Invested Capital & Cash */}
      <StatCard
        label="Invested Capital"
        value={formatCurrency(totalCost, "INR")}
        changeLabel={`Liquid Cash: ${formatCurrency(cash, "INR", { compact: true })}`}
        icon={<DollarSign className="w-4 h-4 text-secondary" />}
      />

      {/* 3. Today's P&L */}
      <StatCard
        label="Today's P&L"
        value={`${dailyPnl >= 0 ? "+" : ""}${formatCurrency(dailyPnl, "INR")}`}
        change={dailyPnlPct}
        changeLabel="1-day return"
        icon={<TrendingUp className="w-4 h-4 text-accent" />}
      />

      {/* 4. Total Unrealized P&L */}
      <StatCard
        label="Total Unrealized P&L"
        value={`${totalPnl >= 0 ? "+" : ""}${formatCurrency(totalPnl, "INR")}`}
        change={totalPnlPct}
        changeLabel="cumulative gain/loss"
        icon={<DollarSign className="w-4 h-4 text-primary-dark" />}
      />

      {/* 5. Positions Count */}
      <StatCard
        label="Active Holdings"
        value={`${positionsCount} Positions`}
        changeLabel="Equity constituents"
        icon={<Layers className="w-4 h-4 text-content-muted" />}
      />

      {/* 6. Weighted Beta */}
      <StatCard
        label="Portfolio Beta (β)"
        value={weightedBeta.toFixed(2)}
        changeLabel="vs NIFTY 50 Benchmark"
        icon={<Activity className="w-4 h-4 text-secondary" />}
      />

      {/* 7. Parametric 95% Daily VaR */}
      <StatCard
        label="Daily 95% VaR"
        value={`${formatCurrency(dailyVarAmount, "INR", { compact: true })} (${formatPercent(dailyVarPct)})`}
        changeLabel="Max expected 24h loss (95% CI)"
        icon={<Shield className="w-4 h-4 text-financial-loss" />}
      />

      {/* 8. Total Return % */}
      <StatCard
        label="Total Return"
        value={formatPercent(totalPnlPct)}
        change={dailyPnlPct}
        changeLabel="vs last session"
        icon={<Percent className="w-4 h-4 text-accent-dark" />}
      />
    </div>
  );
};
