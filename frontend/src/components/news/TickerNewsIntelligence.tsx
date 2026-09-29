"use client";

import React, { useState, useEffect } from "react";
import { newsApi } from "@/lib/api/news";
import { NewsSentimentSummary } from "@/types";
import { TrendingUp, Sparkles, BookOpen, ExternalLink } from "lucide-react";
import { Badge } from "@/components/common/Badge";
import { useRouter } from "next/navigation";

interface TickerNewsIntelligenceProps {
  selectedTicker: string;
  onSelectTicker: (ticker: string) => void;
}

const POPULAR_TICKERS = [
  "RELIANCE.NS",
  "TCS.NS",
  "INFY.NS",
  "HDFCBANK.NS",
  "ICICIBANK.NS",
  "TATAMOTORS.NS",
];

export const TickerNewsIntelligence: React.FC<TickerNewsIntelligenceProps> = ({
  selectedTicker,
  onSelectTicker,
}) => {
  const router = useRouter();
  const [summary, setSummary] = useState<NewsSentimentSummary | null>(null);
  const [isLoading, setIsLoading] = useState(false);

  const activeTicker = selectedTicker === "ALL" ? "RELIANCE.NS" : selectedTicker;

  useEffect(() => {
    let isMounted = true;
    async function loadTickerNews() {
      setIsLoading(true);
      try {
        const res = await newsApi.getTickerNews(activeTicker, 5);
        if (isMounted) setSummary(res);
      } catch {
        if (isMounted) setSummary(null);
      } finally {
        if (isMounted) setIsLoading(false);
      }
    }

    loadTickerNews();
    return () => {
      isMounted = false;
    };
  }, [activeTicker]);

  return (
    <div className="bg-surface p-5 rounded-2xl border border-border shadow-card space-y-4">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2 border-b border-border pb-3">
        <div className="flex items-center gap-2">
          <TrendingUp className="w-4 h-4 text-primary" />
          <h3 className="text-xs font-bold text-content uppercase tracking-wider">
            Ticker News Telemetry
          </h3>
        </div>

        {/* Ticker Selector */}
        <select
          value={activeTicker}
          onChange={(e: React.ChangeEvent<HTMLSelectElement>) => onSelectTicker(e.target.value)}
          className="bg-surface-subtle border border-border rounded-lg text-xs font-semibold text-content px-2 py-1 focus:outline-none focus:border-primary"
        >
          {POPULAR_TICKERS.map((t) => (
            <option key={t} value={t}>
              {t}
            </option>
          ))}
        </select>
      </div>

      {isLoading ? (
        <div className="h-40 flex items-center justify-center">
          <div className="w-6 h-6 border-2 border-primary border-t-transparent rounded-full animate-spin" />
        </div>
      ) : summary ? (
        <div className="space-y-3">
          <div className="flex items-center justify-between p-3 bg-surface-subtle rounded-xl border border-border">
            <div>
              <span className="text-[10px] text-content-muted uppercase font-semibold">Aggregate Polarity</span>
              <p className="text-xs font-bold text-content mt-0.5">
                {summary.ticker}: {summary.overall_sentiment}
              </p>
            </div>
            <Badge
              variant={
                summary.overall_sentiment === "BULLISH"
                  ? "gain"
                  : summary.overall_sentiment === "BEARISH"
                  ? "loss"
                  : "neutral"
              }
              size="sm"
            >
              Avg Score: {summary.average_sentiment_score > 0 ? `+` : ``}{summary.average_sentiment_score}
            </Badge>
          </div>

          <div className="space-y-2">
            {summary.news_items?.slice(0, 3).map((item) => (
              <div
                key={item.id}
                onClick={() =>
                  router.push(
                    `/research?ticker=${encodeURIComponent(summary.ticker)}&q=${encodeURIComponent(item.title)}`
                  )
                }
                className="p-2.5 bg-surface-subtle/40 hover:bg-surface-subtle rounded-xl border border-border transition-all cursor-pointer space-y-1"
              >
                <div className="flex items-center justify-between text-[10px] text-content-muted">
                  <span>{item.source}</span>
                  <span>{item.published_at}</span>
                </div>
                <h5 className="text-xs font-bold text-content hover:text-primary transition-colors line-clamp-2">
                  {item.title}
                </h5>
              </div>
            ))}
          </div>

          <div className="flex items-center justify-between pt-2 border-t border-border/80">
            <button
              onClick={() => router.push(`/stocks/${encodeURIComponent(summary.ticker)}`)}
              className="text-xs font-semibold text-primary hover:underline flex items-center gap-1"
            >
              <TrendingUp className="w-3.5 h-3.5" />
              <span>Stock Workspace</span>
            </button>
            <button
              onClick={() => router.push(`/research?ticker=${encodeURIComponent(summary.ticker)}`)}
              className="text-xs font-semibold text-secondary hover:underline flex items-center gap-1"
            >
              <Sparkles className="w-3.5 h-3.5" />
              <span>Research Agent</span>
            </button>
          </div>
        </div>
      ) : (
        <div className="h-32 flex items-center justify-center text-xs text-content-muted">
          No ticker-specific news available.
        </div>
      )}
    </div>
  );
};
