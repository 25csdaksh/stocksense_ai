"use client";

import React, { useState } from "react";
import { ResearchPlan } from "@/types";
import { CheckCircle2, Circle, Clock, ChevronDown, ChevronUp, Cpu, Layers } from "lucide-react";

interface ResearchPlanPanelProps {
  plan?: ResearchPlan;
}

export const ResearchPlanPanel: React.FC<ResearchPlanPanelProps> = ({ plan }) => {
  const [isExpanded, setIsExpanded] = useState<boolean>(true);

  if (!plan) return null;

  return (
    <div className="bg-surface border border-border rounded-2xl p-4 shadow-sm space-y-3">
      <div
        className="flex items-center justify-between cursor-pointer select-none"
        onClick={() => setIsExpanded(!isExpanded)}
      >
        <div className="flex items-center gap-2">
          <div className="w-7 h-7 rounded-lg bg-primary/10 text-primary flex items-center justify-center font-bold text-xs">
            <Cpu className="w-4 h-4" />
          </div>
          <div>
            <h4 className="text-xs font-bold text-content uppercase tracking-wider">
              Research Plan & Task Graph
            </h4>
            <p className="text-[10px] text-content-muted">
              Intent: <span className="font-semibold text-primary">{plan.intent}</span> | Depth:{" "}
              <span className="font-semibold text-accent">{plan.research_depth}</span>
            </p>
          </div>
        </div>

        <button className="text-content-muted hover:text-content transition-colors p-1">
          {isExpanded ? <ChevronUp className="w-4 h-4" /> : <ChevronDown className="w-4 h-4" />}
        </button>
      </div>

      {isExpanded && (
        <div className="space-y-2.5 pt-2 border-t border-border-subtle">
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-2 text-xs">
            {plan.tasks.map((t, idx) => (
              <div
                key={t.task_id || idx}
                className="flex items-start gap-2 p-2 rounded-xl bg-surface-subtle border border-border/60 text-[11px]"
              >
                {t.status === "COMPLETED" ? (
                  <CheckCircle2 className="w-3.5 h-3.5 text-financial-gain flex-shrink-0 mt-0.5" />
                ) : t.status === "RUNNING" ? (
                  <Clock className="w-3.5 h-3.5 text-primary animate-spin flex-shrink-0 mt-0.5" />
                ) : t.status === "FAILED" ? (
                  <span className="w-3.5 h-3.5 rounded-full bg-financial-loss/20 text-financial-loss flex items-center justify-center text-[9px] font-bold mt-0.5">
                    ✕
                  </span>
                ) : (
                  <Circle className="w-3.5 h-3.5 text-content-muted flex-shrink-0 mt-0.5" />
                )}
                <div className="min-w-0 flex-1">
                  <span className="font-bold text-content block truncate capitalize">
                    {t.agent.replace("_", " ")}
                  </span>
                  <p className="text-[10px] text-content-muted truncate">{t.objective}</p>
                </div>
              </div>
            ))}
          </div>

          {plan.required_tools && plan.required_tools.length > 0 && (
            <div className="flex flex-wrap items-center gap-1.5 pt-1">
              <span className="text-[10px] uppercase font-bold text-content-muted mr-1">
                Tools Invocations:
              </span>
              {plan.required_tools.map((tool, i) => (
                <span
                  key={i}
                  className="px-2 py-0.5 bg-surface rounded-md border border-border text-[10px] font-mono text-content-muted"
                >
                  {tool}
                </span>
              ))}
            </div>
          )}
        </div>
      )}
    </div>
  );
};
