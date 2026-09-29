"use client";

import React, { useState } from "react";
import { useRouter } from "next/navigation";
import { Card, CardContent } from "@/components/common/Card";
import { Button } from "@/components/common/Button";
import { Brain, ArrowRight, Sparkles, Send } from "lucide-react";

const SUGGESTED_QUERIES = [
  "Why did TCS.NS move today?",
  "Compare TCS.NS and INFY.NS operating margins",
  "What unusual activity is happening in NIFTY IT?",
  "Explain the latest anomaly in RELIANCE.NS",
  "Synthesize RBI monetary stance on Bank Nifty",
];

export const AIResearchQuickLaunch: React.FC = () => {
  const router = useRouter();
  const [query, setQuery] = useState("");

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!query.trim()) return;
    router.push(`/research?q=${encodeURIComponent(query.trim())}`);
  };

  const handleSelectQuery = (sq: string) => {
    setQuery(sq);
    router.push(`/research?q=${encodeURIComponent(sq)}`);
  };

  return (
    <Card className="border-primary/40 bg-gradient-to-r from-surface to-primary/5 shadow-card overflow-hidden">
      <CardContent className="p-4 sm:p-6 space-y-3.5">
        <div className="flex items-center gap-2">
          <div className="p-1.5 rounded-lg bg-primary text-accent">
            <Brain className="w-4 h-4 text-accent" />
          </div>
          <div>
            <h3 className="text-sm sm:text-base font-bold text-primary-dark flex items-center gap-2">
              Deep AI Research & LangGraph Multi-Agent Assistant
              <Sparkles className="w-3.5 h-3.5 text-accent animate-pulse" />
            </h3>
            <p className="text-xs text-content-muted">
              Query cross-asset valuation models, SEC 10-K regulatory filings, and volatility forecasts
            </p>
          </div>
        </div>

        {/* Input Form */}
        <form onSubmit={handleSubmit} className="relative flex items-center">
          <input
            type="text"
            placeholder="Ask MarketMind anything about the market (e.g., 'Analyze TCS vs INFY valuation multiples')..."
            value={query}
            onChange={(e: React.ChangeEvent<HTMLInputElement>) => setQuery(e.target.value)}
            className="w-full h-12 pl-4 pr-28 rounded-xl border border-border bg-surface text-xs sm:text-sm text-content placeholder:text-content-muted/70 focus:outline-none focus:ring-2 focus:ring-primary/20 focus:border-primary shadow-xs transition-all"
          />
          <div className="absolute right-1.5 flex items-center">
            <Button
              type="submit"
              variant="primary"
              size="sm"
              className="h-9 px-3.5 text-xs font-semibold shadow-xs"
              rightIcon={<Send className="w-3 h-3 text-accent" />}
            >
              Analyze
            </Button>
          </div>
        </form>

        {/* Suggested Queries Chips */}
        <div className="flex flex-wrap items-center gap-1.5 pt-0.5">
          <span className="text-[11px] font-semibold text-content-muted mr-1">Quick Inquiries:</span>
          {SUGGESTED_QUERIES.map((sq, i) => (
            <button
              key={i}
              type="button"
              onClick={() => handleSelectQuery(sq)}
              className="text-[11px] px-2.5 py-1 rounded-lg bg-surface border border-border text-content-muted hover:text-primary hover:border-primary/40 hover:bg-surface-subtle transition-all truncate max-w-xs"
            >
              {sq}
            </button>
          ))}
        </div>
      </CardContent>
    </Card>
  );
};
