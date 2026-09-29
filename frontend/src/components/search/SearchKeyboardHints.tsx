"use client";

import React from "react";

export const SearchKeyboardHints: React.FC = () => {
  return (
    <div className="p-3 bg-surface-subtle/70 border-t border-border flex flex-wrap items-center justify-between text-[11px] text-content-muted px-4 gap-2">
      <div className="flex items-center gap-3">
        <span className="flex items-center gap-1">
          <kbd className="font-mono bg-surface px-1.5 py-0.5 border border-border rounded text-[10px]">↑</kbd>
          <kbd className="font-mono bg-surface px-1.5 py-0.5 border border-border rounded text-[10px]">↓</kbd>
          <span>Navigate</span>
        </span>
        <span className="flex items-center gap-1">
          <kbd className="font-mono bg-surface px-1.5 py-0.5 border border-border rounded text-[10px]">↵</kbd>
          <span>Select</span>
        </span>
        <span className="flex items-center gap-1">
          <kbd className="font-mono bg-surface px-1.5 py-0.5 border border-border rounded text-[10px]">ESC</kbd>
          <span>Close</span>
        </span>
      </div>

      <span className="font-semibold text-primary">MarketMind AI • Global Command Center</span>
    </div>
  );
};
