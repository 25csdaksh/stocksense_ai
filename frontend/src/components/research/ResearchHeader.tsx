"use client";

import React from "react";
import { Badge } from "@/components/common/Badge";
import { Button } from "@/components/common/Button";
import { ResearchMode } from "@/types";
import {
  Brain,
  Sparkles,
  FileText,
  RotateCcw,
  Building2,
  X,
  Layers,
  ChevronDown,
} from "lucide-react";
import { POPULAR_INDIAN_STOCKS } from "@/lib/constants";

export interface ResearchHeaderProps {
  selectedTicker: string | null;
  onSelectTicker: (ticker: string | null) => void;
  mode: ResearchMode;
  onSelectMode: (mode: ResearchMode) => void;
  isReportMode: boolean;
  onToggleReportMode: () => void;
  onResetSession: () => void;
}

const RESEARCH_MODES: Array<{ id: ResearchMode; label: string }> = [
  { id: "ALL", label: "Full Multi-Agent" },
  { id: "COMPANY", label: "Company Deep-Dive" },
  { id: "FUNDAMENTAL", label: "Valuation & Margins" },
  { id: "TECHNICAL", label: "Technicals & Trends" },
  { id: "RISK", label: "Risk & Volatility" },
  { id: "ANOMALY", label: "Anomalies & Flow" },
  { id: "NEWS", label: "News & Sentiment" },
  { id: "FILINGS", label: "SEC 10-K Filings" },
];

export const ResearchHeader: React.FC<ResearchHeaderProps> = ({
  selectedTicker,
  onSelectTicker,
  mode,
  onSelectMode,
  isReportMode,
  onToggleReportMode,
  onResetSession,
}) => {
  return (
    <div className="bg-surface border border-border rounded-2xl p-5 shadow-card space-y-4">
      <div className="flex flex-col lg:flex-row lg:items-center justify-between gap-4">
        {/* Left: Terminal Identity */}
        <div className="flex items-start sm:items-center gap-3.5">
          <div className="w-12 h-12 rounded-xl bg-primary text-accent font-extrabold flex items-center justify-center shadow-sm flex-shrink-0 border border-primary-light/20">
            <Brain className="w-6 h-6" />
          </div>
          <div>
            <div className="flex flex-wrap items-center gap-2">
              <h1 className="text-2xl font-extrabold tracking-tight text-content">
                AI Deep Research Terminal
              </h1>
              <Badge variant="gold" size="sm">
                LANGGRAPH MULTI-AGENT
              </Badge>
              <Badge variant="primary" size="sm">
                SEC 10-K RAG
              </Badge>
            </div>
            <p className="text-xs text-content-muted mt-0.5">
              Autonomous institutional equity research across real-time feeds, financial statement filings, and econometric models
            </p>
          </div>
        </div>

        {/* Right: Workspace Controls */}
        <div className="flex flex-wrap items-center gap-2">
          {/* Ticker Context Pill */}
          {selectedTicker ? (
            <div className="inline-flex items-center gap-2 px-3 py-1.5 rounded-xl bg-primary-light/10 border border-primary/30 text-xs font-bold text-primary">
              <Building2 className="w-3.5 h-3.5" />
              <span>Target: {selectedTicker}</span>
              <button
                onClick={() => onSelectTicker(null)}
                className="hover:text-primary-dark ml-0.5 p-0.5"
                title="Clear target ticker"
                aria-label="Clear target ticker"
              >
                <X className="w-3 h-3" />
              </button>
            </div>
          ) : (
            <div className="relative inline-block">
              <select
                onChange={(e: React.ChangeEvent<HTMLSelectElement>) => onSelectTicker(e.target.value || null)}
                value=""
                className="text-xs font-semibold py-1.5 pl-3 pr-7 rounded-xl bg-surface border border-border text-content hover:border-primary/40 focus:outline-none focus:ring-1 focus:ring-primary cursor-pointer appearance-none"
              >
                <option value="">+ Focus on Ticker</option>
                {POPULAR_INDIAN_STOCKS.map((s) => (
                  <option key={s.ticker} value={s.ticker}>
                    {s.ticker} — {s.name}
                  </option>
                ))}
              </select>
              <ChevronDown className="w-3.5 h-3.5 text-content-muted absolute right-2 top-1/2 -translate-y-1/2 pointer-events-none" />
            </div>
          )}

          {/* Report Mode Toggle */}
          <Button
            variant={isReportMode ? "gold" : "outline"}
            size="sm"
            onClick={onToggleReportMode}
            leftIcon={<FileText className="w-4 h-4" />}
          >
            {isReportMode ? "Terminal View" : "Research Report"}
          </Button>

          {/* Reset Session */}
          <Button
            variant="outline"
            size="sm"
            onClick={onResetSession}
            leftIcon={<RotateCcw className="w-3.5 h-3.5 text-content-muted" />}
          >
            New Session
          </Button>
        </div>
      </div>

      {/* Research Mode Selection Tabs */}
      <div className="flex items-center gap-1.5 overflow-x-auto pb-1 pt-1 border-t border-border-subtle scrollbar-none">
        <span className="text-[11px] font-bold text-content-muted uppercase tracking-wider mr-1 flex items-center gap-1 flex-shrink-0">
          <Layers className="w-3 h-3 text-primary" />
          Mode:
        </span>
        {RESEARCH_MODES.map((m) => (
          <button
            key={m.id}
            onClick={() => onSelectMode(m.id)}
            className={`text-xs font-semibold px-2.5 py-1 rounded-lg whitespace-nowrap transition-all ${
              mode === m.id
                ? "bg-primary text-white shadow-sm"
                : "text-content-muted hover:text-content hover:bg-surface-subtle border border-transparent hover:border-border"
            }`}
          >
            {m.label}
          </button>
        ))}
      </div>
    </div>
  );
};
