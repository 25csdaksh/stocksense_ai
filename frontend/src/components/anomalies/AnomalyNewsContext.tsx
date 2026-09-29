"use client";

import React from "react";
import { Card, CardHeader, CardTitle, CardDescription, CardContent } from "@/components/common/Card";
import { Badge } from "@/components/common/Badge";
import { NewsArticle } from "@/types";
import { Newspaper, ExternalLink, Clock, TrendingUp, TrendingDown } from "lucide-react";

export interface AnomalyNewsContextProps {
  ticker: string;
  news: NewsArticle[];
  isLoading?: boolean;
}

export const AnomalyNewsContext: React.FC<AnomalyNewsContextProps> = ({
  ticker,
  news,
  isLoading = false,
}) => {
  return (
    <Card>
      <CardHeader className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-2 pb-2">
        <div>
          <div className="flex items-center gap-2">
            <CardTitle className="flex items-center gap-2">
              <Newspaper className="w-4 h-4 text-primary" />
              Verified News &amp; Disclosure Context: {ticker}
            </CardTitle>
            <Badge variant="neutral" size="sm">
              {news.length} Articles
            </Badge>
          </div>
          <CardDescription>
            Regulatory filings and market press releases matching current anomaly timeframe.
          </CardDescription>
        </div>
      </CardHeader>

      <CardContent>
        {isLoading ? (
          <div className="p-8 text-center text-xs text-content-muted">
            Retrieving verified market headlines...
          </div>
        ) : news.length === 0 ? (
          <div className="p-8 text-center bg-surface-subtle/50 rounded-xl border border-dashed border-border text-xs text-content-muted">
            No verified related news or regulatory disclosures available for {ticker} during this session.
          </div>
        ) : (
          <div className="space-y-2.5">
            {news.map((item) => {
              const isPositive = item.sentiment_label === "POSITIVE" || item.sentiment_label === "BULLISH";
              const isNegative = item.sentiment_label === "NEGATIVE" || item.sentiment_label === "BEARISH";

              return (
                <div
                  key={item.id}
                  className="p-3 bg-surface-subtle/60 rounded-xl border border-border hover:bg-surface-subtle transition-all space-y-1.5"
                >
                  <div className="flex items-start justify-between gap-3">
                    <h4 className="text-xs font-bold text-content leading-snug hover:text-primary transition-colors">
                      {item.title}
                    </h4>
                    <Badge
                      variant={isPositive ? "gain" : isNegative ? "loss" : "neutral"}
                      size="sm"
                      className="text-[9px] uppercase font-bold shrink-0"
                    >
                      {item.sentiment_label || "NEUTRAL"}
                    </Badge>
                  </div>

                  <p className="text-[11px] text-content-muted line-clamp-2 leading-relaxed">
                    {item.summary}
                  </p>

                  <div className="flex items-center justify-between text-[10px] text-content-muted pt-1 border-t border-border/40">
                    <span className="font-semibold text-content">{item.source || "Market Wire"}</span>
                    <span className="flex items-center gap-1">
                      <Clock className="w-3 h-3" />
                      {item.published_at || "Recent"}
                    </span>
                  </div>
                </div>
              );
            })}
          </div>
        )}
      </CardContent>
    </Card>
  );
};
