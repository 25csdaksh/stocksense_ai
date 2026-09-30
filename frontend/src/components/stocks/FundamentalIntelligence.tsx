"use client";

import React, { useState } from "react";
import { useStockFundamentals } from "@/hooks/useStockFundamentals";
import { Card, CardHeader, CardTitle, CardDescription, CardContent } from "@/components/common/Card";
import { Badge } from "@/components/common/Badge";
import { Skeleton } from "@/components/common/Skeleton";
import { Button } from "@/components/common/Button";
import {
  FileText,
  DollarSign,
  Percent,
  ShieldCheck,
  AlertCircle,
  RefreshCw,
  TrendingUp,
  BarChart3,
  Scale,
  Wallet,
} from "lucide-react";
import { cn } from "@/lib/utils";

export interface FundamentalIntelligenceProps {
  ticker: string;
  isDemo?: boolean;
}

export const FundamentalIntelligence: React.FC<FundamentalIntelligenceProps> = ({
  ticker,
  isDemo: parentDemo = false,
}) => {
  const [statementTab, setStatementTab] = useState<"income" | "balance_sheet" | "cash_flow">("income");
  const {
    fundamentals,
    incomeStatements,
    balanceSheets,
    cashFlowStatements,
    profile,
    periodType,
    setPeriodType,
    isLoading,
    isError,
    error,
    isDemo,
    isUnavailable,
    refresh,
  } = useStockFundamentals(ticker);

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
  const isIndian = ticker.endsWith(".NS") || ticker.endsWith(".BO") || fundamentals.currency === "INR";

  // Helper function to format large corporate financial numbers
  const formatCurrency = (val?: number | null) => {
    if (val === undefined || val === null || isNaN(val)) return "—";
    const absVal = Math.abs(val);
    const sign = val < 0 ? "-" : "";

    if (isIndian) {
      if (absVal >= 1e7) {
        return `${sign}₹${(absVal / 1e7).toLocaleString("en-IN", { maximumFractionDigits: 2 })} Cr`;
      } else if (absVal >= 1e5) {
        return `${sign}₹${(absVal / 1e5).toLocaleString("en-IN", { maximumFractionDigits: 2 })} L`;
      }
      return `${sign}₹${absVal.toLocaleString("en-IN")}`;
    } else {
      if (absVal >= 1e9) {
        return `${sign}$${(absVal / 1e9).toFixed(2)}B`;
      } else if (absVal >= 1e6) {
        return `${sign}$${(absVal / 1e6).toFixed(2)}M`;
      }
      return `${sign}$${absVal.toLocaleString("en-US")}`;
    }
  };

  const activeStatement =
    statementTab === "income"
      ? incomeStatements
      : statementTab === "balance_sheet"
      ? balanceSheets
      : cashFlowStatements;

  return (
    <Card className="border-border shadow-card">
      <CardHeader className="pb-3 border-b border-border/60 flex flex-col sm:flex-row sm:items-center justify-between gap-3">
        <div>
          <div className="flex flex-wrap items-center gap-2">
            <CardTitle className="text-lg font-bold flex items-center gap-2 text-content">
              <FileText className="w-5 h-5 text-primary" />
              Fundamental & Financial Statement Intelligence
            </CardTitle>
            {displayDemo && (
              <Badge variant="gold" size="sm">
                DEMO DATA
              </Badge>
            )}
            {isUnavailable && (
              <Badge variant="loss" size="sm">
                DATA UNAVAILABLE
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
          <CardDescription className="text-xs text-content-muted mt-1">
            Audited financial ratios, cash generation capacity, capital efficiency, and multi-period statements
          </CardDescription>
        </div>

        <div className="flex items-center gap-2 self-end sm:self-center">
          {/* Annual / Quarterly Period Toggle */}
          <div className="flex items-center bg-surface-subtle p-1 rounded-lg border border-border text-xs">
            <button
              onClick={() => setPeriodType("annual")}
              className={cn(
                "px-2.5 py-1 rounded-md font-semibold transition-colors",
                periodType === "annual"
                  ? "bg-surface shadow-sm text-primary font-bold"
                  : "text-content-muted hover:text-content"
              )}
            >
              Annual
            </button>
            <button
              onClick={() => setPeriodType("quarterly")}
              className={cn(
                "px-2.5 py-1 rounded-md font-semibold transition-colors",
                periodType === "quarterly"
                  ? "bg-surface shadow-sm text-primary font-bold"
                  : "text-content-muted hover:text-content"
              )}
            >
              Quarterly
            </button>
          </div>

          <button
            onClick={() => refresh()}
            className="p-2 rounded-lg text-content-muted hover:text-content hover:bg-surface-subtle transition-colors border border-border"
            title="Refresh Fundamentals"
          >
            <RefreshCw className="w-3.5 h-3.5" />
          </button>
        </div>
      </CardHeader>

      <CardContent className="pt-4 space-y-6">
        {/* Key Ratios Cards Grid */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          {/* 1. Valuation Multiples */}
          <div className="p-4 rounded-xl bg-surface-subtle/70 border border-border space-y-3">
            <div className="flex items-center justify-between border-b border-border/60 pb-2">
              <span className="text-xs font-bold text-content flex items-center gap-1.5">
                <DollarSign className="w-4 h-4 text-primary" />
                Valuation Multiples
              </span>
              <span className="text-[10px] text-content-muted font-semibold">TTM / Forward</span>
            </div>
            <div className="space-y-2 font-tabular text-xs">
              <div className="flex items-center justify-between">
                <span className="text-content-muted">P/E Ratio (TTM):</span>
                <span className="font-bold text-content">
                  {valuation?.pe_ratio ? `${valuation.pe_ratio.toFixed(1)}x` : "—"}
                </span>
              </div>
              <div className="flex items-center justify-between">
                <span className="text-content-muted">Forward P/E:</span>
                <span className="font-bold text-content">
                  {valuation?.forward_pe ? `${valuation.forward_pe.toFixed(1)}x` : "—"}
                </span>
              </div>
              <div className="flex items-center justify-between">
                <span className="text-content-muted">Price to Book (P/B):</span>
                <span className="font-bold text-content">
                  {valuation?.pb_ratio ? `${valuation.pb_ratio.toFixed(2)}x` : "—"}
                </span>
              </div>
              <div className="flex items-center justify-between">
                <span className="text-content-muted">EV / EBITDA:</span>
                <span className="font-bold text-content">
                  {valuation?.ev_ebitda ? `${valuation.ev_ebitda.toFixed(1)}x` : "—"}
                </span>
              </div>
              <div className="flex items-center justify-between">
                <span className="text-content-muted">FCF Yield:</span>
                <span className="font-bold text-financial-gain">
                  {valuation?.fcf_yield_pct ? `${valuation.fcf_yield_pct.toFixed(1)}%` : "—"}
                </span>
              </div>
            </div>
          </div>

          {/* 2. Profitability & Margins */}
          <div className="p-4 rounded-xl bg-surface-subtle/70 border border-border space-y-3">
            <div className="flex items-center justify-between border-b border-border/60 pb-2">
              <span className="text-xs font-bold text-content flex items-center gap-1.5">
                <Percent className="w-4 h-4 text-primary" />
                Profitability & Margins
              </span>
              <span className="text-[10px] text-content-muted font-semibold">Efficiency</span>
            </div>
            <div className="space-y-2 font-tabular text-xs">
              <div className="flex items-center justify-between">
                <span className="text-content-muted">Gross Margin:</span>
                <span className="font-bold text-content">
                  {profitability?.gross_margin_pct ? `${profitability.gross_margin_pct.toFixed(1)}%` : "—"}
                </span>
              </div>
              <div className="flex items-center justify-between">
                <span className="text-content-muted">Operating Margin:</span>
                <span className="font-bold text-content">
                  {profitability?.operating_margin_pct ? `${profitability.operating_margin_pct.toFixed(1)}%` : "—"}
                </span>
              </div>
              <div className="flex items-center justify-between">
                <span className="text-content-muted">Net Margin:</span>
                <span className="font-bold text-content">
                  {profitability?.net_margin_pct ? `${profitability.net_margin_pct.toFixed(1)}%` : "—"}
                </span>
              </div>
              <div className="flex items-center justify-between">
                <span className="text-content-muted">Return on Equity (ROE):</span>
                <span className="font-bold text-financial-gain">
                  {profitability?.roe_pct ? `${profitability.roe_pct.toFixed(1)}%` : "—"}
                </span>
              </div>
              <div className="flex items-center justify-between">
                <span className="text-content-muted">Return on Assets (ROA):</span>
                <span className="font-bold text-content">
                  {profitability?.roa_pct ? `${profitability.roa_pct.toFixed(1)}%` : "—"}
                </span>
              </div>
            </div>
          </div>

          {/* 3. Financial Health & Solvency */}
          <div className="p-4 rounded-xl bg-surface-subtle/70 border border-border space-y-3">
            <div className="flex items-center justify-between border-b border-border/60 pb-2">
              <span className="text-xs font-bold text-content flex items-center gap-1.5">
                <ShieldCheck className="w-4 h-4 text-primary" />
                Financial Health & Solvency
              </span>
              <span className="text-[10px] text-content-muted font-semibold">Risk & Leverage</span>
            </div>
            <div className="space-y-2 font-tabular text-xs">
              <div className="flex items-center justify-between">
                <span className="text-content-muted">Debt / Equity:</span>
                <span className="font-bold text-content">
                  {financial_health?.debt_to_equity !== undefined && financial_health?.debt_to_equity !== null
                    ? `${financial_health.debt_to_equity.toFixed(2)}`
                    : "—"}
                </span>
              </div>
              <div className="flex items-center justify-between">
                <span className="text-content-muted">Current Ratio:</span>
                <span className="font-bold text-content">
                  {financial_health?.current_ratio ? `${financial_health.current_ratio.toFixed(2)}` : "—"}
                </span>
              </div>
              <div className="flex items-center justify-between">
                <span className="text-content-muted">Interest Coverage:</span>
                <span className="font-bold text-content">
                  {financial_health?.interest_coverage_ratio
                    ? `${financial_health.interest_coverage_ratio.toFixed(1)}x`
                    : "—"}
                </span>
              </div>
              <div className="flex items-center justify-between">
                <span className="text-content-muted">Altman Z-Score:</span>
                <span className="font-bold text-content">
                  {financial_health?.altman_z_score ? `${financial_health.altman_z_score.toFixed(2)}` : "—"}
                </span>
              </div>
              <div className="flex items-center justify-between">
                <span className="text-content-muted">Health Rating:</span>
                <span className="font-bold text-financial-gain">
                  {financial_health?.health_score || "HEALTHY"}
                </span>
              </div>
            </div>
          </div>
        </div>

        {/* Multi-Period Financial Statements Explorer */}
        <div className="border border-border rounded-xl p-4 bg-surface space-y-4">
          <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 border-b border-border/60 pb-3">
            <div className="flex items-center gap-2">
              <BarChart3 className="w-4 h-4 text-primary" />
              <span className="text-sm font-bold text-content">
                Financial Statement Line Items ({periodType === "annual" ? "Annual Filings" : "Quarterly Reports"})
              </span>
            </div>

            {/* Statement Type Tabs */}
            <div className="flex items-center bg-surface-subtle p-1 rounded-lg border border-border text-xs">
              <button
                onClick={() => setStatementTab("income")}
                className={cn(
                  "px-3 py-1 rounded-md font-semibold transition-colors",
                  statementTab === "income"
                    ? "bg-surface shadow-sm text-primary font-bold"
                    : "text-content-muted hover:text-content"
                )}
              >
                Income Statement
              </button>
              <button
                onClick={() => setStatementTab("balance_sheet")}
                className={cn(
                  "px-3 py-1 rounded-md font-semibold transition-colors",
                  statementTab === "balance_sheet"
                    ? "bg-surface shadow-sm text-primary font-bold"
                    : "text-content-muted hover:text-content"
                )}
              >
                Balance Sheet
              </button>
              <button
                onClick={() => setStatementTab("cash_flow")}
                className={cn(
                  "px-3 py-1 rounded-md font-semibold transition-colors",
                  statementTab === "cash_flow"
                    ? "bg-surface shadow-sm text-primary font-bold"
                    : "text-content-muted hover:text-content"
                )}
              >
                Cash Flow
              </button>
            </div>
          </div>

          {/* Dynamic Financial Table */}
          {activeStatement && activeStatement.periods && activeStatement.periods.length > 0 ? (
            <div className="overflow-x-auto">
              <table className="w-full text-left text-xs font-tabular border-collapse">
                <thead>
                  <tr className="border-b border-border text-content-muted uppercase tracking-wider text-[10px]">
                    <th className="py-2.5 px-3 font-semibold">Line Item</th>
                    {activeStatement.periods.map((p, idx) => (
                      <th key={idx} className="py-2.5 px-3 font-semibold text-right">
                        {p.period || `Period ${idx + 1}`}
                      </th>
                    ))}
                  </tr>
                </thead>
                <tbody className="divide-y divide-border/60">
                  {statementTab === "income" && (
                    <>
                      <tr className="hover:bg-surface-subtle/50 font-semibold text-content">
                        <td className="py-2.5 px-3">Total Revenue</td>
                        {activeStatement.periods.map((p, idx) => (
                          <td key={idx} className="py-2.5 px-3 text-right">
                            {formatCurrency(p.revenue ?? p.total_revenue)}
                          </td>
                        ))}
                      </tr>
                      <tr className="hover:bg-surface-subtle/50 text-content">
                        <td className="py-2.5 px-3 pl-6 text-content-muted">Cost of Revenue</td>
                        {activeStatement.periods.map((p, idx) => (
                          <td key={idx} className="py-2.5 px-3 text-right">
                            {formatCurrency(p.cost_of_revenue)}
                          </td>
                        ))}
                      </tr>
                      <tr className="hover:bg-surface-subtle/50 font-medium text-content">
                        <td className="py-2.5 px-3">Gross Profit</td>
                        {activeStatement.periods.map((p, idx) => (
                          <td key={idx} className="py-2.5 px-3 text-right text-financial-gain">
                            {formatCurrency(p.gross_profit)}
                          </td>
                        ))}
                      </tr>
                      <tr className="hover:bg-surface-subtle/50 text-content">
                        <td className="py-2.5 px-3 pl-6 text-content-muted">Operating Expenses</td>
                        {activeStatement.periods.map((p, idx) => (
                          <td key={idx} className="py-2.5 px-3 text-right">
                            {formatCurrency(p.operating_expenses)}
                          </td>
                        ))}
                      </tr>
                      <tr className="hover:bg-surface-subtle/50 font-semibold text-content">
                        <td className="py-2.5 px-3">Operating Income (EBIT)</td>
                        {activeStatement.periods.map((p, idx) => (
                          <td key={idx} className="py-2.5 px-3 text-right">
                            {formatCurrency(p.operating_income ?? p.ebit)}
                          </td>
                        ))}
                      </tr>
                      <tr className="hover:bg-surface-subtle/50 font-semibold text-content">
                        <td className="py-2.5 px-3">EBITDA</td>
                        {activeStatement.periods.map((p, idx) => (
                          <td key={idx} className="py-2.5 px-3 text-right">
                            {formatCurrency(p.ebitda)}
                          </td>
                        ))}
                      </tr>
                      <tr className="hover:bg-surface-subtle/50 text-content">
                        <td className="py-2.5 px-3 pl-6 text-content-muted">Interest Expense</td>
                        {activeStatement.periods.map((p, idx) => (
                          <td key={idx} className="py-2.5 px-3 text-right">
                            {formatCurrency(p.interest_expense)}
                          </td>
                        ))}
                      </tr>
                      <tr className="hover:bg-surface-subtle/50 text-content">
                        <td className="py-2.5 px-3 pl-6 text-content-muted">Tax Expense</td>
                        {activeStatement.periods.map((p, idx) => (
                          <td key={idx} className="py-2.5 px-3 text-right">
                            {formatCurrency(p.tax_expense)}
                          </td>
                        ))}
                      </tr>
                      <tr className="hover:bg-surface-subtle/50 font-bold text-primary bg-primary/5">
                        <td className="py-2.5 px-3">Net Income</td>
                        {activeStatement.periods.map((p, idx) => (
                          <td key={idx} className="py-2.5 px-3 text-right text-financial-gain">
                            {formatCurrency(p.net_income)}
                          </td>
                        ))}
                      </tr>
                      <tr className="hover:bg-surface-subtle/50 text-content font-semibold">
                        <td className="py-2.5 px-3">Earnings Per Share (EPS)</td>
                        {activeStatement.periods.map((p, idx) => (
                          <td key={idx} className="py-2.5 px-3 text-right">
                            {p.eps ? (isIndian ? `₹${p.eps.toFixed(2)}` : `$${p.eps.toFixed(2)}`) : "—"}
                          </td>
                        ))}
                      </tr>
                    </>
                  )}

                  {statementTab === "balance_sheet" && (
                    <>
                      <tr className="hover:bg-surface-subtle/50 text-content">
                        <td className="py-2.5 px-3 pl-6 text-content-muted">Cash & Equivalents</td>
                        {activeStatement.periods.map((p, idx) => (
                          <td key={idx} className="py-2.5 px-3 text-right">
                            {formatCurrency(p.cash_and_equivalents ?? p.cash)}
                          </td>
                        ))}
                      </tr>
                      <tr className="hover:bg-surface-subtle/50 text-content">
                        <td className="py-2.5 px-3 pl-6 text-content-muted">Total Current Assets</td>
                        {activeStatement.periods.map((p, idx) => (
                          <td key={idx} className="py-2.5 px-3 text-right">
                            {formatCurrency(p.total_current_assets)}
                          </td>
                        ))}
                      </tr>
                      <tr className="hover:bg-surface-subtle/50 font-bold text-content">
                        <td className="py-2.5 px-3">Total Assets</td>
                        {activeStatement.periods.map((p, idx) => (
                          <td key={idx} className="py-2.5 px-3 text-right">
                            {formatCurrency(p.total_assets)}
                          </td>
                        ))}
                      </tr>
                      <tr className="hover:bg-surface-subtle/50 text-content">
                        <td className="py-2.5 px-3 pl-6 text-content-muted">Current Liabilities</td>
                        {activeStatement.periods.map((p, idx) => (
                          <td key={idx} className="py-2.5 px-3 text-right">
                            {formatCurrency(p.current_liabilities)}
                          </td>
                        ))}
                      </tr>
                      <tr className="hover:bg-surface-subtle/50 text-content">
                        <td className="py-2.5 px-3 pl-6 text-content-muted">Total Debt</td>
                        {activeStatement.periods.map((p, idx) => (
                          <td key={idx} className="py-2.5 px-3 text-right">
                            {formatCurrency(p.total_debt)}
                          </td>
                        ))}
                      </tr>
                      <tr className="hover:bg-surface-subtle/50 font-bold text-content">
                        <td className="py-2.5 px-3">Total Liabilities</td>
                        {activeStatement.periods.map((p, idx) => (
                          <td key={idx} className="py-2.5 px-3 text-right">
                            {formatCurrency(p.total_liabilities)}
                          </td>
                        ))}
                      </tr>
                      <tr className="hover:bg-surface-subtle/50 font-bold text-primary bg-primary/5">
                        <td className="py-2.5 px-3">Total Stockholders Equity</td>
                        {activeStatement.periods.map((p, idx) => (
                          <td key={idx} className="py-2.5 px-3 text-right text-financial-gain">
                            {formatCurrency(p.total_equity ?? p.stockholders_equity)}
                          </td>
                        ))}
                      </tr>
                    </>
                  )}

                  {statementTab === "cash_flow" && (
                    <>
                      <tr className="hover:bg-surface-subtle/50 font-semibold text-content">
                        <td className="py-2.5 px-3">Operating Cash Flow (OCF)</td>
                        {activeStatement.periods.map((p, idx) => (
                          <td key={idx} className="py-2.5 px-3 text-right text-financial-gain">
                            {formatCurrency(p.operating_cash_flow)}
                          </td>
                        ))}
                      </tr>
                      <tr className="hover:bg-surface-subtle/50 text-content">
                        <td className="py-2.5 px-3 pl-6 text-content-muted">Capital Expenditures (CapEx)</td>
                        {activeStatement.periods.map((p, idx) => (
                          <td key={idx} className="py-2.5 px-3 text-right">
                            {formatCurrency(p.capital_expenditures)}
                          </td>
                        ))}
                      </tr>
                      <tr className="hover:bg-surface-subtle/50 font-bold text-primary bg-primary/5">
                        <td className="py-2.5 px-3">Free Cash Flow (FCF)</td>
                        {activeStatement.periods.map((p, idx) => (
                          <td key={idx} className="py-2.5 px-3 text-right text-financial-gain">
                            {formatCurrency(p.free_cash_flow)}
                          </td>
                        ))}
                      </tr>
                      <tr className="hover:bg-surface-subtle/50 text-content">
                        <td className="py-2.5 px-3 pl-6 text-content-muted">Cash Dividends Paid</td>
                        {activeStatement.periods.map((p, idx) => (
                          <td key={idx} className="py-2.5 px-3 text-right">
                            {formatCurrency(p.dividends_paid)}
                          </td>
                        ))}
                      </tr>
                    </>
                  )}
                </tbody>
              </table>
            </div>
          ) : (
            <div className="py-6 text-center text-xs text-content-muted">
              No statement periods available for {periodType} reporting frequency.
            </div>
          )}
        </div>

        {/* Data Provenance & Freshness Footer */}
        <div className="flex flex-wrap items-center justify-between text-[11px] text-content-muted pt-2 border-t border-border/60">
          <div className="flex items-center gap-3">
            <span>
              DATA SOURCE:{" "}
              <strong className="text-content font-semibold">
                {fundamentals?.data_source || "DEMO"}
              </strong>
            </span>
            <span>•</span>
            <span>
              STATUS:{" "}
              <strong
                className={cn(
                  "font-semibold",
                  fundamentals?.data_status === "LIVE"
                    ? "text-financial-gain"
                    : "text-gold"
                )}
              >
                {fundamentals?.data_status || "DEMO"}
              </strong>
            </span>
          </div>
          <div>
            <span>
              LAST UPDATED:{" "}
              {fundamentals?.updated_at
                ? new Date(fundamentals.updated_at).toLocaleTimeString()
                : "Just now"}
            </span>
          </div>
        </div>
      </CardContent>
    </Card>
  );
};
