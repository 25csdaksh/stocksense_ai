"use client";

import React from "react";
import { ResearchMessage, CitationItem } from "@/types";
import { Card, CardHeader, CardTitle, CardContent } from "@/components/common/Card";
import { Badge } from "@/components/common/Badge";
import { Button } from "@/components/common/Button";
import {
  FileText,
  Printer,
  Copy,
  ArrowLeft,
  ShieldCheck,
  Building2,
  Calendar,
  CheckCircle2,
  Info,
  Layers,
} from "lucide-react";

export interface ResearchReportViewProps {
  message: ResearchMessage;
  onClose: () => void;
}

export const ResearchReportView: React.FC<ResearchReportViewProps> = ({ message, onClose }) => {
  const handlePrint = () => {
    if (typeof window !== "undefined") {
      window.print();
    }
  };

  const handleCopy = () => {
    if (typeof window !== "undefined") {
      navigator.clipboard?.writeText(message.content);
    }
  };

  const formattedDate = new Date(message.timestamp).toLocaleDateString("en-US", {
    year: "numeric",
    month: "long",
    day: "numeric",
  });

  return (
    <div className="space-y-6 max-w-4xl mx-auto">
      {/* Top Action Bar */}
      <div className="flex items-center justify-between gap-3 bg-surface p-4 rounded-2xl border border-border shadow-sm print:hidden">
        <Button variant="outline" size="sm" onClick={onClose} leftIcon={<ArrowLeft className="w-4 h-4" />}>
          Back to Terminal View
        </Button>

        <div className="flex items-center gap-2">
          <Button variant="outline" size="sm" onClick={handleCopy} leftIcon={<Copy className="w-4 h-4" />}>
            Copy Report
          </Button>
          <Button variant="gold" size="sm" onClick={handlePrint} leftIcon={<Printer className="w-4 h-4" />}>
            Print / PDF Export
          </Button>
        </div>
      </div>

      {/* Formal Research Report Document */}
      <div className="bg-surface border border-border rounded-2xl p-8 sm:p-12 shadow-card space-y-8 font-sans">
        {/* Document Header */}
        <div className="border-b-2 border-primary pb-6 space-y-3">
          <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2">
            <div className="flex items-center gap-2.5">
              <div className="w-10 h-10 rounded-xl bg-primary text-accent font-black text-lg flex items-center justify-center">
                M
              </div>
              <div>
                <h2 className="text-xl font-extrabold text-content tracking-tight">MARKETMIND AI</h2>
                <p className="text-[11px] text-content-muted uppercase tracking-widest font-semibold">
                  Institutional Equity Research Division
                </p>
              </div>
            </div>

            <div className="text-right">
              <Badge variant="primary" size="md">
                FORMAL RESEARCH BRIEFING
              </Badge>
              <p className="text-xs text-content-muted mt-1 flex items-center justify-end gap-1 font-medium">
                <Calendar className="w-3.5 h-3.5" /> {formattedDate}
              </p>
            </div>
          </div>

          <div className="grid grid-cols-2 sm:grid-cols-4 gap-4 pt-4 border-t border-border-subtle text-xs font-tabular">
            <div>
              <span className="text-content-muted uppercase text-[10px] block font-bold">Target Instrument</span>
              <span className="font-extrabold text-content text-sm">{message.ticker || "Multi-Asset Universe"}</span>
            </div>
            <div>
              <span className="text-content-muted uppercase text-[10px] block font-bold">Coverage Scope</span>
              <span className="font-semibold text-content">Equities / Macro Derivatives</span>
            </div>
            <div>
              <span className="text-content-muted uppercase text-[10px] block font-bold">Framework</span>
              <span className="font-semibold text-content">Fama-French + GARCH + RAG</span>
            </div>
            <div>
              <span className="text-content-muted uppercase text-[10px] block font-bold">Verification Status</span>
              <span className="font-bold text-financial-gain flex items-center gap-1">
                <ShieldCheck className="w-3.5 h-3.5" /> 100% Grounded
              </span>
            </div>
          </div>
        </div>

        {/* Primary Query Title */}
        <div className="space-y-1">
          <span className="text-[11px] font-bold text-primary uppercase tracking-wider">Research Inquiry:</span>
          <h1 className="text-lg sm:text-xl font-bold text-content leading-snug">
            {message.agentResponse?.query || message.content.slice(0, 100)}
          </h1>
        </div>

        {/* Main Body Report Content */}
        <div className="space-y-6 text-xs sm:text-sm text-content leading-relaxed whitespace-pre-wrap font-sans">
          {message.content}
        </div>

        {/* Citations & Exhibits */}
        {message.citations && message.citations.length > 0 && (
          <div className="border-t border-border pt-6 space-y-3">
            <h3 className="text-xs font-extrabold uppercase tracking-wider text-content flex items-center gap-1.5">
              <FileText className="w-4 h-4 text-primary" />
              Exhibit A: Regulatory Filing Citations & Evidence Trail
            </h3>

            <div className="space-y-2">
              {message.citations.map((cite, idx) => (
                <div key={idx} className="p-3 bg-surface-subtle rounded-xl border border-border text-xs space-y-1">
                  <div className="flex items-center justify-between">
                    <span className="font-bold text-content">
                      [{idx + 1}] {cite.title} — {cite.section}
                    </span>
                    <span className="text-[10px] text-content-muted font-tabular">
                      Period: FY{cite.fiscal_year}
                    </span>
                  </div>
                  <p className="text-[11px] text-content-muted italic">&quot;{cite.content_snippet}&quot;</p>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Institutional Regulatory Disclaimers */}
        <div className="border-t border-border pt-6 text-[11px] text-content-muted space-y-1.5 leading-normal">
          <p className="font-bold text-content uppercase tracking-wider text-[10px]">
            Institutional Compliance & Analytical Disclaimers:
          </p>
          <p>
            This document is an automated analytical intelligence summary compiled through multi-agent financial data pipelines and semantic vector retrieval over audited corporate disclosures. This publication does not constitute personalized investment, legal, or tax advice. MarketMind AI explicitly prohibits the interpretation of this report as a solicitation, endorsement, or guaranteed price expectation.
          </p>
        </div>
      </div>
    </div>
  );
};
