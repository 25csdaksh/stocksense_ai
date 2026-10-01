"use client";

import React from "react";
import { Database, ShieldCheck, Cpu } from "lucide-react";

interface ProvenancePanelProps {
  provenanceSummary?: Record<string, string>;
}

export const ProvenancePanel: React.FC<ProvenancePanelProps> = ({ provenanceSummary }) => {
  if (!provenanceSummary || Object.keys(provenanceSummary).length === 0) return null;

  return (
    <div className="bg-surface border border-border rounded-2xl p-4 shadow-sm space-y-3">
      <div className="flex items-center gap-2">
        <Database className="w-4 h-4 text-primary" />
        <h4 className="text-xs font-bold text-content uppercase tracking-wider">
          Data Provenance & Audit Trail
        </h4>
      </div>

      <div className="grid grid-cols-1 sm:grid-cols-2 gap-2 text-xs font-tabular">
        {Object.entries(provenanceSummary).map(([tier, countStr]) => (
          <div
            key={tier}
            className="p-2.5 rounded-xl bg-surface-subtle border border-border/70 flex items-center justify-between"
          >
            <span className="text-[11px] text-content-muted font-medium">{tier}</span>
            <span className="text-[11px] font-bold text-content">{countStr}</span>
          </div>
        ))}
      </div>
    </div>
  );
};
