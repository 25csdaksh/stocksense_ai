"use client";

import React from "react";
import { useStockFundamentals } from "@/hooks/useStockFundamentals";
import { Card, CardHeader, CardTitle, CardDescription, CardContent } from "@/components/common/Card";
import { Badge } from "@/components/common/Badge";
import { Skeleton } from "@/components/common/Skeleton";
import { Button } from "@/components/common/Button";
import { FileText, ShieldCheck, DollarSign, Percent, TrendingUp, AlertCircle, RefreshCw } from "lucide-react";
import { cn } from "@/lib/utils";

export interface FundamentalIntelligenceProps {
  ticker: string;
  isDemo?: boolean;
}

export const FundamentalIntelligence: React.FC<FundamentalIntelligenceProps> = ({
  ticker,
  isDemo: parentDemo = false,
}) => {
  const { fundamentals, isLoading, isError, error, isDemo, refresh } = useStockFundamentals(ticker);

  const displayDemo = parentDemo || isDemo;

  if (isLoading) {
    return (
      <Card className="border-border">
        <CardHeader>
          <Skeleton className="h-6 w-48" />
          <Skeleton className="h-4 w-72" />
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            {[1, 2, 3].map((i) => (
              <Skeleton key={i} className="h-48 rounded-xl" />
            ))}
          </div>
        </CardContent>
      </Card>
    );
  }

  if (isError || !fundamentals) {
    return (
      <Card className="border-border">
        <CardContent className="py-8 text-center space-y-3">
          <AlertCircle className="w-8 h-8 text-financial-loss mx-auto" />
          <p className="text-sm font-semibold text-content">Unable to load fundamental analytics</p>
          <p className="text-xs text-content-muted">{error || "Server response unavailable"}</p>
          <Button variant="outline" size="sm" onClick={() => refresh()}>
            Retry
          </Button>
        </CardContent>
      </Card>
    );
  }

  const { valuation, profitability, financial_health } = fundamentals;

  return (
    <Card className="border-border shadow-card">
      <CardHeader className="pb-3 border-b border-border/60 flex flex-col sm:flex-row sm:items-center justify-between gap-3">
        <div>
          <div className="flex items-center gap-2">
            <CardTitle className="text-lg font-bold flex items-center gap-2 text-content">
              <FileText className="w-5 h-5 text-primary" />
              Fundamental & Financial Statement Intelligence
            </CardTitle>
            {displayDemo && (
              <Badge variant="gold" size="sm">
                DEMO DATA
              </Badge>
            )}
            {financial_health?.health_score && (
              <Badge
                variant={
                  financial_health.health_score === "EXCELLENT" || financial_health.health_score === "STRONG"
                    ? "gain"
                    : "gold"
                }
                size="md"
              >
                HEALTH: {financial_health.health_score}
              </Badge>
            )}

          </div>
          <CardDescription className="text-xs text-content-muted">
            Audited financial ratios, cash generation capacity, capital efficiency, and solvency metrics
          </CardDescription>
        </div>

        <button
          onClick={() => refresh()}
          className="p-1.5 self-end sm:self-center rounded-lg text-content-muted hover:text-content hover:bg-surface-subtle transition-colors"
          title="Refresh Fundamentals"
        >
          <RefreshCw className="w-3.5 h-3.5" />
        </button>
      </CardHeader>

      <CardContent className="pt-4">
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-4">
          {/* Section 1: Valuation Multiples */}
          <div className="p-4 rounded-xl bg-surface-subtle/70 border border-border space-y-3">
            <div className="flex items-center justify-between border-b border-border/60 pb-2">
              <span className="text-xs font-bold text-content flex items-center gap-1.5">
                <DollarSign className="w-4 h-4 text-primary" />
                Valuation Multiples
              </span>
              <span className="text-[10px] text-content-muted font-semibold">TTM / Forward</span>
            </div>

            <div className="space-y-2.5 font-tabular text-xs">
              <div className="flex items-center justify-between">
                <span className="text-content-muted">P/E Ratio (TTM):</span>
                <span className="font-bold text-content">
                  {valuation?.pe_ratio ? `${valuation.pe_ratio.toFixed(1)}x` : "DATA UNAVAILABLE"}
                </span>
              </div>
              <div className="flex items-center justify-between">
                <span className="text-content-muted">Forward P/E:</span>
                <span className="font-bold text-content">
                  {valuation?.forward_pe ? `${valuation.forward_pe.toFixed(1)}x` : "DATA UNAVAILABLE"}
                </span>
              </div>
              <div className="flex items-center justify-between">
                <span className="text-content-muted">Price to Book (P/B):</span>
                <span className="font-bold text-content">
                  {valuation?.pb_ratio ? `${valuation.pb_ratio.toFixed(2)}x` : "DATA UNAVAILABLE"}
                </span>
              </div>
              <div className="flex items-center justify-between">
                <span className="text-content-muted">EV / EBITDA:</span>
                <span className="font-bold text-content">
                  {valuation?.ev_ebitda ? `${valuation.ev_ebitda.toFixed(1)}x` : "DATA UNAVAILABLE"}
                </span>
              </div>
              <div className="flex items-center justify-between">
                <span className="text-content-muted">FCF Yield:</span>
                <span className="font-bold text-financial-gain">
                  {valuation?.fcf_yield_pct ? `${valuation.fcf_yield_pct.toFixed(1)}%` : "DATA UNAVAILABLE"}
                </span>
              </div>
            </div>
          </div>

          {/* Section 2: Profitability & Margins */}
          <div className="p-4 rounded-xl bg-surface-subtle/70 border border-border space-y-3">
            <div className="flex items-center justify-between border-b border-border/60 pb-2">
              <span className="text-xs font-bold text-content flex items-center gap-1.5">
                <Percent className="w-4 h-4 text-secondary" />
                Profitability & Returns
              </span>
              <span className="text-[10px] text-content-muted font-semibold">Normalized</span>
            </div>

            <div className="space-y-2.5 font-tabular text-xs">
              <div className="flex items-center justify-between">
                <span className="text-content-muted">Gross Margin:</span>
                <span className="font-bold text-content">
                  {profitability?.gross_margin_pct ? `${profitability.gross_margin_pct.toFixed(1)}%` : "DATA UNAVAILABLE"}
                </span>
              </div>
              <div className="flex items-center justify-between">
                <span className="text-content-muted">Operating Margin:</span>
                <span className="font-bold text-content">
                  {profitability?.operating_margin_pct ? `${profitability.operating_margin_pct.toFixed(1)}%` : "DATA UNAVAILABLE"}
                </span>
              </div>
              <div className="flex items-center justify-between">
                <span className="text-content-muted">Net Profit Margin:</span>
                <span className="font-bold text-content">
                  {profitability?.net_margin_pct ? `${profitability.net_margin_pct.toFixed(1)}%` : "DATA UNAVAILABLE"}
                </span>
              </div>
              <div className="flex items-center justify-between">
                <span className="text-content-muted">Return on Equity (ROE):</span>
                <span className="font-bold text-financial-gain">
                  {profitability?.roe_pct ? `${profitability.roe_pct.toFixed(1)}%` : "DATA UNAVAILABLE"}
                </span>
              </div>
              <div className="flex items-center justify-between">
                <span className="text-content-muted">Return on Assets (ROA):</span>
                <span className="font-bold text-content">
                  {profitability?.roa_pct ? `${profitability.roa_pct.toFixed(1)}%` : "DATA UNAVAILABLE"}
                </span>
              </div>
            </div>
          </div>

          {/* Section 3: Financial Health & Solvency */}
          <div className="p-4 rounded-xl bg-surface-subtle/70 border border-border space-y-3">
            <div className="flex items-center justify-between border-b border-border/60 pb-2">
              <span className="text-xs font-bold text-content flex items-center gap-1.5">
                <ShieldCheck className="w-4 h-4 text-primary" />
                Balance Sheet & Solvency
              </span>
              <span className="text-[10px] text-content-muted font-semibold">Stress Resilient</span>
            </div>

            <div className="space-y-2.5 font-tabular text-xs">
              <div className="flex items-center justify-between">
                <span className="text-content-muted">Current Ratio:</span>
                <span className="font-bold text-content">
                  {financial_health?.current_ratio ? `${financial_health.current_ratio.toFixed(2)}x` : "DATA UNAVAILABLE"}
                </span>
              </div>
              <div className="flex items-center justify-between">
                <span className="text-content-muted">Debt / Equity:</span>
                <span className="font-bold text-content">
                  {financial_health?.debt_to_equity !== undefined && financial_health?.debt_to_equity !== null
                    ? `${financial_health.debt_to_equity.toFixed(2)}x`
                    : "DATA UNAVAILABLE"}
                </span>
              </div>
              <div className="flex items-center justify-between">
                <span className="text-content-muted">Interest Coverage:</span>
                <span className="font-bold text-content">
                  {financial_health?.interest_coverage_ratio
                    ? `${financial_health.interest_coverage_ratio.toFixed(1)}x`
                    : "DATA UNAVAILABLE"}
                </span>
              </div>
              <div className="flex items-center justify-between">
                <span className="text-content-muted">Altman Z-Score:</span>
                <span
                  className={cn(
                    "font-bold",
                    financial_health?.altman_z_score && financial_health.altman_z_score > 3.0
                      ? "text-financial-gain"
                      : financial_health?.altman_z_score && financial_health.altman_z_score < 1.8
                      ? "text-financial-loss"
                      : "text-content"
                  )}
                >
                  {financial_health?.altman_z_score
                    ? `${financial_health.altman_z_score.toFixed(2)} (${financial_health.altman_z_score > 3 ? "Safe" : "Distress Zone"})`
                    : "DATA UNAVAILABLE"}
                </span>
              </div>
              <div className="flex items-center justify-between">
                <span className="text-content-muted">Solvency Grade:</span>
                <span className="font-bold text-primary">
                  {financial_health?.health_score || "STABLE"}
                </span>
              </div>
            </div>
          </div>
        </div>
      </CardContent>
    </Card>
  );
};
