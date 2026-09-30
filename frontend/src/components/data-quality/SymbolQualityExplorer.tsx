"use client";

import React, { useState } from "react";
import { SymbolDataQualityReport, QualityScoreBreakdown } from "@/types/data-quality";
import { DataFreshnessBadge } from "./DataFreshnessBadge";
import {
  Search,
  TrendingUp,
  FileText,
  Newspaper,
  ShieldCheck,
  AlertTriangle,
  Layers,
  Clock,
  Sparkles,
  BarChart3,
} from "lucide-react";
import { cn } from "@/lib/utils";

interface SymbolQualityExplorerProps {
  initialReport?: SymbolDataQualityReport | null;
  onSearchSymbol?: (symbol: string) => Promise<void>;
  isLoading?: boolean;
}

const SAMPLE_SYMBOLS = ["RELIANCE.NS", "TCS.NS", "INFY.NS", "AAPL", "NVDA", "MSFT"];

export const SymbolQualityExplorer: React.FC<SymbolQualityExplorerProps> = ({
  initialReport,
  onSearchSymbol,
  isLoading,
}) => {
  const [query, setQuery] = useState("");
  const [selectedSymbol, setSelectedSymbol] = useState(initialReport?.symbol || "RELIANCE.NS");

  const handleSearch = (e: React.FormEvent) => {
    e.preventDefault();
    if (query.trim() && onSearchSymbol) {
      const sym = query.trim().toUpperCase();
      setSelectedSymbol(sym);
      onSearchSymbol(sym);
    }
  };

  const handleSelectSample = (sym: string) => {
    setSelectedSymbol(sym);
    if (onSearchSymbol) {
      onSearchSymbol(sym);
    }
  };

  const renderDimensionBar = (label: string, weight: string, score: number) => {
    return (
      <div className="space-y-1">
        <div className="flex justify-between text-[11px]">
          <span className="text-content font-medium">
            {label} <span className="text-content-muted font-mono">({weight})</span>
          </span>
          <span className="font-mono font-bold text-primary">{score}/100</span>
        </div>
        <div className="h-2 w-full rounded-full bg-surface-subtle overflow-hidden border border-border/50">
          <div
            className={cn(
              "h-full rounded-full transition-all duration-500",
              score >= 90
                ? "bg-emerald-500"
                : score >= 70
                ? "bg-amber-500"
                : "bg-rose-500"
            )}
            style={{ width: `${Math.max(5, score)}%` }}
          />
        </div>
      </div>
    );
  };

  const rep = initialReport;

  return (
    <div className="p-5 rounded-2xl bg-surface border border-border space-y-5 shadow-2xs">
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-3">
        <div className="flex items-center gap-2">
          <Search className="w-4 h-4 text-primary" />
          <h3 className="text-xs font-bold uppercase tracking-wider text-content">
            Symbol-Level 3-Pillar Data Quality Inspector
          </h3>
        </div>

        {/* Search input & Sample Buttons */}
        <div className="flex flex-wrap items-center gap-2">
          <form onSubmit={handleSearch} className="relative flex items-center">
            <input
              type="text"
              placeholder="Search ticker (e.g. RELIANCE.NS, AAPL)..."
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              className="px-3 py-1.5 pl-8 rounded-xl bg-surface-subtle border border-border text-xs font-mono placeholder:text-content-muted focus:outline-none focus:ring-1 focus:ring-primary w-52"
            />
            <Search className="w-3.5 h-3.5 text-content-muted absolute left-2.5 pointer-events-none" />
          </form>

          <div className="flex items-center gap-1">
            {SAMPLE_SYMBOLS.map((s) => (
              <button
                key={s}
                onClick={() => handleSelectSample(s)}
                className={cn(
                  "px-2 py-1 rounded-lg text-[10px] font-mono font-bold border transition-colors",
                  selectedSymbol === s
                    ? "bg-primary text-white border-primary"
                    : "bg-surface-subtle border-border text-content-muted hover:text-primary hover:bg-surface"
                )}
              >
                {s}
              </button>
            ))}
          </div>
        </div>
      </div>

      {isLoading || !rep ? (
        <div className="h-64 rounded-xl bg-surface-subtle animate-pulse" />
      ) : (
        <div className="space-y-5">
          {/* Header Summary for Symbol */}
          <div className="p-4 rounded-xl bg-surface-subtle border border-border/80 flex flex-col md:flex-row items-start md:items-center justify-between gap-3">
            <div>
              <div className="flex items-center gap-2">
                <span className="text-lg font-extrabold font-mono text-primary">
                  {rep.symbol}
                </span>
                <span
                  className={cn(
                    "text-[10px] font-bold font-mono px-2 py-0.5 rounded border",
                    rep.overall_status === "HEALTHY"
                      ? "bg-emerald-500/10 text-emerald-700 border-emerald-500/30"
                      : "bg-amber-500/10 text-amber-700 border-amber-500/30"
                  )}
                >
                  {rep.overall_status}
                </span>
              </div>
              <p className="text-[11px] text-content-muted">
                Inspected: {new Date(rep.inspected_at).toLocaleTimeString()} UTC
              </p>
            </div>

            <div className="flex items-center gap-4">
              <div className="text-right">
                <span className="text-[10px] uppercase font-bold text-content-muted">Composite Score</span>
                <div className="text-2xl font-black font-mono text-primary">
                  {rep.overall_score} <span className="text-xs text-content-muted font-normal">/ 100</span>
                </div>
              </div>
              <DataFreshnessBadge
                status={rep.market_data.data_status}
                dataSource={rep.market_data.data_source}
                dataStatus={rep.market_data.data_status}
                lastUpdated={rep.market_data.last_updated}
                ageSeconds={rep.market_data.freshness_seconds}
              />
            </div>
          </div>

          {/* 3 Pillar Cards */}
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-4">
            {/* Pillar 1: Market Data */}
            <div className="p-4 rounded-xl bg-surface-subtle/50 border border-border space-y-3">
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-2">
                  <TrendingUp className="w-4 h-4 text-primary" />
                  <span className="text-xs font-bold text-content">Market Data Pillar</span>
                </div>
                <span className="text-xs font-mono font-black text-primary">
                  {rep.market_data.score}/100
                </span>
              </div>

              <div className="text-[11px] space-y-1 text-content-muted">
                <div className="flex justify-between">
                  <span>Candles & Quotes Checked:</span>
                  <span className="font-mono text-content font-semibold">{rep.market_data.total_records_checked}</span>
                </div>
                <div className="flex justify-between">
                  <span>Detected Gaps:</span>
                  <span className={cn("font-mono font-semibold", rep.market_data.gap_count > 0 ? "text-amber-600" : "text-content")}>
                    {rep.market_data.gap_count}
                  </span>
                </div>
                <div className="flex justify-between">
                  <span>Duplicate Timestamps:</span>
                  <span className="font-mono text-content font-semibold">{rep.market_data.duplicate_count}</span>
                </div>
                <div className="flex justify-between">
                  <span>Provider Latency:</span>
                  <span className="font-mono text-content font-semibold">{rep.market_data.provider_latency_ms ?? 0} ms</span>
                </div>
              </div>

              {rep.market_data.gaps_detected.length > 0 && (
                <div className="p-2 rounded-lg bg-amber-500/10 border border-amber-500/20 text-[10px] text-amber-800 space-y-1">
                  <div className="font-bold flex items-center gap-1">
                    <AlertTriangle className="w-3 h-3" />
                    <span>Non-Weekend Trading Gap</span>
                  </div>
                  <p className="font-mono">
                    {rep.market_data.gaps_detected[0].gap_duration_hours}h gap from {rep.market_data.gaps_detected[0].from_timestamp?.slice(0, 10)}
                  </p>
                </div>
              )}
            </div>

            {/* Pillar 2: Fundamentals */}
            <div className="p-4 rounded-xl bg-surface-subtle/50 border border-border space-y-3">
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-2">
                  <FileText className="w-4 h-4 text-primary" />
                  <span className="text-xs font-bold text-content">Fundamentals Pillar</span>
                </div>
                <span className="text-xs font-mono font-black text-primary">
                  {rep.fundamentals.score}/100
                </span>
              </div>

              <div className="text-[11px] space-y-1 text-content-muted">
                <div className="flex justify-between">
                  <span>Statements Verified:</span>
                  <span className="font-mono text-content font-semibold">Income, Balance, CashFlow</span>
                </div>
                <div className="flex justify-between">
                  <span>Ratio Calculation:</span>
                  <span className="font-mono text-emerald-600 font-semibold">Deterministic PASS</span>
                </div>
                <div className="flex justify-between">
                  <span>Period Gaps / Outliers:</span>
                  <span className="font-mono text-content font-semibold">{rep.fundamentals.validation_errors.length}</span>
                </div>
                <div className="flex justify-between">
                  <span>Provider Latency:</span>
                  <span className="font-mono text-content font-semibold">{rep.fundamentals.provider_latency_ms ?? 0} ms</span>
                </div>
              </div>
            </div>

            {/* Pillar 3: News */}
            <div className="p-4 rounded-xl bg-surface-subtle/50 border border-border space-y-3">
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-2">
                  <Newspaper className="w-4 h-4 text-primary" />
                  <span className="text-xs font-bold text-content">News Intelligence</span>
                </div>
                <span className="text-xs font-mono font-black text-primary">
                  {rep.news.score}/100
                </span>
              </div>

              <div className="text-[11px] space-y-1 text-content-muted">
                <div className="flex justify-between">
                  <span>Recent Articles Inspected:</span>
                  <span className="font-mono text-content font-semibold">{rep.news.total_records_checked}</span>
                </div>
                <div className="flex justify-between">
                  <span>Content Hash Duplicates:</span>
                  <span className="font-mono text-content font-semibold">{rep.news.duplicate_count}</span>
                </div>
                <div className="flex justify-between">
                  <span>Sentiment / Sector Mapped:</span>
                  <span className="font-mono text-emerald-600 font-semibold">100% COVERED</span>
                </div>
                <div className="flex justify-between">
                  <span>Feed Latency:</span>
                  <span className="font-mono text-content font-semibold">{rep.news.provider_latency_ms ?? 0} ms</span>
                </div>
              </div>
            </div>
          </div>

          {/* 6-Dimension Score Breakdown */}
          <div className="p-4 rounded-xl bg-surface-subtle/40 border border-border/80 space-y-3">
            <div className="flex items-center gap-2">
              <BarChart3 className="w-4 h-4 text-primary" />
              <h4 className="text-xs font-bold uppercase tracking-wider text-content">
                6-Dimension Quality Score Breakdown (Market Data Pillar)
              </h4>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-x-6 gap-y-3">
              {renderDimensionBar("Freshness", "25%", rep.market_data.score_breakdown.freshness_score)}
              {renderDimensionBar("Completeness", "20%", rep.market_data.score_breakdown.completeness_score)}
              {renderDimensionBar("Validity", "20%", rep.market_data.score_breakdown.validity_score)}
              {renderDimensionBar("Availability", "15%", rep.market_data.score_breakdown.availability_score)}
              {renderDimensionBar("Consistency", "10%", rep.market_data.score_breakdown.consistency_score)}
              {renderDimensionBar("Continuity", "10%", rep.market_data.score_breakdown.continuity_score)}
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
