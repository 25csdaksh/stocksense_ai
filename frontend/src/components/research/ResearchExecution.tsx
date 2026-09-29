"use client";

import React from "react";
import { PipelineNode } from "@/types";
import { Card, CardHeader, CardTitle, CardDescription, CardContent } from "@/components/common/Card";
import { Badge } from "@/components/common/Badge";
import {
  Brain,
  CheckCircle2,
  Loader2,
  AlertTriangle,
  XCircle,
  Clock,
  ArrowRight,
} from "lucide-react";
import { cn } from "@/lib/utils";

export interface ResearchExecutionProps {
  nodes: PipelineNode[];
  isProcessing: boolean;
}

export const ResearchExecution: React.FC<ResearchExecutionProps> = ({ nodes, isProcessing }) => {
  if (!isProcessing && nodes.every((n) => n.status === "pending")) {
    return null;
  }

  const getStatusIcon = (status: PipelineNode["status"]) => {
    switch (status) {
      case "completed":
        return <CheckCircle2 className="w-4 h-4 text-financial-gain" />;
      case "running":
        return <Loader2 className="w-4 h-4 text-accent animate-spin" />;
      case "warning":
        return <AlertTriangle className="w-4 h-4 text-accent" />;
      case "failed":
        return <XCircle className="w-4 h-4 text-financial-loss" />;
      default:
        return <Clock className="w-4 h-4 text-content-muted/60" />;
    }
  };

  const getStatusBadge = (status: PipelineNode["status"]) => {
    switch (status) {
      case "completed":
        return <Badge variant="gain" size="sm">COMPLETED</Badge>;
      case "running":
        return <Badge variant="gold" size="sm">RUNNING</Badge>;
      case "warning":
        return <Badge variant="gold" size="sm">WARNING</Badge>;
      case "failed":
        return <Badge variant="loss" size="sm">FAILED</Badge>;
      default:
        return <Badge variant="neutral" size="sm">PENDING</Badge>;
    }
  };

  return (
    <Card className="border-border shadow-card bg-surface overflow-hidden">
      <CardHeader className="py-3 px-5 border-b border-border/60 bg-surface-subtle/50 flex flex-row items-center justify-between">
        <div className="flex items-center gap-2">
          <Brain className="w-4 h-4 text-primary" />
          <CardTitle className="text-xs font-bold uppercase tracking-wider text-content">
            Multi-Agent Execution Pipeline
          </CardTitle>
        </div>
        <div className="text-[11px] font-semibold text-content-muted">
          {nodes.filter((n) => n.status === "completed").length} of {nodes.length} Nodes Verified
        </div>
      </CardHeader>

      <CardContent className="p-4 space-y-3">
        {/* Visual Pipeline Step Progression */}
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-2.5">
          {nodes.map((node, index) => (
            <div
              key={node.id}
              className={cn(
                "p-3 rounded-xl border transition-all space-y-1.5",
                node.status === "running"
                  ? "bg-primary-light/10 border-primary/50 ring-1 ring-primary/20 shadow-sm"
                  : node.status === "completed"
                  ? "bg-surface-subtle/70 border-border"
                  : node.status === "failed"
                  ? "bg-financial-loss-bg border-financial-loss/30"
                  : "bg-surface border-border/60 opacity-60"
              )}
            >
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-2">
                  {getStatusIcon(node.status)}
                  <span className="text-xs font-bold text-content font-sans">
                    {node.name}
                  </span>
                </div>
                {getStatusBadge(node.status)}
              </div>

              <p className="text-[11px] text-content-muted leading-tight">
                {node.detail || node.description}
              </p>
            </div>
          ))}
        </div>
      </CardContent>
    </Card>
  );
};
