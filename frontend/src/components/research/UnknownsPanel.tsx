"use client";

import React from "react";
import { HelpCircle, ChevronRight } from "lucide-react";

interface UnknownsPanelProps {
  unknowns?: string[];
}

export const UnknownsPanel: React.FC<UnknownsPanelProps> = ({ unknowns }) => {
  if (!unknowns || unknowns.length === 0) return null;

  return (
    <div className="bg-surface border border-border rounded-2xl p-4 shadow-sm space-y-3">
      <div className="flex items-center gap-2">
        <HelpCircle className="w-4 h-4 text-accent" />
        <h4 className="text-xs font-bold text-content uppercase tracking-wider">
          Key Research Unknowns & Data Gaps
        </h4>
      </div>

      <ul className="space-y-1.5 text-xs text-content-muted font-sans">
        {unknowns.map((item, idx) => (
          <li key={idx} className="flex items-start gap-2 text-[11px] leading-relaxed">
            <ChevronRight className="w-3.5 h-3.5 text-accent flex-shrink-0 mt-0.5" />
            <span>{item}</span>
          </li>
        ))}
      </ul>
    </div>
  );
};
