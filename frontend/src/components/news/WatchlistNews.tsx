"use client";

import React, { useEffect, useState } from "react";
import { watchlistApi } from "@/lib/api/watchlist";
import { NewsArticle, WatchlistItem } from "@/types";
import { Bookmark, ExternalLink, TrendingUp } from "lucide-react";
import { Badge } from "@/components/common/Badge";
import { useRouter } from "next/navigation";

interface WatchlistNewsProps {
  articles: NewsArticle[];
}

export const WatchlistNews: React.FC<WatchlistNewsProps> = ({ articles }) => {
  const router = useRouter();
  const [watchlist, setWatchlist] = useState<WatchlistItem[]>([]);
  const [isLoading, setIsLoading] = useState(false);

  useEffect(() => {
    let isMounted = true;
    async function loadWatchlist() {
      setIsLoading(true);
      try {
        const items = await watchlistApi.getWatchlist();
        if (isMounted) setWatchlist(items);
      } catch {
        if (isMounted) setWatchlist([]);
      } finally {
        if (isMounted) setIsLoading(false);
      }
    }

    loadWatchlist();
    return () => {
      isMounted = false;
    };
  }, []);

  const watchTickers = new Set(watchlist.map((w) => w.ticker));

  const matchedArticles = articles.filter(
    (a) =>
      (a.ticker && watchTickers.has(a.ticker)) ||
      a.related_tickers?.some((t) => watchTickers.has(t))
  );

  if (watchlist.length === 0 || matchedArticles.length === 0) {
    return null;
  }

  return (
    <div className="bg-surface p-5 rounded-2xl border border-border shadow-card space-y-3.5">
      <div className="flex items-center justify-between border-b border-border pb-3">
        <div className="flex items-center gap-2">
          <Bookmark className="w-4 h-4 text-primary" />
          <h3 className="text-xs font-bold text-content uppercase tracking-wider">
            Your Watchlist News Flow
          </h3>
        </div>
        <Badge variant="primary" size="sm">
          {matchedArticles.length} Monitored Items
        </Badge>
      </div>

      <div className="space-y-2.5">
        {matchedArticles.slice(0, 4).map((art) => (
          <div
            key={art.id}
            onClick={() => {
              const ticker = art.ticker || art.related_tickers?.[0];
              if (ticker) router.push(`/stocks/${encodeURIComponent(ticker)}`);
            }}
            className="p-3 bg-surface-subtle/50 hover:bg-surface-subtle rounded-xl border border-border transition-all cursor-pointer space-y-1 group"
          >
            <div className="flex items-center justify-between text-[10px] text-content-muted">
              <span className="font-bold text-content">{art.source}</span>
              <span>{art.published_at}</span>
            </div>
            <h5 className="text-xs font-bold text-content group-hover:text-primary transition-colors line-clamp-2">
              {art.title}
            </h5>
          </div>
        ))}
      </div>
    </div>
  );
};
