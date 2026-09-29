"use client";

import React, { useState } from "react";
import { CitationItem } from "@/types";
import { Card, CardHeader, CardTitle, CardDescription, CardContent } from "@/components/common/Card";
import { Badge } from "@/components/common/Badge";
import { Button } from "@/components/common/Button";
import {
  FileText,
  Search,
  ExternalLink,
  Layers,
  Filter,
  CheckCircle2,
  BookOpen,
} from "lucide-react";
import { cn } from "@/lib/utils";

export interface ResearchEvidencePanelProps {
  citations: CitationItem[];
  selectedCitation?: CitationItem | null;
  onSelectCitation?: (citation: CitationItem | null) => void;
}

type SourceFilter = "ALL" | "FILINGS" | "NEWS" | "RESEARCH";

export const ResearchEvidencePanel: React.FC<ResearchEvidencePanelProps> = ({
  citations,
  selectedCitation,
  onSelectCitation,
}) => {
  const [filter, setFilter] = useState<SourceFilter>("ALL");
  const [activeModalCitation, setActiveModalCitation] = useState<CitationItem | null>(null);

  const filteredCitations = citations.filter((c) => {
    if (filter === "FILINGS") {
      return (
        c.filing_type?.toLowerCase().includes("filing") ||
        c.filing_type?.toLowerCase().includes("10-k") ||
        c.filing_type?.toLowerCase().includes("annual")
      );
    }
    if (filter === "NEWS") {
      return c.filing_type?.toLowerCase().includes("news") || c.title?.toLowerCase().includes("news");
    }
    if (filter === "RESEARCH") {
      return c.filing_type?.toLowerCase().includes("research") || c.title?.toLowerCase().includes("research");
    }
    return true;
  });

  return (
    <Card className="border-border shadow-card bg-surface overflow-hidden">
      <CardHeader className="py-3 px-4 border-b border-border/60 bg-surface-subtle/50 flex flex-col sm:flex-row sm:items-center justify-between gap-2">
        <div className="flex items-center gap-2">
          <BookOpen className="w-4 h-4 text-primary" />
          <CardTitle className="text-xs font-bold uppercase tracking-wider text-content">
            RAG Evidence & Filings
          </CardTitle>
          <Badge variant="primary" size="sm">
            {citations.length} CHUNKS
          </Badge>
        </div>

        {/* Filter Pills */}
        <div className="flex items-center gap-1 overflow-x-auto">
          {(["ALL", "FILINGS", "NEWS", "RESEARCH"] as SourceFilter[]).map((f) => (
            <button
              key={f}
              onClick={() => setFilter(f)}
              className={cn(
                "px-2 py-0.5 text-[10px] font-bold rounded-md transition-all",
                filter === f
                  ? "bg-primary text-white"
                  : "text-content-muted hover:text-content hover:bg-surface"
              )}
            >
              {f}
            </button>
          ))}
        </div>
      </CardHeader>

      <CardContent className="p-4 space-y-3 max-h-[600px] overflow-y-auto">
        {filteredCitations.length > 0 ? (
          filteredCitations.map((item, idx) => (
            <div
              key={item.id || idx}
              onClick={() => {
                onSelectCitation?.(item);
                setActiveModalCitation(item);
              }}
              className={cn(
                "p-3 rounded-xl border transition-all cursor-pointer space-y-1.5",
                selectedCitation?.id === item.id
                  ? "bg-primary-light/10 border-primary ring-1 ring-primary/20"
                  : "bg-surface hover:bg-surface-subtle border-border hover:border-primary/40"
              )}
            >
              <div className="flex items-center justify-between gap-2">
                <span className="text-xs font-bold text-content line-clamp-1">
                  {item.title}
                </span>
                {item.relevance_score !== undefined && (
                  <span className="text-[10px] font-bold text-primary font-tabular flex-shrink-0">
                    {Math.round(item.relevance_score * 100)}% REL
                  </span>
                )}
              </div>

              <div className="flex items-center gap-2 text-[10px] text-content-muted">
                <Badge variant="neutral" size="sm">
                  {item.filing_type || "Filing"}
                </Badge>
                {item.fiscal_year && <span>FY{item.fiscal_year}</span>}
                {item.section && (
                  <>
                    <span>•</span>
                    <span className="line-clamp-1">{item.section}</span>
                  </>
                )}
              </div>

              <p className="text-[11px] text-content-muted leading-relaxed line-clamp-3 italic">
                &quot;{item.content_snippet}&quot;
              </p>

              <div className="pt-1 flex items-center justify-between text-[10px] text-primary font-semibold">
                <span>Inspect Evidence Chunk →</span>
                {item.page_number ? <span>Page {item.page_number}</span> : null}
              </div>
            </div>
          ))
        ) : (
          <div className="p-6 text-center rounded-xl bg-surface-subtle/50 border border-dashed border-border space-y-1">
            <FileText className="w-5 h-5 text-content-muted mx-auto" />
            <p className="text-xs font-semibold text-content">Source unavailable</p>
            <p className="text-[11px] text-content-muted">
              No matching filing evidence retrieved for the active search filter.
            </p>
          </div>
        )}
      </CardContent>

      {/* Detail Chunk Modal */}
      {activeModalCitation && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50 backdrop-blur-sm p-4 animate-fade-in">
          <div className="bg-surface border border-border rounded-2xl w-full max-w-lg shadow-modal overflow-hidden p-5 space-y-4">
            <div className="flex items-center justify-between border-b border-border pb-3">
              <div>
                <h3 className="text-sm font-bold text-content">{activeModalCitation.title}</h3>
                <p className="text-xs text-primary font-medium">{activeModalCitation.section}</p>
              </div>
              <Badge variant="primary" size="md">
                {activeModalCitation.relevance_score
                  ? `${Math.round(activeModalCitation.relevance_score * 100)}% Relevance`
                  : "Verified"}
              </Badge>
            </div>

            <div className="p-3.5 bg-surface-subtle rounded-xl border border-border text-xs leading-relaxed text-content max-h-60 overflow-y-auto">
              <p className="font-mono">{activeModalCitation.content_snippet}</p>
            </div>

            <div className="flex justify-between items-center text-xs text-content-muted">
              <span>Filing Type: {activeModalCitation.filing_type}</span>
              <span>Fiscal Period: FY{activeModalCitation.fiscal_year}</span>
            </div>

            <div className="flex justify-end pt-2">
              <Button variant="outline" size="sm" onClick={() => setActiveModalCitation(null)}>
                Close Evidence
              </Button>
            </div>
          </div>
        </div>
      )}
    </Card>
  );
};
