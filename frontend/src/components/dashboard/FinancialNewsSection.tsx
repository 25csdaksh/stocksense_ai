"use client";

import React from "react";
import Link from "next/link";
import { useNews } from "@/hooks/useNews";
import { Card, CardHeader, CardTitle, CardContent } from "@/components/common/Card";
import { Badge } from "@/components/common/Badge";
import { Button } from "@/components/common/Button";
import { Skeleton } from "@/components/common/Skeleton";
import { Newspaper, ArrowRight, ExternalLink } from "lucide-react";

export const FinancialNewsSection: React.FC = () => {
  const { news, isLoading, isDemo } = useNews(4);

  const getSentimentBadge = (label?: string) => {
    switch (label?.toUpperCase()) {
      case "POSITIVE":
        return <Badge variant="gain" size="sm">Positive</Badge>;
      case "NEGATIVE":
        return <Badge variant="loss" size="sm">Negative</Badge>;
      default:
        return <Badge variant="neutral" size="sm">Neutral</Badge>;
    }
  };

  return (
    <Card className="border-border shadow-card">
      <CardHeader className="pb-3 border-b border-border flex flex-row items-center justify-between">
        <div className="flex items-center gap-2">
          <div className="p-1.5 rounded-lg bg-secondary/10 text-secondary">
            <Newspaper className="w-4 h-4" />
          </div>
          <div>
            <CardTitle className="text-base font-bold text-content flex items-center gap-2">
              Financial News & Sentiment Feed
              {isDemo && (
                <Badge variant="gold" size="sm">
                  DEMO DATA
                </Badge>
              )}
            </CardTitle>
            <p className="text-xs text-content-muted mt-0.5">
              Live corporate disclosures, regulatory wires & NLP sentiment scoring
            </p>
          </div>
        </div>

        <Link href="/news">
          <Button
            variant="ghost"
            size="sm"
            className="text-xs text-primary hover:text-primary-dark"
            rightIcon={<ArrowRight className="w-3.5 h-3.5" />}
          >
            View All News
          </Button>
        </Link>
      </CardHeader>

      <CardContent className="p-4 sm:p-5">
        {isLoading ? (
          <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
            {[1, 2, 3, 4].map((i) => (
              <Skeleton key={i} variant="card" className="h-28" />
            ))}
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
            {news.map((item) => (
              <div
                key={item.id}
                className="p-3.5 rounded-xl bg-surface border border-border/80 hover:border-primary/30 transition-all flex flex-col justify-between space-y-2 group"
              >
                <div>
                  {/* Source, Time & Sentiment */}
                  <div className="flex items-center justify-between gap-2 mb-1.5">
                    <div className="flex items-center gap-1.5 text-[11px] text-content-muted font-medium">
                      <span>{item.source}</span>
                      <span>•</span>
                      <span className="font-mono">{item.published_at}</span>
                    </div>
                    {getSentimentBadge(item.sentiment_label)}
                  </div>

                  {/* Headline */}
                  <h4 className="text-xs sm:text-sm font-bold text-content group-hover:text-primary transition-colors leading-snug line-clamp-2">
                    {item.title}
                  </h4>

                  {/* Summary excerpt */}
                  <p className="text-xs text-content-muted mt-1 line-clamp-2 leading-relaxed">
                    {item.summary}
                  </p>
                </div>

                {/* Ticker chips */}
                <div className="flex flex-wrap items-center justify-between gap-2 pt-2 border-t border-border/50 text-[11px]">
                  <div className="flex flex-wrap gap-1.5">
                    {(item.related_tickers || []).map((ticker) => (
                      <Link
                        key={ticker}
                        href={`/stocks/${encodeURIComponent(ticker)}`}
                        className="px-1.5 py-0.5 rounded bg-surface-subtle border border-border text-content-muted hover:text-primary font-mono font-semibold transition-colors"
                      >
                        {ticker}
                      </Link>
                    ))}
                  </div>

                  <a
                    href={item.url}
                    target="_blank"
                    rel="noreferrer"
                    className="inline-flex items-center gap-1 text-[11px] text-content-muted hover:text-primary transition-colors"
                  >
                    <span>Source</span>
                    <ExternalLink className="w-3 h-3" />
                  </a>
                </div>
              </div>
            ))}
          </div>
        )}
      </CardContent>
    </Card>
  );
};
