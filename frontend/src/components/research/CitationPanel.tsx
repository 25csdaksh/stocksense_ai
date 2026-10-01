"use client";

import React from "react";
import { ResearchCitation } from "@/types";
import { FileText, ExternalLink, Calendar, BookOpen } from "lucide-react";

interface CitationPanelProps {
  citations?: ResearchCitation[];
  selectedCitationId?: string | null;
  onSelectCitation?: (citationId: string) => void;
}

export const CitationPanel: React.FC<CitationPanelProps> = ({
  citations = [],
  selectedCitationId,
  onSelectCitation,
}) => {
  if (!citations || citations.length === 0) {
    return (
      <div className="bg-surface border border-border rounded-2xl p-5 shadow-sm space-y-3 text-center">
        <BookOpen className="w-8 h-8 text-content-muted mx-auto" />
        <h4 className="text-xs font-bold text-content uppercase tracking-wider">
          Evidence & Citations
        </h4>
        <p className="text-[11px] text-content-muted">
          No external filings or news citations linked to current query.
        </p>
      </div>
    );
  }

  return (
    <div className="bg-surface border border-border rounded-2xl p-5 shadow-sm space-y-4">
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-2">
          <FileText className="w-4 h-4 text-primary" />
          <h4 className="text-xs font-bold text-content uppercase tracking-wider">
            Verified Citations ({citations.length})
          </h4>
        </div>
        <span className="text-[10px] text-content-muted font-tabular">100% Grounded</span>
      </div>

      <div className="space-y-2 max-h-[450px] overflow-y-auto pr-1">
        {citations.map((cite, idx) => {
          const isSelected = selectedCitationId === cite.citation_id;
          return (
            <div
              key={cite.citation_id || idx}
              onClick={() => onSelectCitation && onSelectCitation(cite.citation_id)}
              className={`p-3 rounded-xl border text-xs cursor-pointer transition-all space-y-1.5 ${
                isSelected
                  ? "bg-primary/10 border-primary shadow-sm"
                  : "bg-surface-subtle border-border hover:border-primary/40"
              }`}
            >
              <div className="flex items-start justify-between gap-2">
                <span className="font-bold text-content leading-tight">
                  [{idx + 1}] {cite.source_name}
                </span>
                <span className="px-1.5 py-0.5 rounded bg-surface border border-border text-[9px] font-mono text-content-muted flex-shrink-0">
                  {cite.source_type}
                </span>
              </div>

              {cite.excerpt && (
                <p className="text-[11px] text-content-muted line-clamp-3 italic">
                  &quot;{cite.excerpt}&quot;
                </p>
              )}

              {cite.source_url && (
                <a
                  href={cite.source_url}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="inline-flex items-center gap-1 text-[10px] text-primary hover:underline pt-1"
                  onClick={(e) => e.stopPropagation()}
                >
                  <span>Source URL</span>
                  <ExternalLink className="w-2.5 h-2.5" />
                </a>
              )}
            </div>
          );
        })}
      </div>
    </div>
  );
};
