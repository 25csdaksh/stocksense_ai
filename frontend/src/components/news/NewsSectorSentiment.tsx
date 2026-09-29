"use client";

import React from "react";
import { SectorNewsSentiment } from "@/types";
import { PieChart, TrendingUp, TrendingDown } from "lucide-react";
import { Badge } from "@/components/common/Badge";

interface NewsSectorSentimentProps {
  sectors: SectorNewsSentiment[];
  onSelectSector?: (sector: string) => void;
}

export const NewsSectorSentiment: React.FC<NewsSectorSentimentProps> = ({
  sectors,
  onSelectSector,
}) => {
  if (sectors.length === 0) {
    return null;
  }

  return (
    <div className="bg-surface p-5 rounded-2xl border border-border shadow-card space-y-3.5">
      <div className="flex items-center justify-between border-b border-border pb-3">
        <div className="flex items-center gap-2">
          <PieChart className="w-4 h-4 text-primary" />
          <h3 className="text-xs font-bold text-content uppercase tracking-wider">
            Sector-Level Sentiment Intelligence
          </h3>
        </div>
        <span className="text-[10px] text-content-muted">Real-Time Aggregates</span>
      </div>

      <div className="space-y-2">
        {sectors.map((sec) => {
          const isPositive = sec.average_sentiment_score > 0.10;
          const isNegative = sec.average_sentiment_score < -0.10;

          return (
            <div
              key={sec.sector}
              onClick={() => onSelectSector && onSelectSector(sec.sector)}
              className="p-2.5 bg-surface-subtle/50 hover:bg-surface-subtle rounded-xl border border-border transition-all cursor-pointer space-y-1.5"
            >
              <div className="flex items-center justify-between text-xs">
                <span className="font-bold text-content">{sec.sector}</span>
                <span
                  className={`font-bold font-tabular text-[11px] ${
                    isPositive ? "text-financial-gain" : isNegative ? "text-financial-loss" : "text-content-muted"
                  }`}
                >
                  Score: {sec.average_sentiment_score > 0 ? `+` : ``}{sec.average_sentiment_score.toFixed(2)}
                </span>
              </div>

              {/* Stacked bar */}
              <div className="w-full bg-border/40 h-1.5 rounded-full overflow-hidden flex">
                <div className="bg-financial-gain h-full" style={{ width: `${sec.positive_pct}%` }} />
                <div className="bg-content-muted/40 h-full" style={{ width: `${sec.neutral_pct}%` }} />
                <div className="bg-financial-loss h-full" style={{ width: `${sec.negative_pct}%` }} />
              </div>

              <div className="flex items-center justify-between text-[10px] text-content-muted">
                <span>{sec.article_count} articles</span>
                <span>
                  {sec.positive_pct}% Pos • {sec.neutral_pct}% Neu • {sec.negative_pct}% Neg
                </span>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
};
