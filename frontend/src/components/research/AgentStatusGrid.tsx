"use client";

import React from "react";
import { ResearchTask } from "@/types";
import { CheckCircle2, Clock, AlertCircle, Circle } from "lucide-react";

interface AgentStatusGridProps {
  tasks?: ResearchTask[];
}

export const AgentStatusGrid: React.FC<AgentStatusGridProps> = ({ tasks = [] }) => {
  if (!tasks || tasks.length === 0) return null;

  return (
    <div className="grid grid-cols-2 sm:grid-cols-4 gap-2 text-xs font-sans">
      {tasks.map((t) => {
        const isCompleted = t.status === "COMPLETED";
        const isRunning = t.status === "RUNNING";
        const isFailed = t.status === "FAILED";

        return (
          <div
            key={t.task_id}
            className={`p-2.5 rounded-xl border transition-all ${
              isCompleted
                ? "bg-financial-gain/5 border-financial-gain/20 text-content"
                : isRunning
                ? "bg-primary/5 border-primary/30 text-content"
                : isFailed
                ? "bg-financial-loss/5 border-financial-loss/20 text-content"
                : "bg-surface-subtle border-border/60 text-content-muted"
            }`}
          >
            <div className="flex items-center justify-between mb-1">
              <span className="font-extrabold text-[11px] truncate capitalize">
                {t.agent.replace("_agent", "").replace("_", " ")}
              </span>
              {isCompleted ? (
                <CheckCircle2 className="w-3.5 h-3.5 text-financial-gain" />
              ) : isRunning ? (
                <Clock className="w-3.5 h-3.5 text-primary animate-spin" />
              ) : isFailed ? (
                <AlertCircle className="w-3.5 h-3.5 text-financial-loss" />
              ) : (
                <Circle className="w-3.5 h-3.5 text-content-muted" />
              )}
            </div>
            <p className="text-[9px] text-content-muted truncate">{t.objective}</p>
          </div>
        );
      })}
    </div>
  );
};
