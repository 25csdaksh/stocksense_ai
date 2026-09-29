"use client";

import React, { useRef } from "react";
import { AppLayout } from "@/components/layout/AppLayout";
import { useNews } from "@/hooks/useNews";
import { useNewsFilters } from "@/hooks/useNewsFilters";
import { useNewsSentiment } from "@/hooks/useNewsSentiment";
import {
  NewsHeader,
  NewsFilters,
  NewsFeed,
  NewsImportantSection,
  NewsSentimentOverview,
  NewsSectorSentiment,
  TickerNewsIntelligence,
  NewsTimeline,
  AINewsAnalysis,
  NewsMarketContext,
  WatchlistNews,
} from "@/components/news";

export default function NewsPage() {
  const { news, isLoading, isDemo, refresh } = useNews(25);
  const { filters, updateFilter, resetFilters, filteredArticles } = useNewsFilters(news);
  const sentimentStats = useNewsSentiment(filteredArticles);
  const aiSectionRef = useRef<HTMLDivElement>(null);

  const availableSectors = Array.from(
    new Set(
      news
        .map((a) => a.sector || (a.ticker?.includes("TCS") ? "Information Technology" : a.ticker?.includes("BANK") ? "Banking & Financials" : a.ticker?.includes("RELIANCE") ? "Energy & Petrochemicals" : null))
        .filter(Boolean) as string[]
    )
  );

  const handleScrollToAI = () => {
    aiSectionRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  return (
    <AppLayout>
      <div className="space-y-6 max-w-7xl mx-auto pb-12">
        {/* 1. News Command Header */}
        <NewsHeader
          totalArticles={news.length}
          lastUpdated="Real-Time Feed"
          isLoading={isLoading}
          isDemo={isDemo}
          onRefresh={refresh}
          onOpenAI={handleScrollToAI}
        />

        {/* 2. Market-Moving Wire Highlights */}
        <NewsImportantSection articles={news} />

        {/* 3. Filter Bar */}
        <NewsFilters
          filters={filters}
          updateFilter={updateFilter}
          resetFilters={resetFilters}
          sectorsList={availableSectors}
          totalResults={filteredArticles.length}
        />

        {/* 4. Multi-Column Terminal Grid */}
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
          {/* Main News Feed (7 cols on desktop) */}
          <div className="lg:col-span-7 space-y-4">
            <NewsFeed
              articles={filteredArticles}
              isLoading={isLoading}
              onSelectTicker={(t) => updateFilter("selectedTicker", t)}
            />
          </div>

          {/* Intelligence Sidebars (5 cols on desktop) */}
          <div className="lg:col-span-5 space-y-6">
            <NewsSentimentOverview stats={sentimentStats} isLoading={isLoading} />
            <TickerNewsIntelligence
              selectedTicker={filters.selectedTicker}
              onSelectTicker={(t) => updateFilter("selectedTicker", t)}
            />
            <NewsSectorSentiment
              sectors={sentimentStats.sectorBreakdown}
              onSelectSector={(s) => updateFilter("selectedSector", s)}
            />
            <WatchlistNews articles={news} />
            <NewsMarketContext articles={news} />
            <NewsTimeline articles={filteredArticles} />
          </div>
        </div>

        {/* 5. AI News Intelligence Section */}
        <div ref={aiSectionRef}>
          <AINewsAnalysis
            articles={filteredArticles}
            selectedTicker={filters.selectedTicker !== "ALL" ? filters.selectedTicker : undefined}
          />
        </div>
      </div>
    </AppLayout>
  );
}
