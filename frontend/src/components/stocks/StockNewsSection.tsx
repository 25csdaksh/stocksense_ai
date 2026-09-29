"use client";

import React from "react";
import { useStockNews } from "@/hooks/useStockNews";
import { Card, CardHeader, CardTitle, CardDescription, CardContent } from "@/components/common/Card";
import { Badge } from "@/components/common/Badge";
import { Skeleton } from "@/components/common/Skeleton";
import { Button } from "@/components/common/Button";
import { Newspaper, ExternalLink, Clock, TrendingUp, TrendingDown, Minus, AlertCircle, RefreshCw } from "lucide-react";
import { cn } from "@/lib/utils";

export interface StockNewsSectionProps {
  ticker: string;
  isDemo?: boolean;
}

export const StockNewsSection: React.FC<StockNewsSectionProps> = ({
  ticker,
  isDemo: parentDemo = false,
}) => {
  const { articles, overallSentiment, averageSentimentScore, isLoading, isError, error, isDemo, refresh } =
    useStockNews(ticker);

  const displayDemo = parentDemo || isDemo;

  if (isLoading) {
    return (
      <Card className="border-border">
        <CardHeader>
          <Skeleton className="h-6 w-48" />
          <Skeleton className="h-4 w-72" />
        </CardHeader>
        <CardContent>
          <div className="space-y-3">
            {[1, 2, 3].map((i) => (
              <Skeleton key={i} className="h-24 rounded-xl" />
            ))}
          </div>
        </CardContent>
      </Card>
    );
  }

  if (isError) {
    return (
      <Card className="border-border">
        <CardContent className="py-8 text-center space-y-3">
          <AlertCircle className="w-8 h-8 text-financial-loss mx-auto" />
          <p className="text-sm font-semibold text-content">Unable to load company news</p>
          <p className="text-xs text-content-muted">{error || "Server response unavailable"}</p>
          <Button variant="outline" size="sm" onClick={() => refresh()}>
            Retry
          </Button>
        </CardContent>
      </Card>
    );
  }

  const getSentimentBadge = (label: string) => {
    const upper = label.toUpperCase();
    if (upper === "POSITIVE" || upper === "BULLISH") {
      return (
        <Badge variant="gain" size="sm" className="gap-1">
          <TrendingUp className="w-3 h-3" />
          POSITIVE
        </Badge>
      );
    }
    if (upper === "NEGATIVE" || upper === "BEARISH") {
      return (
        <Badge variant="loss" size="sm" className="gap-1">
          <TrendingDown className="w-3 h-3" />
          NEGATIVE
        </Badge>
      );
    }
    return (
      <Badge variant="neutral" size="sm" className="gap-1">
        <Minus className="w-3 h-3" />
        NEUTRAL
      </Badge>
    );
  };

  return (
    <Card className="border-border shadow-card">
      <CardHeader className="pb-3 border-b border-border/60 flex flex-col sm:flex-row sm:items-center justify-between gap-3">
        <div>
          <div className="flex items-center gap-2">
            <CardTitle className="text-lg font-bold flex items-center gap-2 text-content">
              <Newspaper className="w-5 h-5 text-primary" />
              Verified Financial News & Sentiment
            </CardTitle>
            {displayDemo && (
              <Badge variant="gold" size="sm">
                DEMO DATA
              </Badge>
            )}
            <Badge
              variant={
                overallSentiment === "BULLISH" || overallSentiment === "POSITIVE"
                  ? "gain"
                  : overallSentiment === "BEARISH" || overallSentiment === "NEGATIVE"
                  ? "loss"
                  : "neutral"
              }
              size="md"
            >
              NLP SENTIMENT: {overallSentiment} ({averageSentimentScore > 0 ? `+${averageSentimentScore.toFixed(2)}` : averageSentimentScore.toFixed(2)})
            </Badge>

          </div>
          <CardDescription className="text-xs text-content-muted">
            Institutional corporate disclosures, regulatory notifications, and market developments
          </CardDescription>
        </div>

        <button
          onClick={() => refresh()}
          className="p-1.5 self-end sm:self-center rounded-lg text-content-muted hover:text-content hover:bg-surface-subtle transition-colors"
          title="Refresh News"
        >
          <RefreshCw className="w-3.5 h-3.5" />
        </button>
      </CardHeader>

      <CardContent className="pt-4">
        {articles.length > 0 ? (
          <div className="space-y-3">
            {articles.map((item) => (
              <div
                key={item.id}
                className="p-4 rounded-xl bg-surface border border-border hover:border-primary/40 transition-colors shadow-sm space-y-2"
              >
                <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2">
                  <div className="flex items-center gap-2.5">
                    {getSentimentBadge(item.sentiment_label)}
                    <span className="text-xs font-bold text-primary">{item.source}</span>
                    <span className="text-border">•</span>
                    <span className="text-[11px] text-content-muted flex items-center gap-1">
                      <Clock className="w-3 h-3" />
                      {item.published_at}
                    </span>
                  </div>

                  {item.url && item.url !== "#" && (
                    <a
                      href={item.url}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="text-xs font-semibold text-primary hover:text-primary-dark inline-flex items-center gap-1"
                    >
                      Source Article <ExternalLink className="w-3 h-3" />
                    </a>
                  )}
                </div>

                <h2 className="text-sm font-bold text-content leading-snug">{item.title}</h2>
                {item.summary && (
                  <p className="text-xs text-content-muted leading-relaxed line-clamp-2">
                    {item.summary}
                  </p>
                )}
              </div>
            ))}
          </div>
        ) : (
          <div className="p-8 text-center rounded-xl bg-surface-subtle/50 border border-dashed border-border">
            <p className="text-xs font-semibold text-content-muted">No verified company news available.</p>
          </div>
        )}
      </CardContent>
    </Card>
  );
};
