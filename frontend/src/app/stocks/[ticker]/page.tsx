"use client";

import React, { useState, useRef } from "react";
import { useParams, useRouter } from "next/navigation";
import Link from "next/link";
import { AppLayout } from "@/components/layout/AppLayout";
import { useStockQuote } from "@/hooks/useStockQuote";
import {
  StockHeader,
  StockPriceSummary,
  StockChartSection,
  TechnicalIntelligence,
  FundamentalIntelligence,
  StockDNASection,
  RiskIntelligence,
  AnomalyIntelligence,
  CorrelationIntelligence,
  AIResearchPanel,
  StockResearchActions,
  StockNewsSection,
  StockCompareModal,
} from "@/components/stocks";
import { Card, CardContent } from "@/components/common/Card";
import { Button } from "@/components/common/Button";
import { ArrowLeft, AlertCircle, Sparkles } from "lucide-react";

export default function StockDetailPage() {
  const params = useParams();
  const router = useRouter();

  // Safely decode and normalize ticker parameter
  const rawTicker = typeof params?.ticker === "string" ? params.ticker : "RELIANCE.NS";
  const ticker = decodeURIComponent(rawTicker).toUpperCase();

  const { quote, isInWatchlist, isLoading, isError, error, isDemo, toggleWatchlist } =
    useStockQuote(ticker);

  const [compareModalOpen, setCompareModalOpen] = useState(false);
  const [selectedAIPrompt, setSelectedAIPrompt] = useState<string>("");

  const aiPanelRef = useRef<HTMLDivElement>(null);

  const isIndian = ticker.endsWith(".NS") || ticker.endsWith(".BO") || ticker.startsWith("^");
  const currency = isIndian ? "INR" : "USD";

  // Dispatch prompt directly to AI research panel and smoothly scroll into view
  const handleTriggerAIResearch = (customPrompt?: string) => {
    const promptToUse =
      customPrompt || `Analyze ${ticker} using available market, technical, fundamental, and news data.`;
    setSelectedAIPrompt(promptToUse);
    if (aiPanelRef.current) {
      aiPanelRef.current.scrollIntoView({ behavior: "smooth", block: "start" });
    }
  };

  // If ticker is completely invalid or not found
  if (isError && !quote) {
    return (
      <AppLayout>
        <div className="max-w-4xl mx-auto py-12 px-4 text-center space-y-4">
          <div className="w-16 h-16 rounded-2xl bg-financial-loss-bg text-financial-loss flex items-center justify-center mx-auto">
            <AlertCircle className="w-8 h-8" />
          </div>
          <h1 className="text-2xl font-bold text-content">Stock Not Found</h1>
          <p className="text-sm text-content-muted max-w-md mx-auto">
            Unable to locate quote and analytics for ticker symbol &quot;{ticker}&quot;. Please verify the symbol or explore the stock universe.
          </p>
          <div className="pt-2">
            <Link href="/stocks">
              <Button variant="primary" size="md" leftIcon={<ArrowLeft className="w-4 h-4" />}>
                Return to Stock Universe
              </Button>
            </Link>
          </div>
        </div>
      </AppLayout>
    );
  }

  return (
    <AppLayout>
      <div className="space-y-6 pb-12">
        {/* Navigation Breadcrumb */}
        <div className="flex items-center gap-2 text-xs font-semibold text-content-muted">
          <Link href="/dashboard" className="hover:text-primary transition-colors">
            Dashboard
          </Link>
          <span>/</span>
          <Link href="/stocks" className="hover:text-primary transition-colors">
            Stock Universe
          </Link>
          <span>/</span>
          <span className="text-content font-bold">{ticker}</span>
        </div>

        {/* Section A: Stock Identity & Market Header */}
        <StockHeader
          ticker={ticker}
          name={(quote as any)?.name}
          exchange={isIndian ? "NSE" : "NASDAQ"}
          sector={isIndian ? "Indian Capital Markets" : "US Equities"}
          quote={quote}
          isInWatchlist={isInWatchlist}
          onToggleWatchlist={toggleWatchlist}
          onOpenAIResearch={handleTriggerAIResearch}
          onOpenCompare={() => setCompareModalOpen(true)}
          isDemo={isDemo}
        />

        {/* Section B: Price Intelligence Summary Card */}
        <StockPriceSummary
          quote={quote}
          currency={currency}
          isLoading={isLoading}
          isDemo={isDemo}
        />

        {/* Section K / Quick Actions: AI Research Dispatchers */}
        <StockResearchActions
          ticker={ticker}
          onSelectAction={handleTriggerAIResearch}
          onOpenCompare={() => setCompareModalOpen(true)}
        />

        {/* Section C: Interactive OHLCV Candlestick & Volume Chart */}
        <StockChartSection
          ticker={ticker}
          currency={currency}
          isDemo={isDemo}
        />

        {/* Section J: Ask MarketMind AI Research Panel */}
        <div ref={aiPanelRef}>
          <AIResearchPanel
            ticker={ticker}
            initialQuery={selectedAIPrompt}
            isDemo={isDemo}
          />
        </div>

        {/* Quantitative Grid: Technical & Fundamental Intelligence */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 items-start">
          {/* Section D: Technical Intelligence */}
          <TechnicalIntelligence
            ticker={ticker}
            currency={currency}
            isDemo={isDemo}
          />

          {/* Section E: Fundamental Intelligence */}
          <FundamentalIntelligence
            ticker={ticker}
            isDemo={isDemo}
          />
        </div>

        {/* Factor Profile & Risk Grid */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 items-start">
          {/* Section F: 5-Factor Stock DNA Profile */}
          <StockDNASection
            ticker={ticker}
            isDemo={isDemo}
          />

          {/* Section G: Risk & Volatility Intelligence */}
          <RiskIntelligence
            ticker={ticker}
            currency={currency}
            isDemo={isDemo}
          />
        </div>

        {/* Flow & Macro Grid: Anomalies & Cross-Asset Correlation */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 items-start">
          {/* Section H: Anomaly & Flow Intelligence */}
          <AnomalyIntelligence
            ticker={ticker}
            currency={currency}
            isDemo={isDemo}
          />

          {/* Section I: Cross-Asset Correlation Intelligence */}
          <CorrelationIntelligence
            ticker={ticker}
            isDemo={isDemo}
          />
        </div>

        {/* Section L: Key Verified News & Real-Time Sentiment */}
        <StockNewsSection
          ticker={ticker}
          isDemo={isDemo}
        />

        {/* Stock Comparison Modal / Dialog */}
        <StockCompareModal
          isOpen={compareModalOpen}
          onClose={() => setCompareModalOpen(false)}
          baseTicker={ticker}
          onCompareWithAI={handleTriggerAIResearch}
        />
      </div>
    </AppLayout>
  );
}
