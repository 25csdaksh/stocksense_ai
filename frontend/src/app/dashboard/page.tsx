"use client";

import React from "react";
import { AppLayout } from "@/components/layout/AppLayout";
import {
  MarketIndicesSection,
  MarketOverviewChartSection,
  AIMarketBriefSection,
  SectorIntelligenceSection,
  MarketAnomalyFeedSection,
  WatchlistSnapshotSection,
  PortfolioSnapshotSection,
  FinancialNewsSection,
  AIResearchQuickLaunch,
} from "@/components/dashboard";

export default function DashboardPage() {
  return (
    <AppLayout>
      <div className="space-y-6 pb-12">
        {/* 1. AI Research Quick Launch Bar */}
        <section aria-label="AI Research Query">
          <AIResearchQuickLaunch />
        </section>

        {/* 2. Top Benchmark Index Cards & Market Status */}
        <section aria-label="Market Benchmarks">
          <MarketIndicesSection />
        </section>

        {/* 3. Main Intelligence & Analytics Multi-Column Grid */}
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-6 items-start">
          {/* Main Analytics Column (8 Cols on LG) */}
          <div className="lg:col-span-8 space-y-6">
            {/* AI Market Synthesis */}
            <section aria-label="Market Intelligence Brief">
              <AIMarketBriefSection />
            </section>

            {/* Interactive Market Candlestick & Volume Chart */}
            <section aria-label="Market Overview Chart">
              <MarketOverviewChartSection />
            </section>

            {/* Anomaly & Volatility Stream Feed */}
            <section aria-label="Market Anomalies">
              <MarketAnomalyFeedSection />
            </section>

            {/* Sector Performance & Momentum */}
            <section aria-label="Sector Intelligence">
              <SectorIntelligenceSection />
            </section>
          </div>

          {/* Right Holdings & Tracking Column (4 Cols on LG) */}
          <div className="lg:col-span-4 space-y-6">
            {/* Portfolio Snapshot & Allocation Donut */}
            <section aria-label="Portfolio Snapshot">
              <PortfolioSnapshotSection />
            </section>

            {/* User Watchlist Live Ticker Table */}
            <section aria-label="Watchlist Snapshot">
              <WatchlistSnapshotSection />
            </section>

            {/* Corporate & Regulatory Financial News Feed */}
            <section aria-label="Financial News">
              <FinancialNewsSection />
            </section>
          </div>
        </div>
      </div>
    </AppLayout>
  );
}
