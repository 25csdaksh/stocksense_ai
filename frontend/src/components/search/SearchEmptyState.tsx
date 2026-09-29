"use client";

import React from "react";
import { Sparkles, Brain, ArrowRight } from "lucide-react";
import { Button } from "@/components/common/Button";

interface SearchEmptyStateProps {
  query: string;
  onAskAI: (q: string) => void;
}

export const SearchEmptyState: React.FC<SearchEmptyStateProps> = ({
  query,
  onAskAI,
}) => {
  return (
    <div className="py-8 px-4 text-center space-y-4">
      <div className="w-12 h-12 rounded-2xl bg-surface-subtle border border-border flex items-center justify-center text-content-muted mx-auto">
        <Brain className="w-6 h-6 text-primary" />
      </div>

      <div className="space-y-1 max-w-sm mx-auto">
        <h4 className="text-sm font-bold text-content">No Direct Results for &ldquo;{query}&rdquo;</h4>
        <p className="text-xs text-content-muted">
          Our standard symbol directories don&apos;t match this query. Ask MarketMind multi-agent research to analyze it.
        </p>
      </div>

      <div className="pt-1">
        <Button
          variant="gold"
          size="sm"
          onClick={() => onAskAI(query)}
          leftIcon={<Sparkles className="w-3.5 h-3.5" />}
        >
          Ask MarketMind AI to Research
        </Button>
      </div>
    </div>
  );
};
