"use client";

import { useState, useMemo } from "react";
import { NewsArticle } from "@/types";

export interface NewsFilterState {
  market: "ALL" | "INDIA" | "GLOBAL";
  asset: "ALL" | "STOCKS" | "INDICES" | "SECTORS" | "MACRO";
  sentiment: "ALL" | "POSITIVE" | "NEUTRAL" | "NEGATIVE";
  timeWindow: "ALL" | "1H" | "6H" | "1D" | "1W";
  searchQuery: string;
  selectedSector: string;
  selectedTicker: string;
}

export const DEFAULT_NEWS_FILTERS: NewsFilterState = {
  market: "ALL",
  asset: "ALL",
  sentiment: "ALL",
  timeWindow: "ALL",
  searchQuery: "",
  selectedSector: "ALL",
  selectedTicker: "ALL",
};

export function useNewsFilters(articles: NewsArticle[]) {
  const [filters, setFilters] = useState<NewsFilterState>(DEFAULT_NEWS_FILTERS);

  const updateFilter = <K extends keyof NewsFilterState>(key: K, value: NewsFilterState[K]) => {
    setFilters((prev) => ({ ...prev, [key]: value }));
  };

  const resetFilters = () => {
    setFilters(DEFAULT_NEWS_FILTERS);
  };

  const filteredArticles = useMemo(() => {
    return articles.filter((art) => {
      // 1. Search Query (headline, summary, ticker, source)
      if (filters.searchQuery.trim()) {
        const query = filters.searchQuery.toLowerCase();
        const matchesTitle = art.title.toLowerCase().includes(query);
        const matchesSummary = art.summary?.toLowerCase().includes(query);
        const matchesSource = art.source.toLowerCase().includes(query);
        const matchesTicker = art.ticker?.toLowerCase().includes(query);
        const matchesRelated = art.related_tickers?.some((t) => t.toLowerCase().includes(query));

        if (!matchesTitle && !matchesSummary && !matchesSource && !matchesTicker && !matchesRelated) {
          return false;
        }
      }

      // 2. Sentiment Filter
      if (filters.sentiment !== "ALL") {
        const s = art.sentiment_label?.toUpperCase();
        if (filters.sentiment === "POSITIVE" && s !== "POSITIVE" && s !== "BULLISH") return false;
        if (filters.sentiment === "NEGATIVE" && s !== "NEGATIVE" && s !== "BEARISH") return false;
        if (filters.sentiment === "NEUTRAL" && s !== "NEUTRAL") return false;
      }

      // 3. Market Filter
      if (filters.market === "INDIA") {
        const isIndia = art.ticker?.endsWith(".NS") || art.ticker?.endsWith(".BO") || art.related_tickers?.some((t) => t.endsWith(".NS"));
        if (!isIndia && art.market !== "INDIA") return false;
      } else if (filters.market === "GLOBAL") {
        const isIndia = art.ticker?.endsWith(".NS") || art.ticker?.endsWith(".BO");
        if (isIndia) return false;
      }

      // 4. Sector Filter
      if (filters.selectedSector !== "ALL") {
        if (art.sector && art.sector !== filters.selectedSector) return false;
      }

      // 5. Ticker Filter
      if (filters.selectedTicker !== "ALL") {
        const matchesTicker = art.ticker === filters.selectedTicker;
        const matchesRelated = art.related_tickers?.includes(filters.selectedTicker);
        if (!matchesTicker && !matchesRelated) return false;
      }

      return true;
    });
  }, [articles, filters]);

  return {
    filters,
    updateFilter,
    resetFilters,
    filteredArticles,
  };
}
