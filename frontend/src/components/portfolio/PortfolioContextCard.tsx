"use client";

import React from "react";
import { PortfolioUserContext } from "@/types/portfolio-copilot";
import { Badge } from "@/components/common/Badge";
import { Wallet, TrendingUp, TrendingDown, PieChart, Shield, Activity } from "lucide-react";

interface PortfolioContextCardProps {
  context: PortfolioUserContext;
}

export const PortfolioContextCard: React.FC<PortfolioContextCardProps> = ({ context }) => {
  const isGain = context.absolute_pnl >= 0;

  return (
    <div className="bg-surface border border-border rounded-2xl p-6 shadow-card space-y-5">
      {/* Top Banner */}
      <div className="flex flex-wrap items-center justify-between gap-3 border-b border-border pb-4">
        <div className="flex items-center gap-2.5">
          <div className="p-2 rounded-xl bg-primary/10 text-primary border border-primary/20">
            <Wallet className="w-5 h-5" />
          </div>
          <div>
            <h2 className="text-base font-bold text-content">{context.name}</h2>
            <p className="text-xs text-content-muted">
              {context.holdings_count} active holdings • Herfindahl Index:{" "}
              <span className="font-mono font-bold text-content">{context.herfindahl_index}</span>
            </p>
          </div>
        </div>

        <div className="flex items-center gap-2">
          <Badge
            variant={context.data_status === "LIVE" ? "success" : "neutral"}
            size="sm"
          >
            {context.data_status} DATA
          </Badge>
          <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-surface-subtle border border-border text-content-muted">
            Beta: {context.weighted_beta}
          </span>
        </div>
      </div>

      {/* Grid of Key Metrics */}
      <div className="grid grid-cols-2 sm:grid-cols-4 gap-4 font-tabular">
        {/* Total Market Value */}
        <div className="p-3.5 rounded-xl bg-surface-subtle border border-border/60 space-y-1">
          <span className="text-[10px] uppercase font-bold text-content-muted tracking-wider">
            Total Market Value
          </span>
          <p className="text-lg font-black text-content">
            ₹{context.total_market_value.toLocaleString("en-IN", { minimumFractionDigits: 2, maximumFractionDigits: 2 })}
          </p>
          <span className="text-[10px] text-content-muted">
            Cash: ₹{context.cash_balance.toLocaleString("en-IN")}
          </span>
        </div>

        {/* Total Unrealized P&L */}
        <div className="p-3.5 rounded-xl bg-surface-subtle border border-border/60 space-y-1">
          <span className="text-[10px] uppercase font-bold text-content-muted tracking-wider">
            Unrealized P&L
          </span>
          <div className={`flex items-center gap-1.5 text-lg font-black ${isGain ? "text-financial-gain" : "text-financial-loss"}`}>
            {isGain ? <TrendingUp className="w-4 h-4" /> : <TrendingDown className="w-4 h-4" />}
            <span>
              {isGain ? "+" : ""}₹{context.absolute_pnl.toLocaleString("en-IN", { minimumFractionDigits: 2 })}
            </span>
          </div>
          <span className={`text-[10px] font-bold ${isGain ? "text-financial-gain" : "text-financial-loss"}`}>
            {isGain ? "+" : ""}{context.percentage_pnl}% total return
          </span>
        </div>

        {/* Top Holding Exposure */}
        <div className="p-3.5 rounded-xl bg-surface-subtle border border-border/60 space-y-1">
          <span className="text-[10px] uppercase font-bold text-content-muted tracking-wider flex items-center gap-1">
            <PieChart className="w-3 h-3 text-accent" /> Top Position
          </span>
          <p className="text-base font-bold text-content truncate">
            {context.top_holding_symbol || "N/A"}
          </p>
          <span className="text-[10px] text-content-muted">
            {context.top_holding_weight_pct}% weight (Top 3: {context.top3_exposure_pct}%)
          </span>
        </div>

        {/* Annualized Volatility & VaR */}
        <div className="p-3.5 rounded-xl bg-surface-subtle border border-border/60 space-y-1">
          <span className="text-[10px] uppercase font-bold text-content-muted tracking-wider flex items-center gap-1">
            <Shield className="w-3 h-3 text-financial-warning" /> Risk Profile
          </span>
          <p className="text-base font-bold text-content">
            {context.annualized_volatility_pct}% Vol
          </p>
          <span className="text-[10px] text-content-muted">
            1-Day 95% VaR: {context.var_95_daily_pct}%
          </span>
        </div>
      </div>
    </div>
  );
};
