"use client";

import React from "react";
import { Search, Filter, X, Clock, Layers } from "lucide-react";

export interface AnomalyFiltersProps {
  severityFilter: string;
  onSelectSeverity: (sev: string) => void;
  typeFilter: string;
  onSelectType: (type: string) => void;
  searchQuery: string;
  onSearchChange: (q: string) => void;
  timeWindow: string;
  onSelectTimeWindow: (w: string) => void;
  onReset: () => void;
}

const SEVERITIES = ["ALL", "LOW", "MEDIUM", "HIGH", "CRITICAL"];
const ANOMALY_TYPES = ["ALL", "PRICE", "VOLUME", "VOLATILITY", "STATISTICAL", "CORRELATION"];
const TIME_WINDOWS = ["1H", "1D", "1W", "1M"];

export const AnomalyFilters: React.FC<AnomalyFiltersProps> = ({
  severityFilter,
  onSelectSeverity,
  typeFilter,
  onSelectType,
  searchQuery,
  onSearchChange,
  timeWindow,
  onSelectTimeWindow,
  onReset,
}) => {
  const hasActiveFilters =
    severityFilter !== "ALL" || typeFilter !== "ALL" || searchQuery.trim() !== "" || timeWindow !== "1D";

  return (
    <div className="p-4 bg-surface rounded-xl border border-border space-y-3.5">
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-3">
        {/* Search Box */}
        <div className="relative flex-1">
          <Search className="w-3.5 h-3.5 text-content-muted absolute left-3 top-1/2 -translate-y-1/2" />
          <input
            type="text"
            placeholder="Search by symbol, company, or anomaly signature..."
            value={searchQuery}
            onChange={(e: React.ChangeEvent<HTMLInputElement>) => onSearchChange(e.target.value)}
            className="w-full pl-9 pr-3 py-1.5 text-xs rounded-lg border border-border bg-surface-subtle focus:bg-surface focus:outline-none focus:ring-1 focus:ring-primary text-content"
          />
        </div>

        {/* Time Window Buttons */}
        <div className="flex items-center gap-1.5 self-start md:self-auto">
          <span className="text-[11px] text-content-muted font-medium flex items-center gap-1">
            <Clock className="w-3 h-3" />
            Window:
          </span>
          <div className="flex items-center gap-1 bg-surface-subtle p-0.5 rounded-lg border border-border">
            {TIME_WINDOWS.map((tw) => (
              <button
                key={tw}
                onClick={() => onSelectTimeWindow(tw)}
                className={`px-2 py-0.5 text-[11px] font-semibold rounded transition-all ${
                  timeWindow === tw
                    ? "bg-primary text-white shadow-xs"
                    : "text-content-muted hover:text-content hover:bg-surface"
                }`}
              >
                {tw}
              </button>
            ))}
          </div>

          {hasActiveFilters && (
            <button
              onClick={onReset}
              className="p-1 text-[11px] text-content-muted hover:text-financial-loss flex items-center gap-0.5 font-medium ml-1 transition-colors"
              title="Reset all filters"
            >
              <X className="w-3 h-3" />
              Reset
            </button>
          )}
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-3 pt-1 border-t border-border/50">
        {/* Severity Chips */}
        <div className="flex flex-wrap items-center gap-1.5">
          <span className="text-[11px] font-semibold text-content-muted mr-1">Severity:</span>
          {SEVERITIES.map((sev) => {
            const isSelected = severityFilter === sev;
            const badgeColor =
              sev === "CRITICAL"
                ? isSelected ? "bg-financial-loss text-white" : "bg-financial-loss-bg text-financial-loss hover:bg-financial-loss/20"
                : sev === "HIGH"
                ? isSelected ? "bg-amber-600 text-white" : "bg-amber-50 text-amber-700 hover:bg-amber-100"
                : sev === "MEDIUM"
                ? isSelected ? "bg-primary text-white" : "bg-primary-light text-primary hover:bg-primary/20"
                : sev === "LOW"
                ? isSelected ? "bg-secondary text-white" : "bg-surface-subtle text-content-muted hover:bg-surface"
                : isSelected ? "bg-primary text-white" : "bg-surface-subtle text-content-muted hover:bg-surface";

            return (
              <button
                key={sev}
                onClick={() => onSelectSeverity(sev)}
                className={`px-2.5 py-1 text-[11px] font-bold rounded-lg border border-transparent transition-all ${badgeColor}`}
              >
                {sev}
              </button>
            );
          })}
        </div>

        {/* Anomaly Type Chips */}
        <div className="flex flex-wrap items-center gap-1.5">
          <span className="text-[11px] font-semibold text-content-muted mr-1">Type:</span>
          {ANOMALY_TYPES.map((t) => {
            const isSelected = typeFilter === t;
            return (
              <button
                key={t}
                onClick={() => onSelectType(t)}
                className={`px-2 py-0.5 text-[10px] font-semibold rounded-md border transition-all ${
                  isSelected
                    ? "bg-primary text-white border-primary shadow-xs"
                    : "border-border bg-surface-subtle text-content-muted hover:bg-surface hover:text-content"
                }`}
              >
                {t}
              </button>
            );
          })}
        </div>
      </div>
    </div>
  );
};
