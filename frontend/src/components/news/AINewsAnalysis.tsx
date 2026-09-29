"use client";

import React, { useState } from "react";
import { useNewsAI } from "@/hooks/useNewsAI";
import { NewsArticle } from "@/types";
import { Sparkles, Send, ShieldCheck, AlertTriangle } from "lucide-react";
import { Button } from "@/components/common/Button";
import { Badge } from "@/components/common/Badge";

interface AINewsAnalysisProps {
  articles: NewsArticle[];
  selectedTicker?: string;
}

const SUGGESTED_NEWS_PROMPTS = [
  "What are the most important market developments today?",
  "What news is affecting TCS and Indian IT?",
  "Summarize today's Indian banking and credit news.",
  "What are the dominant sentiment themes across market sectors?",
  "Explain how recent news flow correlates with market volatility.",
];

export const AINewsAnalysis: React.FC<AINewsAnalysisProps> = ({
  articles,
  selectedTicker,
}) => {
  const [customQuery, setCustomQuery] = useState("");
  const { response, isLoading, error, askNewsQuestion } = useNewsAI();

  const handleAsk = (q: string) => {
    if (!q.trim() || isLoading) return;
    askNewsQuestion(q, articles, selectedTicker);
  };

  return (
    <div className="bg-surface p-5 rounded-2xl border border-border shadow-card space-y-4">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2 border-b border-border pb-3">
        <div className="flex items-center gap-2">
          <div className="w-6 h-6 rounded-lg bg-primary/10 flex items-center justify-center text-primary">
            <Sparkles className="w-3.5 h-3.5" />
          </div>
          <h3 className="text-sm font-bold text-content uppercase tracking-wider">
            AI News Intelligence & Synthesis
          </h3>
        </div>
        <Badge variant="gold" size="sm">
          MarketMind Research Agent
        </Badge>
      </div>

      <p className="text-xs text-content-muted">
        Synthesize real-time financial wires, evaluate sector sentiment dynamics, and extract causal market narratives.
      </p>

      {/* Suggested Prompts */}
      <div className="flex flex-wrap gap-2">
        {SUGGESTED_NEWS_PROMPTS.map((prompt, idx) => (
          <button
            key={idx}
            onClick={() => handleAsk(prompt)}
            disabled={isLoading}
            className="text-left text-[11px] font-medium text-primary bg-primary/5 hover:bg-primary/10 border border-primary/20 px-3 py-1.5 rounded-xl transition-all disabled:opacity-50"
          >
            {prompt}
          </button>
        ))}
      </div>

      {/* Input bar */}
      <div className="flex items-center gap-2 pt-1">
        <input
          type="text"
          value={customQuery}
          onChange={(e: React.ChangeEvent<HTMLInputElement>) => setCustomQuery(e.target.value)}
          onKeyDown={(e: React.KeyboardEvent<HTMLInputElement>) => e.key === "Enter" && handleAsk(customQuery)}
          placeholder="Ask a question about today's financial news, earnings, or macro wires..."
          className="flex-1 bg-surface-subtle border border-border rounded-xl px-3.5 py-2 text-xs text-content placeholder:text-content-muted focus:outline-none focus:border-primary"
          disabled={isLoading}
        />
        <Button
          variant="primary"
          size="sm"
          onClick={() => handleAsk(customQuery)}
          disabled={!customQuery.trim() || isLoading}
          isLoading={isLoading}
          leftIcon={<Send className="w-3.5 h-3.5" />}
        >
          Ask
        </Button>
      </div>

      {/* Error state */}
      {error && (
        <div className="bg-financial-loss/10 border border-financial-loss/30 p-3.5 rounded-xl flex items-start gap-2.5 text-xs text-financial-loss">
          <AlertTriangle className="w-4 h-4 shrink-0 mt-0.5" />
          <p>{error}</p>
        </div>
      )}

      {/* Loading state */}
      {isLoading && (
        <div className="bg-surface-subtle p-5 rounded-xl border border-border flex items-center gap-3">
          <div className="w-5 h-5 border-2 border-primary border-t-transparent rounded-full animate-spin shrink-0" />
          <p className="text-xs text-content-muted">
            Synthesizing financial wires, evaluating sentiment polarity, and generating structured synthesis...
          </p>
        </div>
      )}

      {/* AI Response Card */}
      {response && !isLoading && (
        <div className="bg-surface-subtle p-4 rounded-xl border border-border space-y-3">
          <div className="flex items-center justify-between border-b border-border/80 pb-2">
            <div className="flex items-center gap-2">
              <Sparkles className="w-4 h-4 text-primary" />
              <span className="text-xs font-bold text-content">Analysis Output</span>
            </div>
            {response.guardrail_passed && (
              <div className="flex items-center gap-1 text-[10px] text-primary font-medium">
                <ShieldCheck className="w-3.5 h-3.5" />
                <span>Guardrail Verified</span>
              </div>
            )}
          </div>

          <div className="text-xs text-content leading-relaxed whitespace-pre-line space-y-2">
            {response.answer}
          </div>

          {response.citations && response.citations.length > 0 && (
            <div className="pt-2 border-t border-border/80">
              <span className="text-[10px] text-content-muted uppercase font-semibold">Citations & References</span>
              <div className="flex flex-wrap gap-1.5 mt-1">
                {response.citations.map((c, i) => (
                  <span
                    key={i}
                    className="text-[10px] bg-surface px-2 py-0.5 rounded border border-border text-content-muted"
                  >
                    {c.source || c.title || `Wire [${i + 1}]`}
                  </span>
                ))}
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
};
