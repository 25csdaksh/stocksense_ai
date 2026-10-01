"use client";

import React from "react";
import { ResearchReport } from "@/types";
import { ResearchConfidenceCard } from "./ResearchConfidenceCard";
import { EvidenceConflictPanel } from "./EvidenceConflictPanel";
import { UnknownsPanel } from "./UnknownsPanel";
import { ProvenancePanel } from "./ProvenancePanel";
import { Badge } from "@/components/common/Badge";
import {
  FileText,
  TrendingUp,
  BarChart3,
  Newspaper,
  ShieldAlert,
  Zap,
  HelpCircle,
  ExternalLink,
  Scale,
  Sparkles,
  Layers,
} from "lucide-react";

interface ResearchReportRendererProps {
  report: ResearchReport;
  onSelectCitation?: (citationId: string) => void;
}

export const ResearchReportRenderer: React.FC<ResearchReportRendererProps> = ({
  report,
  onSelectCitation,
}) => {
  const symbolsLabel = report.symbols && report.symbols.length > 0 ? report.symbols.join(", ") : "Universal";

  return (
    <div className="bg-surface border border-border rounded-2xl p-6 sm:p-8 shadow-card space-y-7 font-sans">
      {/* Report Header */}
      <div className="border-b border-border pb-5 space-y-3">
        <div className="flex flex-wrap items-center justify-between gap-3">
          <div className="space-y-1">
            <div className="flex items-center gap-2">
              <Badge variant="primary" size="sm">
                AI RESEARCH ENGINE 6.9
              </Badge>
              <span className="text-[10px] font-mono text-content-muted">ID: {report.report_id}</span>
            </div>
            <h2 className="text-xl sm:text-2xl font-black text-content tracking-tight">
              {symbolsLabel} Institutional Research
            </h2>
          </div>

          <div className="flex items-center gap-2 font-tabular">
            <span className="text-xs text-content-muted">
              Horizon: <span className="font-bold text-content">{report.time_range || "6m"}</span>
            </span>
            <span className="text-xs text-content-muted">|</span>
            <span className="text-xs text-content-muted">
              Depth: <span className="font-bold text-accent">{report.research_depth}</span>
            </span>
          </div>
        </div>

        {/* Deterministic Confidence Card */}
        <ResearchConfidenceCard
          level={report.confidence_level}
          rationale={report.confidence_rationale}
          provenanceSummary={report.provenance_summary}
        />
      </div>

      {/* 1. Executive Summary */}
      <div className="space-y-2">
        <h3 className="text-xs font-black uppercase tracking-wider text-primary flex items-center gap-1.5">
          <Sparkles className="w-4 h-4" /> 1. Executive Summary
        </h3>
        <p className="text-xs sm:text-sm text-content leading-relaxed font-sans bg-surface-subtle p-4 rounded-xl border border-border/60">
          {report.executive_summary}
        </p>
      </div>

      {/* 2. Market Context */}
      {report.market_context && (
        <div className="space-y-2">
          <h3 className="text-xs font-black uppercase tracking-wider text-content flex items-center gap-1.5">
            <TrendingUp className="w-4 h-4 text-accent" /> 2. Market & Session Context
          </h3>
          <div className="text-xs text-content leading-relaxed whitespace-pre-wrap bg-surface-subtle p-3.5 rounded-xl border border-border/60 font-sans">
            {report.market_context}
          </div>
        </div>
      )}

      {/* 3. Fundamental Analysis */}
      {report.fundamental_analysis && (
        <div className="space-y-2">
          <h3 className="text-xs font-black uppercase tracking-wider text-content flex items-center gap-1.5">
            <BarChart3 className="w-4 h-4 text-financial-gain" /> 3. Fundamental & Solvency Picture
          </h3>
          <div className="text-xs text-content leading-relaxed whitespace-pre-wrap bg-surface-subtle p-3.5 rounded-xl border border-border/60 font-sans">
            {report.fundamental_analysis}
          </div>
        </div>
      )}

      {/* 4. Technical Analysis */}
      {report.technical_analysis && (
        <div className="space-y-2">
          <h3 className="text-xs font-black uppercase tracking-wider text-content flex items-center gap-1.5">
            <Scale className="w-4 h-4 text-primary" /> 4. Technical Indicators & Trend Regime
          </h3>
          <div className="text-xs text-content leading-relaxed whitespace-pre-wrap bg-surface-subtle p-3.5 rounded-xl border border-border/60 font-sans">
            {report.technical_analysis}
          </div>
        </div>
      )}

      {/* 5. News & Events */}
      {report.news_analysis && (
        <div className="space-y-2">
          <h3 className="text-xs font-black uppercase tracking-wider text-content flex items-center gap-1.5">
            <Newspaper className="w-4 h-4 text-accent" /> 5. News Intelligence & Sentiment Dynamics
          </h3>
          <div className="text-xs text-content leading-relaxed whitespace-pre-wrap bg-surface-subtle p-3.5 rounded-xl border border-border/60 font-sans">
            {report.news_analysis}
          </div>
        </div>
      )}

      {/* 6. Risk Profile */}
      {report.risk_analysis && (
        <div className="space-y-2">
          <h3 className="text-xs font-black uppercase tracking-wider text-content flex items-center gap-1.5">
            <ShieldAlert className="w-4 h-4 text-financial-warning" /> 6. Downside Risk & Value at Risk (VaR)
          </h3>
          <div className="text-xs text-content leading-relaxed whitespace-pre-wrap bg-surface-subtle p-3.5 rounded-xl border border-border/60 font-sans">
            {report.risk_analysis}
          </div>
        </div>
      )}

      {/* 7. Anomalies */}
      {report.anomaly_analysis && (
        <div className="space-y-2">
          <h3 className="text-xs font-black uppercase tracking-wider text-content flex items-center gap-1.5">
            <Zap className="w-4 h-4 text-financial-warning" /> 7. Statistical Market Anomalies
          </h3>
          <div className="text-xs text-content leading-relaxed whitespace-pre-wrap bg-surface-subtle p-3.5 rounded-xl border border-border/60 font-sans">
            {report.anomaly_analysis}
          </div>
        </div>
      )}

      {/* 8. Side-by-Side Comparison */}
      {report.comparison_analysis && (
        <div className="space-y-2">
          <h3 className="text-xs font-black uppercase tracking-wider text-content flex items-center gap-1.5">
            <Layers className="w-4 h-4 text-primary" /> 8. Comparative Analysis
          </h3>
          <div className="text-xs text-content leading-relaxed whitespace-pre-wrap bg-surface-subtle p-3.5 rounded-xl border border-border/60 font-sans">
            {report.comparison_analysis}
          </div>
        </div>
      )}

      {/* 9. Evidence Conflicts */}
      {report.evidence_conflicts && report.evidence_conflicts.length > 0 && (
        <EvidenceConflictPanel conflicts={report.evidence_conflicts} />
      )}

      {/* 10. Key Unknowns */}
      {report.unknowns && report.unknowns.length > 0 && (
        <UnknownsPanel unknowns={report.unknowns} />
      )}

      {/* 11. Research Conclusion */}
      <div className="space-y-2">
        <h3 className="text-xs font-black uppercase tracking-wider text-content flex items-center gap-1.5">
          <FileText className="w-4 h-4 text-primary" /> 11. Analytical Research Conclusion
        </h3>
        <p className="text-xs sm:text-sm text-content leading-relaxed font-sans bg-surface-subtle p-4 rounded-xl border border-primary/30">
          {report.research_conclusion}
        </p>
      </div>

      {/* 12. Citations & Verified Sources */}
      {report.citations && report.citations.length > 0 && (
        <div className="space-y-2.5 pt-4 border-t border-border">
          <h3 className="text-xs font-black uppercase tracking-wider text-content flex items-center gap-1.5">
            <ExternalLink className="w-4 h-4 text-accent" /> 12. Verified Citations & Evidence Trail ({report.citations.length})
          </h3>
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-2 text-xs">
            {report.citations.map((cite, i) => (
              <div
                key={cite.citation_id || i}
                onClick={() => onSelectCitation && onSelectCitation(cite.citation_id)}
                className="p-3 bg-surface-subtle rounded-xl border border-border/70 hover:border-primary/50 cursor-pointer transition-all space-y-1"
              >
                <div className="flex items-center justify-between">
                  <span className="font-bold text-content truncate block max-w-[200px]">
                    [{i + 1}] {cite.source_name}
                  </span>
                  <span className="px-1.5 py-0.5 rounded bg-surface border border-border text-[9px] font-mono text-content-muted">
                    {cite.source_type}
                  </span>
                </div>
                {cite.excerpt && (
                  <p className="text-[10px] text-content-muted line-clamp-2 italic">&quot;{cite.excerpt}&quot;</p>
                )}
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Compliance & Disclaimers */}
      <div className="pt-4 border-t border-border text-[10px] text-content-muted space-y-1 leading-normal">
        <p className="font-bold uppercase text-content text-[9px]">Regulatory Disclaimers & Limitations:</p>
        <ul className="list-disc list-inside space-y-0.5">
          {report.limitations.map((lim, idx) => (
            <li key={idx}>{lim}</li>
          ))}
        </ul>
      </div>
    </div>
  );
};
