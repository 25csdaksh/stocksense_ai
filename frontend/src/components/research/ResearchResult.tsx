"use client";

import React, { useState } from "react";
import { ResearchMessage, CitationItem, ResearchReport, ResearchPlan } from "@/types";
import { Card, CardHeader, CardTitle, CardDescription, CardContent } from "@/components/common/Card";
import { Badge } from "@/components/common/Badge";
import { Button } from "@/components/common/Button";
import { ResearchReportRenderer } from "./ResearchReportRenderer";
import { ResearchPlanPanel } from "./ResearchPlanPanel";
import { EvidenceMatrix } from "./EvidenceMatrix";
import {
  Sparkles,
  Copy,
  Check,
  FileText,
  Bookmark,
  Database,
  Info,
} from "lucide-react";

export interface ResearchResultProps {
  message: ResearchMessage;
  onOpenReportMode?: () => void;
  onSelectCitation?: (citation: CitationItem) => void;
}

export const ResearchResult: React.FC<ResearchResultProps> = ({
  message,
  onOpenReportMode,
  onSelectCitation,
}) => {
  const [copied, setCopied] = useState(false);
  const [saved, setSaved] = useState(false);

  const handleCopy = () => {
    if (typeof window !== "undefined") {
      navigator.clipboard?.writeText(message.content);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    }
  };

  const handleSave = () => {
    setSaved(true);
    setTimeout(() => setSaved(false), 2500);
  };

  const agentResp = message.agentResponse as any;
  const structuredReport = agentResp?.report as ResearchReport | undefined;
  const researchPlan = agentResp?.research_plan as ResearchPlan | undefined;
  const executionSummary = agentResp?.execution_summary;
  const comparisonData =
    structuredReport?.comparison_analysis ||
    executionSummary?.validation_report?.conflicts_detected;

  return (
    <Card className="border-border shadow-card bg-surface overflow-hidden space-y-0">
      {/* Header Banner */}
      <CardHeader className="bg-primary text-white p-4.5 border-b border-primary-light/20 flex flex-col sm:flex-row sm:items-center justify-between gap-3">
        <div className="space-y-0.5">
          <div className="flex items-center gap-2">
            <Sparkles className="w-4 h-4 text-accent" />
            <CardTitle className="text-sm font-bold text-white tracking-wide">
              MarketMind Institutional Research Synthesis
            </CardTitle>
            <Badge variant="gold" size="sm">
              GROUNDED EVIDENCE
            </Badge>
          </div>
          <CardDescription className="text-xs text-surface/80">
            Synthesized at{" "}
            {new Date(message.timestamp).toLocaleTimeString([], {
              hour: "2-digit",
              minute: "2-digit",
            })}
            {message.ticker ? ` • Focus: ${message.ticker}` : " • Universal Market Scope"}
          </CardDescription>
        </div>

        {/* Action Toolbar */}
        <div className="flex items-center gap-1.5 self-end sm:self-center">
          <Button
            variant="outline"
            size="sm"
            onClick={handleCopy}
            className="text-xs bg-primary-dark/50 border-primary-light/30 text-white hover:bg-primary-light/20"
            leftIcon={
              copied ? (
                <Check className="w-3.5 h-3.5 text-financial-gain" />
              ) : (
                <Copy className="w-3.5 h-3.5" />
              )
            }
          >
            {copied ? "Copied" : "Copy"}
          </Button>

          <Button
            variant="outline"
            size="sm"
            onClick={handleSave}
            className="text-xs bg-primary-dark/50 border-primary-light/30 text-white hover:bg-primary-light/20"
            leftIcon={
              saved ? (
                <Check className="w-3.5 h-3.5 text-accent" />
              ) : (
                <Bookmark className="w-3.5 h-3.5" />
              )
            }
          >
            {saved ? "Saved" : "Save"}
          </Button>

          {onOpenReportMode && (
            <Button
              variant="gold"
              size="sm"
              onClick={onOpenReportMode}
              leftIcon={<FileText className="w-3.5 h-3.5" />}
            >
              Report View
            </Button>
          )}
        </div>
      </CardHeader>

      <CardContent className="p-5 space-y-6">
        {/* Phase 6.9 Research Plan Panel */}
        {researchPlan && <ResearchPlanPanel plan={researchPlan} />}

        {/* Phase 6.9 Structured Report Renderer */}
        {structuredReport ? (
          <ResearchReportRenderer
            report={structuredReport}
            onSelectCitation={(citeId) => {
              const matched = message.citations?.find(
                (c) => c.id === citeId || (c as any).citation_id === citeId
              );
              if (matched && onSelectCitation) {
                onSelectCitation(matched);
              }
            }}
          />
        ) : (
          <>
            {/* Legacy Thought Steps Verification Trace */}
            {message.thoughtSteps && message.thoughtSteps.length > 0 && (
              <div className="p-3 bg-surface-subtle/80 rounded-xl border border-border space-y-1.5">
                <span className="text-[10px] font-bold text-content-muted uppercase tracking-wider flex items-center gap-1">
                  <Database className="w-3 h-3 text-primary" />
                  Verified Execution Trail
                </span>
                <div className="flex flex-wrap gap-1.5">
                  {message.thoughtSteps.map((step, sIdx) => (
                    <span
                      key={sIdx}
                      className="inline-flex items-center gap-1 px-2 py-0.5 rounded-md bg-surface border border-border text-[10px] font-medium text-content"
                    >
                      <span className="w-1.5 h-1.5 rounded-full bg-financial-gain" />
                      {step.message}
                    </span>
                  ))}
                </div>
              </div>
            )}

            {/* Structured Research Body */}
            <div className="text-xs sm:text-sm text-content leading-relaxed space-y-4 whitespace-pre-wrap font-sans">
              {message.content}
            </div>

            {/* Citations & Source Evidence */}
            {message.citations && message.citations.length > 0 && (
              <div className="pt-4 border-t border-border space-y-2.5">
                <div className="flex items-center justify-between">
                  <span className="text-xs font-bold text-content flex items-center gap-1.5 uppercase tracking-wider">
                    <FileText className="w-3.5 h-3.5 text-primary" />
                    Traceable Filing & Document Citations ({message.citations.length})
                  </span>
                </div>

                <div className="grid grid-cols-1 sm:grid-cols-2 gap-2.5">
                  {message.citations.map((cite, idx) => (
                    <div
                      key={cite.id || idx}
                      onClick={() => onSelectCitation?.(cite)}
                      className="p-3 rounded-xl bg-surface-subtle/60 border border-border hover:border-primary/40 transition-all cursor-pointer space-y-1 group"
                    >
                      <div className="flex items-center justify-between">
                        <span className="text-xs font-bold text-content group-hover:text-primary transition-colors">
                          {cite.title || "Regulatory Disclosure"}
                        </span>
                        {cite.relevance_score !== undefined && (
                          <Badge variant="primary" size="sm">
                            {Math.round(cite.relevance_score * 100)}% MATCH
                          </Badge>
                        )}
                      </div>
                      <p className="text-[11px] font-semibold text-primary">
                        {cite.section} {cite.fiscal_year ? `(FY${cite.fiscal_year})` : ""}
                      </p>
                      <p className="text-[11px] text-content-muted leading-tight line-clamp-2 italic">
                        &quot;{cite.content_snippet}&quot;
                      </p>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* Limitations & Analytical Disclaimer */}
            <div className="p-3.5 bg-surface-subtle rounded-xl border border-border flex items-start gap-2.5 text-xs text-content-muted">
              <Info className="w-4 h-4 text-primary flex-shrink-0 mt-0.5" />
              <div className="space-y-0.5">
                <p className="font-semibold text-content text-[11px] uppercase tracking-wider">
                  Methodological Notice & Limitations
                </p>
                <p className="text-[11px] leading-relaxed">
                  Research synthesis aggregates verified historical price metrics, econometric
                  models, and filings. Outputs do not guarantee future market behavior, nor do
                  they constitute personalized investment advice or buy/sell execution mandates.
                </p>
              </div>
            </div>
          </>
        )}
      </CardContent>
    </Card>
  );
};
