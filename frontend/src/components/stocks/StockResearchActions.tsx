"use client";

import React from "react";
import { Button } from "@/components/common/Button";
import {
  Sparkles,
  Zap,
  FileText,
  Activity,
  Newspaper,
  ArrowRightLeft,
} from "lucide-react";

export interface StockResearchActionsProps {
  ticker: string;
  onSelectAction: (prompt: string) => void;
  onOpenCompare?: () => void;
}

export const StockResearchActions: React.FC<StockResearchActionsProps> = ({
  ticker,
  onSelectAction,
  onOpenCompare,
}) => {
  const actions = [
    {
      id: "analyze-stock",
      label: "Analyze Stock",
      icon: <Sparkles className="w-4 h-4 text-accent" />,
      prompt: `Analyze ${ticker} using available market, technical, fundamental, and news data.`,
    },
    {
      id: "explain-anomaly",
      label: "Explain Anomaly",
      icon: <Zap className="w-4 h-4 text-accent" />,
      prompt: `Explain recent statistical anomalies, volume bursts, and volatility regimes detected in ${ticker}.`,
    },
    {
      id: "analyze-fundamentals",
      label: "Analyze Fundamentals",
      icon: <FileText className="w-4 h-4 text-primary" />,
      prompt: `Evaluate ${ticker}'s valuation multiples, operating margins, cash flow strength, and Altman Z-score.`,
    },
    {
      id: "analyze-technicals",
      label: "Analyze Technicals",
      icon: <Activity className="w-4 h-4 text-secondary" />,
      prompt: `Examine ${ticker}'s technical momentum, RSI-14, MACD signal, and Bollinger Band envelopes.`,
    },
    {
      id: "summarize-news",
      label: "Summarize News",
      icon: <Newspaper className="w-4 h-4 text-primary" />,
      prompt: `Summarize verified regulatory filings, corporate developments, and market news for ${ticker}.`,
    },
    {
      id: "compare-stock",
      label: "Compare Stock",
      icon: <ArrowRightLeft className="w-4 h-4 text-secondary" />,
      customHandler: () => onOpenCompare?.(),
    },
  ];

  return (
    <div className="bg-surface border border-border rounded-2xl p-4 shadow-sm space-y-3">
      <div className="flex items-center justify-between">
        <span className="text-xs font-extrabold uppercase tracking-wider text-content flex items-center gap-1.5">
          <Sparkles className="w-4 h-4 text-accent" />
          AI Research Quick Commands
        </span>
        <span className="text-[11px] text-content-muted">1-Click Deep Synthesis</span>
      </div>

      <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-6 gap-2">
        {actions.map((act) => (
          <Button
            key={act.id}
            variant="outline"
            size="sm"
            onClick={() => {
              if (act.customHandler) {
                act.customHandler();
              } else if (act.prompt) {
                onSelectAction(act.prompt);
              }
            }}
            className="w-full justify-start text-xs font-semibold hover:border-primary hover:bg-primary-light/10"
            leftIcon={act.icon}
          >
            {act.label}
          </Button>
        ))}
      </div>
    </div>
  );
};
