"use client";

import React, { useState, useRef, useEffect } from "react";
import { Button } from "@/components/common/Button";
import { Card, CardContent } from "@/components/common/Card";
import { Badge } from "@/components/common/Badge";
import { Sparkles, Send, Loader2, HelpCircle, CornerDownLeft, Search } from "lucide-react";

export interface ResearchComposerProps {
  selectedTicker: string | null;
  onSelectTicker: (ticker: string | null) => void;
  onSubmit: (query: string) => void;
  isProcessing: boolean;
  initialQuery?: string;
}

const SUGGESTED_RESEARCH_PROMPTS = [
  "Why did TCS move recently?",
  "Analyze RELIANCE.NS fundamentals and recent risks",
  "Explain the latest anomaly in HDFCBANK.NS",
  "Compare TCS and INFY using available data",
  "What are the major risks affecting Indian IT stocks?",
  "Summarize the latest available financial filing for TCS",
  "Analyze the relationship between crude oil and Indian energy stocks",
  "Explain unusual volatility in the market",
];

export const ResearchComposer: React.FC<ResearchComposerProps> = ({
  selectedTicker,
  onSelectTicker,
  onSubmit,
  isProcessing,
  initialQuery = "",
}) => {
  const [query, setQuery] = useState(initialQuery);
  const textareaRef = useRef<HTMLTextAreaElement | null>(null);

  useEffect(() => {
    if (initialQuery) {
      setQuery(initialQuery);
    }
  }, [initialQuery]);

  const handleSubmit = (e?: React.FormEvent) => {
    if (e) e.preventDefault();
    if (!query.trim() || isProcessing) return;
    onSubmit(query.trim());
    setQuery("");
  };

  const handleKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSubmit();
    }
  };

  const handlePromptClick = (prompt: string) => {
    setQuery(prompt);
    if (textareaRef.current) {
      textareaRef.current.focus();
    }
  };

  return (
    <Card className="border-primary/20 shadow-card bg-surface overflow-hidden">
      <CardContent className="p-4.5 space-y-3.5">
        {/* Composer Input Area */}
        <div className="relative rounded-xl border border-border bg-surface-subtle/50 focus-within:border-primary focus-within:ring-2 focus-within:ring-primary/15 transition-all">
          <textarea
            ref={textareaRef}
            rows={3}
            value={query}
            onChange={(e: React.ChangeEvent<HTMLTextAreaElement>) => setQuery(e.target.value)}
            onKeyDown={handleKeyDown}
            disabled={isProcessing}
            placeholder={
              selectedTicker
                ? `Ask MarketMind to investigate ${selectedTicker} (valuation, risk factors, filings, volatility, anomalies)...`
                : "Ask MarketMind to investigate a company, market event, risk, anomaly, sector or financial filing..."
            }
            className="w-full bg-transparent p-3.5 text-xs sm:text-sm text-content placeholder:text-content-muted/70 focus:outline-none resize-none leading-relaxed"
          />

          {/* Bottom Bar inside Input Box */}
          <div className="flex flex-wrap items-center justify-between gap-2 px-3.5 pb-3 pt-1 text-[11px] text-content-muted border-t border-border/40">
            <div className="flex items-center gap-2">
              <span className="flex items-center gap-1 font-medium">
                <CornerDownLeft className="w-3 h-3 text-primary" />
                <strong>Enter</strong> to run
              </span>
              <span className="text-border">•</span>
              <span><strong>Shift + Enter</strong> for newline</span>
            </div>

            <Button
              variant="gold"
              size="sm"
              disabled={isProcessing || !query.trim()}
              onClick={() => handleSubmit()}
              leftIcon={
                isProcessing ? (
                  <Loader2 className="w-4 h-4 animate-spin" />
                ) : (
                  <Sparkles className="w-4 h-4" />
                )
              }
            >
              {isProcessing ? "Researching..." : "Synthesize Research"}
            </Button>
          </div>
        </div>

        {/* Suggested Research Prompts Carousel / Chips */}
        <div className="space-y-2">
          <div className="flex items-center justify-between">
            <span className="text-[11px] font-bold text-content-muted uppercase tracking-wider flex items-center gap-1.5">
              <HelpCircle className="w-3.5 h-3.5 text-primary" />
              Suggested Research Questions
            </span>
          </div>

          <div className="flex flex-wrap gap-1.5">
            {SUGGESTED_RESEARCH_PROMPTS.map((prompt, idx) => (
              <button
                key={idx}
                onClick={() => handlePromptClick(prompt)}
                disabled={isProcessing}
                className="text-[11px] font-medium px-2.5 py-1 rounded-lg bg-surface-subtle hover:bg-primary-light/10 text-content hover:text-primary border border-border hover:border-primary/40 transition-all text-left disabled:opacity-50"
              >
                {prompt}
              </button>
            ))}
          </div>
        </div>
      </CardContent>
    </Card>
  );
};
