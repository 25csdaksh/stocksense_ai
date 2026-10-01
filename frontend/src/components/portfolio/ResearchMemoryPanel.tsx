"use client";

import React from "react";
import { ResearchMemoryItem } from "@/types/portfolio-copilot";
import { Brain, Clock, ArrowUpRight, Search, FileText } from "lucide-react";

interface ResearchMemoryPanelProps {
  memories: ResearchMemoryItem[];
  onSelectMemory?: (memory: ResearchMemoryItem) => void;
  onCompareWithCurrent?: (memory: ResearchMemoryItem) => void;
}

export const ResearchMemoryPanel: React.FC<ResearchMemoryPanelProps> = ({
  memories,
  onSelectMemory,
  onCompareWithCurrent,
}) => {
  return (
    <div className="bg-surface border border-border rounded-2xl p-6 shadow-card space-y-5">
      <div className="flex items-center justify-between border-b border-border pb-4">
        <div className="flex items-center gap-2">
          <div className="p-2 rounded-xl bg-primary/10 text-primary border border-primary/20">
            <Brain className="w-5 h-5" />
          </div>
          <div>
            <h3 className="text-sm font-black text-content uppercase tracking-wider">
              Personal Research Memory
            </h3>
            <p className="text-xs text-content-muted">
              User-isolated historical inquiry records and baseline parameters ({memories.length} saved)
            </p>
          </div>
        </div>
      </div>

      {memories.length > 0 ? (
        <div className="space-y-3">
          {memories.map((mem) => (
            <div
              key={mem.research_id}
              className="p-4 bg-surface-subtle rounded-xl border border-border/70 hover:border-primary/50 transition-all space-y-2.5"
            >
              <div className="flex flex-wrap items-center justify-between gap-2">
                <div className="flex items-center gap-2">
                  <span className="px-2 py-0.5 rounded bg-surface border border-border text-[10px] font-mono font-bold text-primary">
                    {mem.intent}
                  </span>
                  <span className="text-[10px] text-content-muted flex items-center gap-1">
                    <Clock className="w-3 h-3" /> {mem.created_at ? mem.created_at.slice(0, 10) : ""}
                  </span>
                </div>

                <div className="flex items-center gap-1.5 font-mono text-[10px]">
                  <span className="text-content-muted">Confidence:</span>
                  <span className="font-bold text-accent">{mem.confidence_level}</span>
                </div>
              </div>

              <h4 className="text-xs font-bold text-content leading-snug">
                &quot;{mem.query}&quot;
              </h4>

              {mem.report_summary && (
                <p className="text-[11px] text-content-muted line-clamp-2 leading-relaxed font-sans">
                  {mem.report_summary}
                </p>
              )}

              {mem.symbols && mem.symbols.length > 0 && (
                <div className="flex flex-wrap items-center gap-1.5 pt-1">
                  <span className="text-[10px] text-content-muted font-mono">Symbols:</span>
                  {mem.symbols.map((s, i) => (
                    <span
                      key={i}
                      className="px-1.5 py-0.5 rounded bg-surface border border-border text-[9px] font-mono font-bold text-content"
                    >
                      {s}
                    </span>
                  ))}
                </div>
              )}

              <div className="flex items-center justify-end gap-2 pt-2 border-t border-border/50">
                {onCompareWithCurrent && (
                  <button
                    onClick={() => onCompareWithCurrent(mem)}
                    className="px-2.5 py-1 rounded-lg bg-surface hover:bg-surface-subtle border border-border text-[11px] font-bold text-primary transition-all flex items-center gap-1"
                  >
                    Compare with Current <ArrowUpRight className="w-3 h-3" />
                  </button>
                )}
              </div>
            </div>
          ))}
        </div>
      ) : (
        <div className="p-8 text-center bg-surface-subtle rounded-xl border border-border/60 text-xs text-content-muted space-y-1">
          <FileText className="w-6 h-6 mx-auto text-content-muted/50 mb-2" />
          <p className="font-bold text-content">No research memories saved yet.</p>
          <p>Execute portfolio inquiries to establish historical research baselines.</p>
        </div>
      )}
    </div>
  );
};
