"use client";

import React from "react";
import { NewsArticle } from "@/types";
import { Zap, TrendingUp, Sparkles } from "lucide-react";
import { Badge } from "@/components/common/Badge";
import { useRouter } from "next/navigation";

interface NewsImportantSectionProps {
  articles: NewsArticle[];
}

export const NewsImportantSection: React.FC<NewsImportantSectionProps> = ({ articles }) => {
  const router = useRouter();

  // Pick top 2 most impactful / market moving articles
  const importantArticles = articles
    .filter((a) => a.is_market_moving || Math.abs(a.sentiment_score || 0) > 0.40)
    .slice(0, 2);

  if (importantArticles.length === 0) {
    return null;
  }

  return (
    <div className="bg-primary/5 p-4 rounded-2xl border border-primary/20 space-y-3">
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-2">
          <div className="p-1.5 rounded-lg bg-primary text-white">
            <Zap className="w-3.5 h-3.5" />
          </div>
          <h3 className="text-xs font-bold text-content uppercase tracking-wider">
            Market-Moving / High Impact Wire
          </h3>
        </div>
        <Badge variant="gold" size="sm">
          High Salience
        </Badge>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
        {importantArticles.map((art) => {
          const isPos = (art.sentiment_score || 0) > 0;

          return (
            <div
              key={art.id}
              onClick={() => {
                const ticker = art.ticker || (art.related_tickers && art.related_tickers[0]);
                if (ticker) {
                  router.push(`/research?ticker=${encodeURIComponent(ticker)}&q=${encodeURIComponent(art.title)}`);
                } else {
                  router.push(`/research?q=${encodeURIComponent(art.title)}`);
                }
              }}
              className="p-3.5 bg-surface rounded-xl border border-border hover:border-primary/50 transition-all cursor-pointer space-y-1.5 group"
            >
              <div className="flex items-center justify-between text-[10px] text-content-muted">
                <span className="font-bold text-content">{art.source}</span>
                <span className={`font-bold font-tabular ${isPos ? "text-financial-gain" : "text-financial-loss"}`}>
                  {art.sentiment_label}
                </span>
              </div>
              <h4 className="text-xs font-bold text-content group-hover:text-primary transition-colors line-clamp-2">
                {art.title}
              </h4>
              <p className="text-[11px] text-content-muted line-clamp-2">
                {art.summary}
              </p>
            </div>
          );
        })}
      </div>
    </div>
  );
};
