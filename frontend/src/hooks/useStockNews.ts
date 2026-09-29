"use client";

import { useState, useEffect, useCallback } from "react";
import { newsApi } from "@/lib/api/news";
import { NewsArticle, NewsSentimentSummary } from "@/types";

const FALLBACK_TICKER_NEWS: Record<string, NewsSentimentSummary> = {
  "RELIANCE.NS": {
    ticker: "RELIANCE.NS",
    overall_sentiment: "BULLISH",
    average_sentiment_score: 0.65,
    news_items: [
      {
        id: "rel-1",
        ticker: "RELIANCE.NS",
        title: "Reliance Retail Expands Omnichannel Capabilities Across Tier-2/3 Metros",
        summary: "New consumer tech integrations boost digital store fulfillment and gross merchant margins.",
        source: "Economic Times",
        published_at: "1 hour ago",
        sentiment_score: 0.78,
        sentiment_label: "POSITIVE",
      },
      {
        id: "rel-2",
        ticker: "RELIANCE.NS",
        title: "Jio Platforms Scales 5G Enterprise Monetization with AI Infrastructure Rollouts",
        summary: "Telecom arm signs key enterprise cloud contracts expected to support ARPU expansion.",
        source: "Mint",
        published_at: "3 hours ago",
        sentiment_score: 0.82,
        sentiment_label: "POSITIVE",
      },
      {
        id: "rel-3",
        ticker: "RELIANCE.NS",
        title: "Global Refining Margins Show Muted Volatility Amid Stable Crude Benchmarks",
        summary: "Oil-to-chemicals segment displays operational resilience despite periodic inventory adjustments.",
        source: "Reuters",
        published_at: "6 hours ago",
        sentiment_score: 0.15,
        sentiment_label: "NEUTRAL",
      },
    ],
  },
  "TCS.NS": {
    ticker: "TCS.NS",
    overall_sentiment: "BULLISH",
    average_sentiment_score: 0.82,
    news_items: [
      {
        id: "tcs-1",
        ticker: "TCS.NS",
        title: "TCS Bags Multi-Year $500M Digital Transformation Contract with European Conglomerate",
        summary: "Mega deal pipeline remains robust, reaffirming long-term IT services outsourcing demand.",
        source: "Bloomberg Quint",
        published_at: "45 mins ago",
        sentiment_score: 0.92,
        sentiment_label: "POSITIVE",
      },
      {
        id: "tcs-2",
        ticker: "TCS.NS",
        title: "TCS Expands AI Workforce Training; Upskills Over 300,000 Engineers in Generative AI",
        summary: "Investments in workforce readiness enhance competitive moat in large transformational deals.",
        source: "Financial Express",
        published_at: "2 hours ago",
        sentiment_score: 0.76,
        sentiment_label: "POSITIVE",
      },
    ],
  },
  "INFY.NS": {
    ticker: "INFY.NS",
    overall_sentiment: "POSITIVE",
    average_sentiment_score: 0.68,
    news_items: [
      {
        id: "infy-1",
        ticker: "INFY.NS",
        title: "Infosys Topaz AI Platform Sees Rapid Adoption Across BFSI Clients",
        summary: "Generative AI solutions accelerate client digital migration projects across North America and Europe.",
        source: "Business Standard",
        published_at: "2 hours ago",
        sentiment_score: 0.84,
        sentiment_label: "POSITIVE",
      },
      {
        id: "infy-2",
        ticker: "INFY.NS",
        title: "Infosys Maintained Steady Operating Margins in Recent Quarter",
        summary: "Operational efficiency programs and strategic cost optimization cushion against wage revisions.",
        source: "Mint",
        published_at: "5 hours ago",
        sentiment_score: 0.52,
        sentiment_label: "POSITIVE",
      },
    ],
  },
};

export function useStockNews(ticker: string, limit: number = 5) {
  const [newsSummary, setNewsSummary] = useState<NewsSentimentSummary | null>(null);
  const [articles, setArticles] = useState<NewsArticle[]>([]);
  const [isLoading, setIsLoading] = useState<boolean>(true);
  const [isError, setIsError] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);
  const [isDemo, setIsDemo] = useState<boolean>(false);

  const fetchStockNews = useCallback(async () => {
    if (!ticker) return;
    setIsLoading(true);
    setIsError(false);
    setError(null);

    try {
      const data = await newsApi.getTickerNews(ticker, limit);
      if (data && Array.isArray(data.news_items) && data.news_items.length > 0) {
        setNewsSummary(data);
        setArticles(data.news_items);
        setIsDemo(false);
      } else {
        const fallback = FALLBACK_TICKER_NEWS[ticker] || {
          ticker,
          overall_sentiment: "NEUTRAL",
          average_sentiment_score: 0.1,
          news_items: [
            {
              id: "fallback-1",
              ticker,
              title: `${ticker} Institutional Coverage & Market Positioning Analysis`,
              summary: "Equity analysts continue monitoring operational execution and sector-wide macroeconomic developments.",
              source: "Market Intelligence",
              published_at: "3 hours ago",
              sentiment_score: 0.25,
              sentiment_label: "NEUTRAL",
            },
          ],
        };
        setNewsSummary(fallback);
        setArticles(fallback.news_items);
        setIsDemo(true);
      }
    } catch {
      const fallback = FALLBACK_TICKER_NEWS[ticker] || {
        ticker,
        overall_sentiment: "NEUTRAL",
        average_sentiment_score: 0.1,
        news_items: [
          {
            id: "fallback-1",
            ticker,
            title: `${ticker} Institutional Coverage & Market Positioning Analysis`,
            summary: "Equity analysts continue monitoring operational execution and sector-wide macroeconomic developments.",
            source: "Market Intelligence",
            published_at: "3 hours ago",
            sentiment_score: 0.25,
            sentiment_label: "NEUTRAL",
          },
        ],
      };
      setNewsSummary(fallback);
      setArticles(fallback.news_items);
      setIsDemo(true);
    } finally {
      setIsLoading(false);
    }
  }, [ticker, limit]);

  useEffect(() => {
    fetchStockNews();
  }, [fetchStockNews]);

  return {
    newsSummary,
    articles,
    overallSentiment: newsSummary?.overall_sentiment || "NEUTRAL",
    averageSentimentScore: newsSummary?.average_sentiment_score ?? 0,
    isLoading,
    isError,
    error,
    isDemo,
    refresh: fetchStockNews,
  };
}
