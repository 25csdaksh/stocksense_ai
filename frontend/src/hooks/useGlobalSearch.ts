"use client";

import { useState, useEffect, useMemo, useCallback } from "react";
import {
  GlobalSearchResultItem,
  SearchCategory,
  StockSearchResult,
  NewsSearchResult,
  AnomalySearchResult,
  PortfolioSearchResult,
  ActionSearchResult,
} from "@/types";
import { POPULAR_INDIAN_STOCKS, POPULAR_US_DEMO_STOCKS, MAJOR_INDICES } from "@/lib/constants";
import { newsApi } from "@/lib/api/news";
import { analyticsApi } from "@/lib/api/analytics";
import { portfolioApi } from "@/lib/api/portfolio";

const RECENT_SEARCHES_KEY = "marketmind_recent_searches";

const COMMAND_ACTIONS: ActionSearchResult[] = [
  { type: "ACTION", label: "Open Market Intelligence Dashboard", description: "Market benchmarks, AI brief, and top movers", iconName: "LayoutDashboard", url: "/dashboard", category: "Navigation" },
  { type: "ACTION", label: "Open Stock Intelligence Workspace", description: "Single-equity deep analytics, financials, and valuation", iconName: "TrendingUp", url: "/stocks", category: "Navigation" },
  { type: "ACTION", label: "Open Deep AI Research Workspace", description: "Multi-agent research, SEC 10-K RAG, and financial citations", iconName: "Brain", url: "/research", category: "AI & Research" },
  { type: "ACTION", label: "Open Market Anomaly Surveillance", description: "Isolation Forest, Z-score, and GARCH volatility regime", iconName: "AlertTriangle", url: "/anomalies", category: "Quantitative" },
  { type: "ACTION", label: "Open Scenario & Stress Test Lab", description: "Merton Jump Diffusion, historical crisis replay, and VaR", iconName: "Activity", url: "/scenarios", category: "Quantitative" },
  { type: "ACTION", label: "Open Portfolio Intelligence", description: "Holdings, asset allocation, concentration, and VaR risk", iconName: "Briefcase", url: "/portfolio", category: "Portfolio" },
  { type: "ACTION", label: "Open Financial News Terminal", description: "NLP sentiment polarity, sector breakdowns, and wire feeds", iconName: "Newspaper", url: "/news", category: "Intelligence" },
  { type: "ACTION", label: "Open Watchlist Monitor", description: "Live price tracking and alert management", iconName: "Bookmark", url: "/watchlist", category: "Portfolio" },
  { type: "ACTION", label: "Open Platform Settings", description: "Configure API endpoints, credentials, and preferences", iconName: "Settings", url: "/settings", category: "Preferences" },
];

export function useGlobalSearch() {
  const [query, setQuery] = useState("");
  const [category, setCategory] = useState<SearchCategory>("ALL");
  const [activeIndex, setActiveIndex] = useState(0);
  const [recentSearches, setRecentSearches] = useState<string[]>([]);

  // Telemetry caches
  const [newsResults, setNewsResults] = useState<NewsSearchResult[]>([]);
  const [anomalyResults, setAnomalyResults] = useState<AnomalySearchResult[]>([]);
  const [portfolioResults, setPortfolioResults] = useState<PortfolioSearchResult[]>([]);

  // Load recent searches from localStorage
  useEffect(() => {
    try {
      const stored = localStorage.getItem(RECENT_SEARCHES_KEY);
      if (stored) {
        setRecentSearches(JSON.parse(stored));
      }
    } catch {
      // ignore
    }
  }, []);

  const addRecentSearch = useCallback((term: string) => {
    if (!term.trim()) return;
    setRecentSearches((prev) => {
      const updated = [term.trim(), ...prev.filter((item) => item.toLowerCase() !== term.trim().toLowerCase())].slice(0, 6);
      try {
        localStorage.setItem(RECENT_SEARCHES_KEY, JSON.stringify(updated));
      } catch {
        // ignore
      }
      return updated;
    });
  }, []);

  const removeRecentSearch = useCallback((term: string) => {
    setRecentSearches((prev) => {
      const updated = prev.filter((item) => item !== term);
      try {
        localStorage.setItem(RECENT_SEARCHES_KEY, JSON.stringify(updated));
      } catch {
        // ignore
      }
      return updated;
    });
  }, []);

  const clearRecentSearches = useCallback(() => {
    setRecentSearches([]);
    try {
      localStorage.removeItem(RECENT_SEARCHES_KEY);
    } catch {
      // ignore
    }
  }, []);

  // Preload news and anomalies for lightning fast instant search
  useEffect(() => {
    let isMounted = true;
    async function preloadSearchData() {
      try {
        const [newsData, anomalyStream, portSummary] = await Promise.allSettled([
          newsApi.getNews(15),
          analyticsApi.getMarketAnomalyStream(),
          portfolioApi.getPortfolioSummary(),
        ]);

        if (isMounted && newsData.status === "fulfilled" && newsData.value) {
          setNewsResults(
            newsData.value.map((a) => ({
              type: "NEWS",
              id: a.id,
              title: a.title,
              source: a.source,
              time: a.published_at,
              sentiment: a.sentiment_label,
              ticker: a.ticker || (a.related_tickers && a.related_tickers[0]),
              url: a.ticker ? `/stocks/${encodeURIComponent(a.ticker)}` : `/news`,
            }))
          );
        }

        if (isMounted && anomalyStream.status === "fulfilled" && anomalyStream.value?.anomalies) {
          setAnomalyResults(
            anomalyStream.value.anomalies.map((an: { id?: string; ticker: string; anomaly_type: string; severity?: "LOW" | "MEDIUM" | "HIGH" | "CRITICAL"; timestamp: string }) => ({
              type: "ANOMALY",
              id: an.id || `${an.ticker}-${an.timestamp}`,
              ticker: an.ticker,
              anomaly_type: an.anomaly_type,
              severity: an.severity || "MEDIUM",
              time: an.timestamp,
              url: `/anomalies?ticker=${encodeURIComponent(an.ticker)}`,
            }))
          );
        }

        if (isMounted && portSummary.status === "fulfilled" && portSummary.value?.positions) {
          setPortfolioResults(
            portSummary.value.positions.map((p) => ({
              type: "PORTFOLIO",
              ticker: p.ticker,
              shares: p.shares,
              value: p.market_value,
              pnl_pct: p.unrealized_pnl_pct,
              url: `/stocks/${encodeURIComponent(p.ticker)}`,
            }))
          );
        }
      } catch {
        // ignore
      }
    }

    preloadSearchData();
    return () => {
      isMounted = false;
    };
  }, []);

  // Stocks & Indices universe
  const stockItems: StockSearchResult[] = useMemo(() => {
    return [
      ...MAJOR_INDICES.map((i) => ({
        type: "STOCK" as const,
        ticker: i.ticker,
        name: i.name,
        exchange: i.exchange,
        sector: "Benchmark Index",
        url: `/stocks/${encodeURIComponent(i.ticker)}`,
        is_demo: i.is_demo,
      })),
      ...POPULAR_INDIAN_STOCKS.map((s) => ({
        type: "STOCK" as const,
        ticker: s.ticker,
        name: s.name,
        exchange: s.exchange,
        sector: s.ticker.includes("TCS") || s.ticker.includes("INFY") ? "IT" : s.ticker.includes("BANK") ? "Banking" : s.ticker.includes("RELIANCE") ? "Energy" : "Equities",
        url: `/stocks/${encodeURIComponent(s.ticker)}`,
        is_demo: false,
      })),
      ...POPULAR_US_DEMO_STOCKS.map((s) => ({
        type: "STOCK" as const,
        ticker: s.ticker,
        name: s.name,
        exchange: s.exchange,
        sector: "Mega-Cap Tech",
        url: `/stocks/${encodeURIComponent(s.ticker)}`,
        is_demo: true,
      })),
    ];
  }, []);

  // Filtered and Ranked Search Results
  const results: GlobalSearchResultItem[] = useMemo(() => {
    const q = query.trim().toLowerCase();

    if (!q) {
      if (category === "STOCKS") return stockItems;
      if (category === "NEWS") return newsResults;
      if (category === "ANOMALIES") return anomalyResults;
      if (category === "PORTFOLIO") return portfolioResults;
      if (category === "ACTIONS") return COMMAND_ACTIONS;
      return [...COMMAND_ACTIONS.slice(0, 4), ...stockItems.slice(0, 6)];
    }

    const matchedStocks = stockItems.filter(
      (s) =>
        s.ticker.toLowerCase().includes(q) ||
        s.name.toLowerCase().includes(q) ||
        s.exchange.toLowerCase().includes(q) ||
        (s.sector && s.sector.toLowerCase().includes(q))
    );

    const matchedNews = newsResults.filter(
      (n) =>
        n.title.toLowerCase().includes(q) ||
        n.source.toLowerCase().includes(q) ||
        (n.ticker && n.ticker.toLowerCase().includes(q))
    );

    const matchedAnomalies = anomalyResults.filter(
      (a) =>
        a.ticker.toLowerCase().includes(q) ||
        a.anomaly_type.toLowerCase().includes(q) ||
        a.severity.toLowerCase().includes(q)
    );

    const matchedPortfolio = portfolioResults.filter((p) => p.ticker.toLowerCase().includes(q));

    const matchedActions = COMMAND_ACTIONS.filter(
      (act) =>
        act.label.toLowerCase().includes(q) ||
        act.description.toLowerCase().includes(q) ||
        act.category.toLowerCase().includes(q)
    );

    if (category === "STOCKS") return matchedStocks;
    if (category === "NEWS") return matchedNews;
    if (category === "ANOMALIES") return matchedAnomalies;
    if (category === "PORTFOLIO") return matchedPortfolio;
    if (category === "ACTIONS") return matchedActions;

    // "ALL" Category - blended priority ranking
    return [
      ...matchedStocks.slice(0, 5),
      ...matchedActions.slice(0, 3),
      ...matchedNews.slice(0, 4),
      ...matchedAnomalies.slice(0, 3),
      ...matchedPortfolio.slice(0, 3),
    ];
  }, [query, category, stockItems, newsResults, anomalyResults, portfolioResults]);

  // Reset activeIndex when query or category changes
  useEffect(() => {
    setActiveIndex(0);
  }, [query, category]);

  return {
    query,
    setQuery,
    category,
    setCategory,
    results,
    activeIndex,
    setActiveIndex,
    recentSearches,
    addRecentSearch,
    removeRecentSearch,
    clearRecentSearches,
  };
}
