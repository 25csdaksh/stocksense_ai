"use client";

import React from "react";
import { NewsArticle } from "@/types";
import { Clock, TrendingUp } from "lucide-react";
import { Badge } from "@/components/common/Badge";
import { useRouter } from "next/navigation";

interface NewsTimelineProps {
  articles: NewsArticle[];
}

export const NewsTimeline: React.FC<NewsTimelineProps> = ({ articles }) => {
  const router = useRouter();

  if (articles.length === 0) {
    return null;
  }

  // Group into timeline buckets
  const todayArticles = articles.slice(0, 5);
  const earlierArticles = articles.slice(5, 10);

  return (
    <div className="bg-surface p-5 rounded-2xl border border-border shadow-card space-y-4">
      <div className="flex items-center justify-between border-b border-border pb-3">
        <div className="flex items-center gap-2">
          <Clock className="w-4 h-4 text-primary" />
          <h3 className="text-xs font-bold text-content uppercase tracking-wider">
            Chronological News Flow Timeline
          </h3>
        </div>
        <span className="text-[10px] text-content-muted">Real-Time Timestamped</span>
      </div>

      <div className="relative pl-4 border-l-2 border-primary/30 space-y-4">
        {todayArticles.map((art) => {
          const isPos = art.sentiment_label === "POSITIVE" || art.sentiment_label === "BULLISH";
          const isNeg = art.sentiment_label === "NEGATIVE" || art.sentiment_label === "BEARISH";

          return (
            <div key={art.id} className="relative group cursor-pointer" onClick={() => {
              const ticker = art.ticker || (art.related_tickers && art.related_tickers[0]);
              if (ticker) router.push(`/stocks/${encodeURIComponent(ticker)}`);
            }}>
              {/* Timeline marker node */}
              <div
                className={`absolute -left-[21px] top-1 w-2.5 h-2.5 rounded-full border-2 border-surface transition-transform group-hover:scale-125 ${
                  isPos ? "bg-financial-gain" : isNeg ? "bg-financial-loss" : "bg-primary"
                }`}
              />

              <div className="space-y-1">
                <div className="flex flex-wrap items-center gap-2 text-[10px] text-content-muted">
                  <span className="font-semibold text-content">{art.published_at}</span>
                  <span>•</span>
                  <span>{art.source}</span>
                  {art.ticker && (
                    <Badge variant="outline" size="sm">
                      {art.ticker}
                    </Badge>
                  )}
                  <Badge variant={isPos ? "gain" : isNeg ? "loss" : "neutral"} size="sm">
                    {art.sentiment_label}
                  </Badge>
                </div>
                <p className="text-xs font-bold text-content group-hover:text-primary transition-colors line-clamp-2">
                  {art.title}
                </p>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
};
