"use client";

import React from "react";
import { Card, CardContent } from "@/components/common/Card";
import { Badge } from "@/components/common/Badge";
import { Brain, Loader2, Sparkles } from "lucide-react";

export interface ResearchLoadingStateProps {
  query?: string;
  ticker?: string | null;
}

export const ResearchLoadingState: React.FC<ResearchLoadingStateProps> = ({ query, ticker }) => {
  return (
    <Card className="border-primary/30 shadow-card bg-surface overflow-hidden">
      <CardContent className="p-6 space-y-5">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 border-b border-border pb-4">
          <div className="flex items-center gap-2.5">
            <div className="w-9 h-9 rounded-xl bg-primary text-accent flex items-center justify-center animate-pulse">
              <Brain className="w-5 h-5" />
            </div>
            <div>
              <h3 className="text-sm font-bold text-content flex items-center gap-2">
                MarketMind Research Engine Active
                <Loader2 className="w-3.5 h-3.5 text-accent animate-spin" />
              </h3>
              <p className="text-xs text-content-muted">
                Multi-agent LangGraph orchestrator evaluating {ticker || "cross-asset market intelligence"}
              </p>
            </div>
          </div>
          <Badge variant="gold" size="sm">
            EXECUTING DAG
          </Badge>
        </div>

        {/* Query Prompt Quote */}
        {query && (
          <div className="p-3 bg-surface-subtle rounded-xl border border-border text-xs text-content font-medium">
            <span className="text-primary font-bold">Inquiry:</span> &quot;{query}&quot;
          </div>
        )}

        {/* Pulsing Skeleton Lines */}
        <div className="space-y-3 pt-1">
          <div className="h-3.5 bg-surface-subtle rounded-md w-3/4 animate-pulse" />
          <div className="h-3.5 bg-surface-subtle rounded-md w-full animate-pulse" />
          <div className="h-3.5 bg-surface-subtle rounded-md w-5/6 animate-pulse" />
          <div className="h-3.5 bg-surface-subtle rounded-md w-2/3 animate-pulse" />
        </div>
      </CardContent>
    </Card>
  );
};
