"use client";

import React from "react";
import { Search, X } from "lucide-react";

interface SearchInputProps {
  query: string;
  onChange: (q: string) => void;
  onClear: () => void;
  placeholder?: string;
}

export const SearchInput: React.FC<SearchInputProps> = ({
  query,
  onChange,
  onClear,
  placeholder = "Search stocks, companies, news, research or ask MarketMind...",
}) => {
  return (
    <div className="relative flex items-center px-4 py-3.5 border-b border-border bg-surface">
      <Search className="w-5 h-5 text-primary shrink-0 mr-3" />
      <input
        autoFocus
        type="text"
        value={query}
        onChange={(e: React.ChangeEvent<HTMLInputElement>) => onChange(e.target.value)}
        placeholder={placeholder}
        className="w-full bg-transparent border-none text-sm sm:text-base font-medium text-content placeholder:text-content-muted focus:outline-none focus:ring-0"
      />
      {query && (
        <button
          onClick={onClear}
          className="p-1 text-content-muted hover:text-content rounded-md hover:bg-surface-subtle transition-colors mr-2"
        >
          <X className="w-4 h-4" />
        </button>
      )}
      <kbd className="hidden sm:inline-flex items-center gap-1 px-2 py-0.5 text-[10px] font-mono font-medium text-content-muted bg-surface-subtle border border-border rounded">
        ESC
      </kbd>
    </div>
  );
};
