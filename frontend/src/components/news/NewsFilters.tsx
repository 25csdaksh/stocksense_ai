"use client";

import React from "react";
import { NewsFilterState } from "@/hooks/useNewsFilters";
import { Search, Filter, RotateCcw, Globe, Sliders } from "lucide-react";

interface NewsFiltersProps {
  filters: NewsFilterState;
  updateFilter: <K extends keyof NewsFilterState>(key: K, value: NewsFilterState[K]) => void;
  resetFilters: () => void;
  sectorsList: string[];
  totalResults: number;
}

export const NewsFilters: React.FC<NewsFiltersProps> = ({
  filters,
  updateFilter,
  resetFilters,
  sectorsList,
  totalResults,
}) => {
  return (
    <div className="bg-surface p-4 rounded-2xl border border-border shadow-card space-y-3.5">
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-3">
        {/* Search Input */}
        <div className="relative flex-1">
          <Search className="absolute left-3.5 top-1/2 -translate-y-1/2 w-4 h-4 text-content-muted" />
          <input
            type="text"
            placeholder="Search headlines, ticker symbols (TCS.NS, RELIANCE), keywords..."
            value={filters.searchQuery}
            onChange={(e: React.ChangeEvent<HTMLInputElement>) => updateFilter("searchQuery", e.target.value)}
            className="w-full bg-surface-subtle border border-border rounded-xl pl-9 pr-3.5 py-2 text-xs text-content placeholder:text-content-muted focus:outline-none focus:border-primary"
          />
        </div>

        {/* Market Switcher */}
        <div className="inline-flex p-0.5 rounded-xl bg-surface-subtle border border-border shrink-0">
          {(["ALL", "INDIA", "GLOBAL"] as const).map((m) => (
            <button
              key={m}
              onClick={() => updateFilter("market", m)}
              className={`px-3 py-1.5 text-xs font-semibold rounded-lg transition-all ${
                filters.market === m
                  ? "bg-primary text-white shadow-sm"
                  : "text-content-muted hover:text-content"
              }`}
            >
              {m === "ALL" ? "All Markets" : m === "INDIA" ? "India (NSE/BSE)" : "Global / US"}
            </button>
          ))}
        </div>
      </div>

      <div className="flex flex-wrap items-center justify-between gap-3 pt-1 border-t border-border/80">
        {/* Sentiment Filter */}
        <div className="flex flex-wrap items-center gap-1.5">
          <span className="text-[11px] font-semibold text-content-muted mr-1">Sentiment:</span>
          {(["ALL", "POSITIVE", "NEUTRAL", "NEGATIVE"] as const).map((s) => (
            <button
              key={s}
              onClick={() => updateFilter("sentiment", s)}
              className={`px-2.5 py-1 text-[11px] font-semibold rounded-lg border transition-all ${
                filters.sentiment === s
                  ? s === "POSITIVE"
                    ? "bg-financial-gain/10 border-financial-gain text-financial-gain"
                    : s === "NEGATIVE"
                    ? "bg-financial-loss/10 border-financial-loss text-financial-loss"
                    : s === "NEUTRAL"
                    ? "bg-primary/10 border-primary text-primary"
                    : "bg-primary text-white border-primary"
                  : "bg-surface border-border text-content-muted hover:text-content"
              }`}
            >
              {s}
            </button>
          ))}
        </div>

        {/* Sector dropdown & Reset */}
        <div className="flex items-center gap-2">
          {sectorsList.length > 0 && (
            <select
              value={filters.selectedSector}
              onChange={(e: React.ChangeEvent<HTMLSelectElement>) => updateFilter("selectedSector", e.target.value)}
              className="bg-surface-subtle border border-border rounded-lg text-xs font-semibold text-content px-2.5 py-1.5 focus:outline-none focus:border-primary"
            >
              <option value="ALL">All Sectors</option>
              {sectorsList.map((sec) => (
                <option key={sec} value={sec}>
                  {sec}
                </option>
              ))}
            </select>
          )}

          <button
            onClick={resetFilters}
            className="flex items-center gap-1 text-[11px] font-medium text-content-muted hover:text-primary px-2.5 py-1.5 rounded-lg border border-border bg-surface transition-colors"
          >
            <RotateCcw className="w-3 h-3" />
            <span>Reset</span>
          </button>

          <span className="text-[11px] font-tabular font-bold text-primary bg-primary/10 px-2.5 py-1 rounded-lg">
            {totalResults} Articles
          </span>
        </div>
      </div>
    </div>
  );
};
