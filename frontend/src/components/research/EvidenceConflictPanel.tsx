"use client";

import React from "react";
import { EvidenceConflict } from "@/types";
import { AlertCircle, ArrowRightLeft } from "lucide-react";

interface EvidenceConflictPanelProps {
  conflicts?: EvidenceConflict[];
}

export const EvidenceConflictPanel: React.FC<EvidenceConflictPanelProps> = ({ conflicts }) => {
  if (!conflicts || conflicts.length === 0) return null;

  return (
    <div className="bg-surface border border-financial-warning/40 rounded-2xl p-4 shadow-sm space-y-3">
      <div className="flex items-center gap-2 text-financial-warning">
        <AlertCircle className="w-4 h-4 flex-shrink-0" />
        <h4 className="text-xs font-extrabold uppercase tracking-wider">
          Multi-Source Evidence Discrepancies ({conflicts.length})
        </h4>
      </div>

      <div className="space-y-2.5">
        {conflicts.map((conf) => (
          <div
            key={conf.conflict_id}
            className="p-3 bg-financial-warning/5 rounded-xl border border-financial-warning/20 text-xs space-y-2"
          >
            <div className="flex items-center justify-between">
              <span className="font-bold text-content uppercase tracking-tight text-[11px]">
                Metric: {conf.metric} ({conf.symbols.join(", ")})
              </span>
              <span className="px-2 py-0.5 rounded-full bg-financial-warning/20 text-financial-warning text-[9px] font-extrabold">
                Impact: {conf.impact}
              </span>
            </div>

            <div className="grid grid-cols-1 sm:grid-cols-2 gap-2 text-[11px] font-tabular">
              {conf.conflicting_values.map((item, idx) => (
                <div key={idx} className="p-2 bg-surface rounded-lg border border-border/60">
                  <span className="text-content-muted block text-[10px] font-medium">{item.source}</span>
                  <span className="font-bold text-content">{JSON.stringify(item.value)}</span>
                </div>
              ))}
            </div>

            <p className="text-[10px] text-content-muted italic border-t border-border/40 pt-1">
              Resolution: {conf.resolution}
            </p>
          </div>
        ))}
      </div>
    </div>
  );
};
