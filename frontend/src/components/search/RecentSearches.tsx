"use client";

import React from "react";
import { History, X, Trash2 } from "lucide-react";

interface RecentSearchesProps {
  searches: string[];
  onSelectSearch: (term: string) => void;
  onRemoveSearch: (term: string) => void;
  onClearAll: () => void;
}

export const RecentSearches: React.FC<RecentSearchesProps> = ({
  searches,
  onSelectSearch,
  onRemoveSearch,
  onClearAll,
}) => {
  if (searches.length === 0) {
    return null;
  }

  return (
    <div className="space-y-2 pb-2">
      <div className="flex items-center justify-between text-[11px] font-bold uppercase tracking-wider text-content-muted">
        <div className="flex items-center gap-1.5">
          <History className="w-3.5 h-3.5 text-primary" />
          <span>Recent Searches</span>
        </div>
        <button
          onClick={onClearAll}
          className="text-[10px] font-medium text-content-muted hover:text-financial-loss transition-colors flex items-center gap-1"
        >
          <Trash2 className="w-3 h-3" />
          <span>Clear History</span>
        </button>
      </div>

      <div className="flex flex-wrap gap-1.5">
        {searches.map((term) => (
          <div
            key={term}
            className="inline-flex items-center gap-1.5 bg-surface-subtle border border-border px-2.5 py-1 rounded-lg text-xs font-semibold text-content hover:border-primary/40 transition-colors"
          >
            <span
              onClick={() => onSelectSearch(term)}
              className="cursor-pointer hover:text-primary"
            >
              {term}
            </span>
            <button
              onClick={(e: React.MouseEvent) => {
                e.stopPropagation();
                onRemoveSearch(term);
              }}
              className="text-content-muted hover:text-financial-loss"
            >
              <X className="w-3 h-3" />
            </button>
          </div>
        ))}
      </div>
    </div>
  );
};
