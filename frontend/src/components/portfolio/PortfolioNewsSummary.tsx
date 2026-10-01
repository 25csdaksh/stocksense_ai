"use client";

import React from "react";
import { PortfolioNewsContext } from "@/types/portfolio-copilot";
import { Newspaper, ExternalLink, MessageSquare, TrendingUp, TrendingDown, Minus } from "lucide-react";

interface PortfolioNewsSummaryProps {
  news: PortfolioNewsContext;
}

export const PortfolioNewsSummary: React.FC<PortfolioNewsSummaryProps> = ({ news }) => {
  return (
    <div className="bg-surface border border-border rounded-2xl p-6 shadow-card space-y-5">
      <div className="flex items-center justify-between border-b border-border pb-4">
        <div className="flex items-center gap-2">
          <div className="p-2 rounded-xl bg-accent/10 text-accent border border-accent/20">
            <Newspaper className="w-5 h-5" />
          </div>
          <div>
            <h3 className="text-sm font-black text-content uppercase tracking-wider">
              Portfolio News Intelligence
            </h3>
            <p className="text-xs text-content-muted">
              Aggregated verified headlines across portfolio holdings ({news.articles_count} articles)
            </p>
          </div>
        </div>

        <div className="flex items-center gap-1.5 px-2.5 py-1 rounded-lg bg-surface-subtle border border-border text-xs font-bold font-tabular">
          {news.dominant_sentiment === "POSITIVE" ? (
            <TrendingUp className="w-3.5 h-3.5 text-financial-gain" />
          ) : news.dominant_sentiment === "NEGATIVE" ? (
            <TrendingDown className="w-3.5 h-3.5 text-financial-loss" />
          ) : (
            <Minus className="w-3.5 h-3.5 text-content-muted" />
          )}
          <span className="text-content">{news.dominant_sentiment}</span>
        </div>
      </div>

      {/* Headlines List */}
      {news.high_impact_articles && news.high_impact_articles.length > 0 ? (
        <div className="space-y-2.5">
          {news.high_impact_articles.map((art, idx) => (
            <div
              key={idx}
              className="p-3.5 bg-surface-subtle rounded-xl border border-border/70 hover:border-primary/40 transition-all space-y-1.5"
            >
              <div className="flex items-center justify-between text-[11px]">
                <span className="font-bold text-primary font-mono">{art.source || "News Feed"}</span>
                <span className="text-content-muted">{art.published_at ? art.published_at.slice(0, 10) : ""}</span>
              </div>
              <h4 className="text-xs font-bold text-content leading-snug">
                {art.title}
              </h4>
              {art.summary && (
                <p className="text-[11px] text-content-muted line-clamp-2 leading-relaxed">
                  {art.summary}
                </p>
              )}
            </div>
          ))}
        </div>
      ) : (
        <p className="text-xs text-content-muted italic">
          No breaking news articles indexed for current portfolio holdings.
        </p>
      )}
    </div>
  );
};
