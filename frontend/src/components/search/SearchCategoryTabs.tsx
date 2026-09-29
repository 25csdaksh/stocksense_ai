"use client";

import React from "react";
import { SearchCategory } from "@/types";

interface SearchCategoryTabsProps {
  activeCategory: SearchCategory;
  onSelectCategory: (cat: SearchCategory) => void;
}

const CATEGORIES: Array<{ key: SearchCategory; label: string }> = [
  { key: "ALL", label: "All" },
  { key: "STOCKS", label: "Stocks" },
  { key: "ACTIONS", label: "Commands" },
  { key: "NEWS", label: "News" },
  { key: "ANOMALIES", label: "Anomalies" },
  { key: "PORTFOLIO", label: "Portfolio" },
];

export const SearchCategoryTabs: React.FC<SearchCategoryTabsProps> = ({
  activeCategory,
  onSelectCategory,
}) => {
  return (
    <div className="flex items-center gap-1.5 px-4 py-2 bg-surface-subtle/50 border-b border-border overflow-x-auto scrollbar-none">
      {CATEGORIES.map((cat) => (
        <button
          key={cat.key}
          onClick={() => onSelectCategory(cat.key)}
          className={`px-2.5 py-1 text-[11px] font-semibold rounded-lg transition-all shrink-0 ${
            activeCategory === cat.key
              ? "bg-primary text-white shadow-sm"
              : "text-content-muted hover:text-content hover:bg-surface-subtle"
          }`}
        >
          {cat.label}
        </button>
      ))}
    </div>
  );
};
