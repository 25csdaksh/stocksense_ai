"use client";

import React from "react";
import { ResearchContextFlags } from "@/hooks/useResearch";
import { Card, CardHeader, CardTitle, CardContent } from "@/components/common/Card";
import { Badge } from "@/components/common/Badge";
import {
  ShieldCheck,
  Activity,
  CheckCircle2,
  FileText,
  Layers,
  Database,
  Newspaper,
  Zap,
} from "lucide-react";
import { cn } from "@/lib/utils";

export interface ResearchContextPanelProps {
  contextFlags: ResearchContextFlags;
}

export const ResearchContextPanel: React.FC<ResearchContextPanelProps> = ({ contextFlags }) => {
  const checklistItems = [
    { label: "Market OHLCV & Spot Data", verified: contextFlags.hasMarketData, icon: <Activity className="w-3.5 h-3.5" /> },
    { label: "Audited Fundamentals & Multiples", verified: contextFlags.hasFundamentals, icon: <Layers className="w-3.5 h-3.5" /> },
    { label: "Technical Oscillators & Volatility", verified: contextFlags.hasTechnicals, icon: <Activity className="w-3.5 h-3.5" /> },
    { label: "Verified Financial News", verified: contextFlags.hasNews, icon: <Newspaper className="w-3.5 h-3.5" /> },
    { label: "Isolation Forest Anomalies", verified: contextFlags.hasAnomalies, icon: <Zap className="w-3.5 h-3.5" /> },
    { label: "SEC 10-K & Regulatory Filings", verified: contextFlags.hasDocuments, icon: <FileText className="w-3.5 h-3.5" /> },
    { label: "Qdrant Vector Embeddings (RAG)", verified: contextFlags.hasRAG, icon: <Database className="w-3.5 h-3.5" /> },
  ];

  const verifiedCount = checklistItems.filter((i) => i.verified).length;

  return (
    <Card className="border-border shadow-card bg-surface overflow-hidden">
      <CardHeader className="py-3 px-4 border-b border-border/60 bg-surface-subtle/50 flex flex-row items-center justify-between">
        <div className="flex items-center gap-2">
          <ShieldCheck className="w-4 h-4 text-primary" />
          <CardTitle className="text-xs font-bold uppercase tracking-wider text-content">
            Research Context & Layers
          </CardTitle>
        </div>
        <Badge variant={verifiedCount >= 5 ? "gain" : "neutral"} size="sm">
          {verifiedCount} / {checklistItems.length} ACTIVE
        </Badge>
      </CardHeader>

      <CardContent className="p-4 space-y-3">
        {/* Active Target Banner */}
        <div className="p-2.5 rounded-xl bg-surface-subtle border border-border flex items-center justify-between text-xs">
          <span className="text-content-muted font-medium">Research Scope:</span>
          <span className="font-bold text-primary font-tabular">
            {contextFlags.ticker || "Indian Equity Universe (General)"}
          </span>
        </div>

        {/* Verification Checklist */}
        <div className="space-y-1.5 pt-1">
          {checklistItems.map((item, idx) => (
            <div
              key={idx}
              className={cn(
                "flex items-center justify-between p-2 rounded-lg text-xs font-medium transition-colors border",
                item.verified
                  ? "bg-surface text-content border-border/80"
                  : "bg-surface/40 text-content-muted/60 border-border/40"
              )}
            >
              <div className="flex items-center gap-2">
                <span className={cn(item.verified ? "text-primary" : "text-content-muted/60")}>
                  {item.icon}
                </span>
                <span className="text-[11px]">{item.label}</span>
              </div>

              {item.verified ? (
                <span className="flex items-center gap-1 text-[10px] font-bold text-financial-gain">
                  <CheckCircle2 className="w-3.5 h-3.5" /> Verified
                </span>
              ) : (
                <span className="text-[10px] text-content-muted">Standby</span>
              )}
            </div>
          ))}
        </div>

        {/* Factual Quality Notice */}
        <div className="p-2.5 rounded-lg bg-surface-subtle/70 border border-border text-[11px] text-content-muted">
          <p className="leading-tight">
            <strong>Transparency Notice:</strong> All quantitative layers are computed deterministically via Pandas/NumPy. Regulatory excerpts are retrieved directly from indexed filings.
          </p>
        </div>
      </CardContent>
    </Card>
  );
};
