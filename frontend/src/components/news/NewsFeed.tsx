"use client";

import React, { useState } from "react";
import { NewsArticle } from "@/types";
import { NewsArticleCard } from "./NewsArticleCard";
import { Newspaper, ChevronDown } from "lucide-react";
import { Button } from "@/components/common/Button";

interface NewsFeedProps {
  articles: NewsArticle[];
  isLoading: boolean;
  onSelectTicker?: (ticker: string) => void;
}

const ITEMS_PER_PAGE = 10;

export const NewsFeed: React.FC<NewsFeedProps> = ({
  articles,
  isLoading,
  onSelectTicker,
}) => {
  const [displayCount, setDisplayCount] = useState(ITEMS_PER_PAGE);

  if (isLoading) {
    return (
      <div className="space-y-3">
        {[1, 2, 3, 4].map((i) => (
          <div key={i} className="bg-surface p-5 rounded-xl border border-border animate-pulse space-y-3">
            <div className="flex gap-2 w-1/3 h-4 bg-surface-subtle rounded" />
            <div className="w-3/4 h-5 bg-surface-subtle rounded" />
            <div className="w-full h-10 bg-surface-subtle rounded" />
          </div>
        ))}
      </div>
    );
  }

  if (articles.length === 0) {
    return (
      <div className="bg-surface p-12 rounded-2xl border border-border shadow-card flex flex-col items-center justify-center text-center space-y-3">
        <div className="w-12 h-12 rounded-2xl bg-surface-subtle border border-border flex items-center justify-center text-content-muted">
          <Newspaper className="w-6 h-6" />
        </div>
        <div className="space-y-1">
          <h4 className="text-sm font-bold text-content">No Verified News Found</h4>
          <p className="text-xs text-content-muted max-w-sm">
            No verified financial news matches your current filter criteria. Try broadening your market or sentiment filters.
          </p>
        </div>
      </div>
    );
  }

  const visibleArticles = articles.slice(0, displayCount);
  const hasMore = displayCount < articles.length;

  return (
    <div className="space-y-3">
      {visibleArticles.map((article) => (
        <NewsArticleCard
          key={article.id}
          article={article}
          onSelectTicker={onSelectTicker}
        />
      ))}

      {hasMore && (
        <div className="pt-2 text-center">
          <Button
            variant="outline"
            size="sm"
            onClick={() => setDisplayCount((prev) => prev + ITEMS_PER_PAGE)}
            leftIcon={<ChevronDown className="w-4 h-4" />}
          >
            Load More Articles ({articles.length - displayCount} remaining)
          </Button>
        </div>
      )}
    </div>
  );
};
