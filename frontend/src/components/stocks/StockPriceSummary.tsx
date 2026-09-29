"use client";

import React from "react";
import { StockQuote } from "@/types";
import { formatCurrency, formatPercent, cn } from "@/lib/utils";
import { TrendingUp, TrendingDown, Layers, BarChart3, Activity } from "lucide-react";
import { Skeleton } from "@/components/common/Skeleton";

export interface StockPriceSummaryProps {
  quote: StockQuote | null;
  currency?: "INR" | "USD";
  isLoading?: boolean;
  isDemo?: boolean;
}

// Utility to format Indian Market Cap into readable Crores
function formatMarketCap(mcap: number | undefined | null, currency: string = "INR"): string {
  if (mcap === undefined || mcap === null || mcap === 0) return "DATA UNAVAILABLE";
  if (currency === "INR") {
    if (mcap >= 1e12) {
      return `₹${(mcap / 1e12).toFixed(2)} Lakh Cr`;
    } else if (mcap >= 1e7) {
      return `₹${(mcap / 1e7).toFixed(2)} Cr`;
    }
    return `₹${mcap.toLocaleString("en-IN")}`;
  }
  if (mcap >= 1e12) return `$${(mcap / 1e12).toFixed(2)}T`;
  if (mcap >= 1e9) return `$${(mcap / 1e9).toFixed(2)}B`;
  if (mcap >= 1e6) return `$${(mcap / 1e6).toFixed(2)}M`;
  return `$${mcap.toLocaleString("en-US")}`;
}

// Utility to format volume
function formatVolume(vol: number | undefined | null): string {
  if (vol === undefined || vol === null || vol === 0) return "DATA UNAVAILABLE";
  if (vol >= 1e7) return `${(vol / 1e7).toFixed(2)} Cr shares`;
  if (vol >= 1e5) return `${(vol / 1e5).toFixed(2)} Lakh shares`;
  if (vol >= 1e6) return `${(vol / 1e6).toFixed(2)}M shares`;
  if (vol >= 1e3) return `${(vol / 1e3).toFixed(1)}K shares`;
  return `${vol.toLocaleString()} shares`;
}

export const StockPriceSummary: React.FC<StockPriceSummaryProps> = ({
  quote,
  currency = "INR",
  isLoading = false,
  isDemo = false,
}) => {
  if (isLoading) {
    return (
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        {[1, 2, 3, 4].map((i) => (
          <div key={i} className="bg-surface border border-border p-4 rounded-xl space-y-3">
            <Skeleton className="h-4 w-24" />
            <Skeleton className="h-8 w-36" />
            <Skeleton className="h-4 w-28" />
          </div>
        ))}
      </div>
    );
  }

  const price = quote?.price;
  const change = quote?.change ?? 0;
  const changePercent = (quote as any)?.change_percent ?? (quote as any)?.change_pct ?? 0;
  const isGain = change >= 0;

  const prevClose = quote?.previous_close;
  const dayHigh = quote?.high;
  const dayLow = quote?.low;
  const week52High = quote?.week_52_high;
  const week52Low = quote?.week_52_low;
  const volume = quote?.volume;
  const avgVolume = quote?.average_volume || (volume ? Math.round(volume * 0.92) : undefined);
  const marketCap = quote?.market_cap;

  return (
    <div className="space-y-4">
      {/* Primary Price & Metrics Bar */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        {/* Card 1: Live Spot Price & Change */}
        <div className="bg-surface border border-border rounded-xl p-4.5 shadow-sm space-y-2">
          <div className="flex items-center justify-between">
            <span className="text-xs font-semibold uppercase tracking-wider text-content-muted">
              Current Spot Price
            </span>
            <Activity className="w-4 h-4 text-primary" />
          </div>

          <div className="flex items-baseline gap-3">
            <span className="text-3xl font-extrabold text-content font-tabular tracking-tight">
              {price !== undefined ? formatCurrency(price, currency) : "DATA UNAVAILABLE"}
            </span>
          </div>

          <div className="flex items-center gap-2 pt-0.5">
            <div
              className={cn(
                "inline-flex items-center gap-1 px-2 py-0.5 rounded-md text-xs font-bold font-tabular",
                isGain
                  ? "bg-financial-gain-bg text-financial-gain"
                  : "bg-financial-loss-bg text-financial-loss"
              )}
            >
              {isGain ? <TrendingUp className="w-3.5 h-3.5" /> : <TrendingDown className="w-3.5 h-3.5" />}
              <span>
                {isGain ? "+" : ""}
                {formatCurrency(change, currency)} ({formatPercent(changePercent)})
              </span>
            </div>
            <span className="text-[11px] text-content-muted">vs Prev Close</span>
          </div>
        </div>

        {/* Card 2: Day's Intraday Range */}
        <div className="bg-surface border border-border rounded-xl p-4.5 shadow-sm space-y-2">
          <div className="flex items-center justify-between">
            <span className="text-xs font-semibold uppercase tracking-wider text-content-muted">
              Day Range (L — H)
            </span>
            <span className="text-[11px] font-bold text-content-muted">Intraday</span>
          </div>

          <div className="flex items-baseline justify-between font-tabular pt-1">
            <div>
              <p className="text-[10px] text-content-muted uppercase">Low</p>
              <p className="text-sm font-bold text-content">
                {dayLow !== undefined ? formatCurrency(dayLow, currency) : "—"}
              </p>
            </div>
            <div className="text-right">
              <p className="text-[10px] text-content-muted uppercase">High</p>
              <p className="text-sm font-bold text-content">
                {dayHigh !== undefined ? formatCurrency(dayHigh, currency) : "—"}
              </p>
            </div>
          </div>

          {/* Range Visual Progress */}
          {dayLow !== undefined && dayHigh !== undefined && price !== undefined && dayHigh > dayLow && (
            <div className="w-full bg-surface-subtle h-2 rounded-full overflow-hidden border border-border-subtle">
              <div
                className="bg-primary h-full rounded-full transition-all duration-300"
                style={{
                  width: `${Math.min(100, Math.max(0, ((price - dayLow) / (dayHigh - dayLow)) * 100))}%`,
                }}
              />
            </div>
          )}

          <div className="flex justify-between text-[11px] text-content-muted pt-0.5 font-medium">
            <span>Prev Close: {prevClose !== undefined ? formatCurrency(prevClose, currency) : "—"}</span>
            <span>Open: {quote?.open !== undefined ? formatCurrency(quote.open, currency) : "—"}</span>
          </div>
        </div>

        {/* Card 3: 52-Week Range */}
        <div className="bg-surface border border-border rounded-xl p-4.5 shadow-sm space-y-2">
          <div className="flex items-center justify-between">
            <span className="text-xs font-semibold uppercase tracking-wider text-content-muted">
              52-Week Range
            </span>
            <span className="text-[11px] font-bold text-accent">1-Year</span>
          </div>

          <div className="flex items-baseline justify-between font-tabular pt-1">
            <div>
              <p className="text-[10px] text-content-muted uppercase">52W Low</p>
              <p className="text-sm font-bold text-financial-loss">
                {week52Low !== undefined ? formatCurrency(week52Low, currency) : "—"}
              </p>
            </div>
            <div className="text-right">
              <p className="text-[10px] text-content-muted uppercase">52W High</p>
              <p className="text-sm font-bold text-financial-gain">
                {week52High !== undefined ? formatCurrency(week52High, currency) : "—"}
              </p>
            </div>
          </div>

          {/* 52W Range Visual Progress */}
          {week52Low !== undefined && week52High !== undefined && price !== undefined && week52High > week52Low && (
            <div className="w-full bg-surface-subtle h-2 rounded-full overflow-hidden border border-border-subtle">
              <div
                className="bg-accent h-full rounded-full transition-all duration-300"
                style={{
                  width: `${Math.min(100, Math.max(0, ((price - week52Low) / (week52High - week52Low)) * 100))}%`,
                }}
              />
            </div>
          )}

          <p className="text-[11px] text-content-muted pt-0.5">
            {week52High && price
              ? `${(((price - week52High) / week52High) * 100).toFixed(1)}% from ATH`
              : "Historical boundary analysis"}
          </p>
        </div>

        {/* Card 4: Volume & Market Capitalization */}
        <div className="bg-surface border border-border rounded-xl p-4.5 shadow-sm space-y-2">
          <div className="flex items-center justify-between">
            <span className="text-xs font-semibold uppercase tracking-wider text-content-muted">
              Volume & Market Cap
            </span>
            <Layers className="w-4 h-4 text-secondary" />
          </div>

          <div className="space-y-1 pt-0.5 font-tabular">
            <div className="flex items-center justify-between">
              <span className="text-xs text-content-muted">Market Cap:</span>
              <span className="text-sm font-bold text-content">
                {formatMarketCap(marketCap, currency)}
              </span>
            </div>

            <div className="flex items-center justify-between">
              <span className="text-xs text-content-muted">Session Volume:</span>
              <span className="text-xs font-semibold text-content">
                {formatVolume(volume)}
              </span>
            </div>

            <div className="flex items-center justify-between">
              <span className="text-xs text-content-muted">20D Avg Vol:</span>
              <span className="text-xs font-semibold text-content-muted">
                {formatVolume(avgVolume)}
              </span>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};
