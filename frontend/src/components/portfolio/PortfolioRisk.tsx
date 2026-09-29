"use client";

import React from "react";
import { Card, CardHeader, CardTitle, CardDescription, CardContent } from "@/components/common/Card";
import { Badge } from "@/components/common/Badge";
import { formatCurrency, formatPercent } from "@/lib/utils";
import { PortfolioRiskMetrics } from "@/types";
import {
  ShieldAlert,
  Activity,
  Percent,
  TrendingDown,
  Gauge,
  Zap,
  Sliders,
  ShieldCheck,
} from "lucide-react";

export interface PortfolioRiskProps {
  metrics: PortfolioRiskMetrics;
  totalValue: number;
}

export const PortfolioRisk: React.FC<PortfolioRiskProps> = ({ metrics, totalValue }) => {
  const beta = metrics.portfolio_beta;
  const vol = metrics.annualized_volatility_pct;
  const varPct = metrics.daily_var_95_pct;
  const varAmount = metrics.daily_var_95 ?? (varPct ? (varPct / 100) * totalValue : undefined);
  const maxDd = metrics.max_drawdown_pct;
  const sharpe = metrics.sharpe_ratio;
  const sortino = metrics.sortino_ratio;
  const downsideDev = metrics.downside_deviation_pct;
  const trackingError = metrics.tracking_error_pct;

  const riskCards = [
    {
      title: "Portfolio Beta (β)",
      value: beta !== undefined ? beta.toFixed(2) : "DATA UNAVAILABLE",
      subtext: "Covariance relative to NIFTY 50",
      tag: "Historical Metric",
      icon: <Activity className="w-4 h-4 text-primary" />,
      color: "text-primary",
    },
    {
      title: "Annualized Volatility (σ)",
      value: vol !== undefined ? formatPercent(vol) : "DATA UNAVAILABLE",
      subtext: "252-day rolling annualized standard deviation",
      tag: "Historical Metric",
      icon: <Gauge className="w-4 h-4 text-secondary" />,
      color: "text-secondary",
    },
    {
      title: "1-Day 95% Parametric VaR",
      value:
        varPct !== undefined && varAmount !== undefined
          ? `${formatCurrency(varAmount, "INR", { compact: true })} (${formatPercent(varPct)})`
          : "DATA UNAVAILABLE",
      subtext: "Maximum expected 24h loss with 95% confidence",
      tag: "Model-Derived Metric",
      icon: <ShieldAlert className="w-4 h-4 text-financial-loss" />,
      color: "text-financial-loss",
    },
    {
      title: "Historical Maximum Drawdown",
      value: maxDd !== undefined ? formatPercent(maxDd) : "DATA UNAVAILABLE",
      subtext: "Peak-to-trough equity reduction",
      tag: "Historical Metric",
      icon: <TrendingDown className="w-4 h-4 text-financial-loss" />,
      color: "text-financial-loss",
    },
    {
      title: "Sharpe Ratio",
      value: sharpe !== undefined ? sharpe.toFixed(2) : "DATA UNAVAILABLE",
      subtext: "Excess return per unit of total risk (Rf = 6.5%)",
      tag: "Model-Derived Metric",
      icon: <ShieldCheck className="w-4 h-4 text-primary-dark" />,
      color: "text-primary-dark",
    },
    {
      title: "Sortino Ratio",
      value: sortino !== undefined ? sortino.toFixed(2) : "DATA UNAVAILABLE",
      subtext: "Excess return penalized solely for downside volatility",
      tag: "Model-Derived Metric",
      icon: <Sliders className="w-4 h-4 text-accent-dark" />,
      color: "text-accent-dark",
    },
    {
      title: "Downside Semi-Deviation",
      value: downsideDev !== undefined ? formatPercent(downsideDev) : "DATA UNAVAILABLE",
      subtext: "Volatility of negative portfolio returns",
      tag: "Historical Metric",
      icon: <Zap className="w-4 h-4 text-secondary" />,
      color: "text-secondary",
    },
    {
      title: "Tracking Error (TE)",
      value: trackingError !== undefined ? formatPercent(trackingError) : "DATA UNAVAILABLE",
      subtext: "Standard deviation of excess returns vs NIFTY 50",
      tag: "Model-Derived Metric",
      icon: <Percent className="w-4 h-4 text-content-muted" />,
      color: "text-content",
    },
  ];

  return (
    <Card>
      <CardHeader className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-2 pb-3">
        <div>
          <div className="flex items-center gap-2">
            <CardTitle className="flex items-center gap-2">
              <ShieldAlert className="w-4 h-4 text-financial-loss" />
              Quantitative Portfolio Risk Engine
            </CardTitle>
            <Badge variant="neutral" size="sm" className="font-mono text-[10px]">
              95% Parametric CI
            </Badge>
          </div>
          <CardDescription>
            Multi-factor volatility, tail-risk exposures, downside deviation, and risk-adjusted efficiency.
          </CardDescription>
        </div>
      </CardHeader>

      <CardContent>
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-3.5">
          {riskCards.map((card, idx) => (
            <div
              key={idx}
              className="p-3.5 rounded-xl border border-border bg-surface-subtle/50 hover:bg-surface-subtle transition-all space-y-2"
            >
              <div className="flex items-center justify-between">
                <span className="text-[11px] font-bold text-content-muted truncate block">
                  {card.title}
                </span>
                {card.icon}
              </div>

              <div className={`text-lg font-bold font-tabular ${card.color}`}>
                {card.value}
              </div>

              <div className="flex items-center justify-between pt-1 border-t border-border/50 text-[10px]">
                <span className="text-content-muted truncate max-w-[150px]">{card.subtext}</span>
                <span className="font-semibold text-content-muted/80 tracking-wider uppercase text-[9px]">
                  {card.tag}
                </span>
              </div>
            </div>
          ))}
        </div>
      </CardContent>
    </Card>
  );
};
