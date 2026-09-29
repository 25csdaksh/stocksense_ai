"use client";

import { useState, useEffect, useCallback } from "react";
import { newsApi } from "@/lib/api/news";
import { NewsArticle } from "@/types";

const FALLBACK_NEWS: NewsArticle[] = [
  {
    id: "news-1",
    title: "RBI Keeps Repo Rate Steady at 6.50%; Signals Resilient Growth Across Banking and Credit Sectors",
    summary:
      "Monetary Policy Committee retains stance on disinflation while highlighting robust domestic macroeconomic fundamentals and stable asset quality.",
    source: "Financial Times / Mint",
    url: "#",
    published_at: "18 mins ago",
    sentiment_score: 0.72,
    sentiment_label: "POSITIVE",
    related_tickers: ["HDFCBANK.NS", "SBIN.NS", "ICICIBANK.NS"],
  },
  {
    id: "news-2",
    title: "TCS Secures Multi-Million Enterprise Cloud Modernization Contract with European Retail Giant",
    summary:
      "Tata Consultancy Services expands AI-first cloud migration portfolio, supporting margin resilience heading into next fiscal quarter.",
    source: "Bloomberg Quint",
    url: "#",
    published_at: "42 mins ago",
    sentiment_score: 0.85,
    sentiment_label: "POSITIVE",
    related_tickers: ["TCS.NS", "INFY.NS"],
  },
  {
    id: "news-3",
    title: "Crude Oil Benchmark Volatility Weighs on Refiners and Downstream Petrochemical Margins",
    summary:
      "Brent crude fluctuations induce short-term refining spread compression, prompting caution among institutional energy desks.",
    source: "Reuters",
    url: "#",
    published_at: "1 hour ago",
    sentiment_score: -0.34,
    sentiment_label: "NEGATIVE",
    related_tickers: ["RELIANCE.NS", "ONGC.NS"],
  },
  {
    id: "news-4",
    title: "Automotive Sector Dispatches Surge 14% YoY Driven by Utility Vehicles and EV Momentum",
    summary:
      "Domestic automaker deliveries continue robust expansion with premium utility vehicles capturing record market share.",
    source: "Economic Times",
    url: "#",
    published_at: "2 hours ago",
    sentiment_score: 0.65,
    sentiment_label: "POSITIVE",
    related_tickers: ["TATAMOTORS.NS", "MARUTI.NS"],
  },
];

export function useNews(limit: number = 6) {
  const [news, setNews] = useState<NewsArticle[]>([]);
  const [isLoading, setIsLoading] = useState<boolean>(true);
  const [isError, setIsError] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);
  const [isDemo, setIsDemo] = useState<boolean>(false);

  const fetchNews = useCallback(async () => {
    setIsLoading(true);
    setIsError(false);
    setError(null);
    try {
      const data = await newsApi.getNews(limit);
      if (data && data.length > 0) {
        setNews(data);
        setIsDemo(false);
      } else {
        setNews(FALLBACK_NEWS);
        setIsDemo(true);
      }
    } catch {
      setNews(FALLBACK_NEWS);
      setIsDemo(true);
    } finally {
      setIsLoading(false);
    }
  }, [limit]);

  useEffect(() => {
    fetchNews();
  }, [fetchNews]);

  return {
    news,
    isLoading,
    isError,
    error,
    isDemo,
    refresh: fetchNews,
  };
}
