"use client";

import React, { useState } from "react";
import { AppLayout } from "@/components/layout/AppLayout";
import {
  AnomalyHeader,
  AnomalyFilters,
  SystemicStressOverview,
  AnomalyFeed,
  AnomalySeverityDistribution,
  AnomalyTimeline,
  AnomalySignalBreakdown,
  VolumeSurveillance,
  VolatilitySurveillance,
  CrossAssetAnomalyMap,
  AnomalyInspector,
  AIAnomalyExplanation,
  AnomalyNewsContext,
} from "@/components/anomalies";
import { ErrorState } from "@/components/common/ErrorState";
import { useAnomalyFeed, EnrichedAnomalyItem } from "@/hooks/useAnomalyFeed";
import { useAnomalyDetail } from "@/hooks/useAnomalyDetail";

export default function AnomaliesPage() {
  const {
    anomalies,
    allAnomalies,
    totalActiveCount,
    criticalCount,
    highCount,
    systemicStressIndex,
    severityDistribution,
    isLoading,
    isError,
    error,
    isDemo,
    lastUpdated,
    severityFilter,
    setSeverityFilter,
    typeFilter,
    setTypeFilter,
    searchQuery,
    setSearchQuery,
    timeWindow,
    setTimeWindow,
    refresh,
  } = useAnomalyFeed();

  const [selectedAnomaly, setSelectedAnomaly] = useState<EnrichedAnomalyItem | null>(
    anomalies[0] || null
  );
  const [isInspectorOpen, setIsInspectorOpen] = useState<boolean>(false);

  // Deep telemetry for selected asset
  const { tickerData, news, isLoading: isDetailLoading } = useAnomalyDetail(
    selectedAnomaly?.ticker || "RELIANCE.NS"
  );

  const handleSelectAnomaly = (item: EnrichedAnomalyItem) => {
    setSelectedAnomaly(item);
    setIsInspectorOpen(true);
  };

  const handleResetFilters = () => {
    setSeverityFilter("ALL");
    setTypeFilter("ALL");
    setSearchQuery("");
    setTimeWindow("1D");
  };

  const handleScrollToAI = () => {
    const el = document.getElementById("ai-anomaly-investigator");
    if (el) {
      el.scrollIntoView({ behavior: "smooth" });
    }
  };

  if (isError && allAnomalies.length === 0) {
    return (
      <AppLayout>
        <div className="py-12">
          <ErrorState
            title="Unable to Load Anomaly Surveillance Feeds"
            message={error || "An unexpected error occurred while communicating with the anomaly service."}
            onRetry={refresh}
          />
        </div>
      </AppLayout>
    );
  }

  const activeHoldingAnomaly = selectedAnomaly || anomalies[0] || null;

  return (
    <AppLayout>
      <div className="space-y-6 pb-12">
        {/* A. Anomaly Command Header */}
        <AnomalyHeader
          totalActiveCount={totalActiveCount}
          criticalCount={criticalCount}
          systemicStressIndex={systemicStressIndex}
          lastUpdated={lastUpdated}
          isMarketOpen={true}
          isDemo={isDemo}
          isLoading={isLoading}
          onRefresh={refresh}
          onAIInvestigate={handleScrollToAI}
        />

        {/* B. Systemic Stress Overview */}
        <SystemicStressOverview
          systemicStressIndex={systemicStressIndex}
          totalActiveCount={totalActiveCount}
          highCount={highCount}
          criticalCount={criticalCount}
          marketVolatility={14.8}
        />

        {/* C. Filter Bar */}
        <AnomalyFilters
          severityFilter={severityFilter}
          onSelectSeverity={setSeverityFilter}
          typeFilter={typeFilter}
          onSelectType={setTypeFilter}
          searchQuery={searchQuery}
          onSearchChange={setSearchQuery}
          timeWindow={timeWindow}
          onSelectTimeWindow={setTimeWindow}
          onReset={handleResetFilters}
        />

        {/* D. Feed & Severity Distribution */}
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-6 items-start">
          <div className="lg:col-span-8">
            <AnomalyFeed
              anomalies={anomalies}
              selectedAnomalyId={activeHoldingAnomaly?.id}
              onSelectAnomaly={handleSelectAnomaly}
              isLoading={isLoading}
            />
          </div>

          <div className="lg:col-span-4 space-y-6">
            <AnomalySeverityDistribution
              distribution={severityDistribution}
              activeSeverity={severityFilter}
              onSelectSeverity={setSeverityFilter}
            />
            <AnomalyTimeline
              anomalies={allAnomalies}
              selectedAnomalyId={activeHoldingAnomaly?.id}
              onSelectAnomaly={handleSelectAnomaly}
            />
          </div>
        </div>

        {/* E & F. Statistical Signal Breakdown & Volume / Volatility Surveillance */}
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-6 items-start">
          <div className="lg:col-span-6">
            <AnomalySignalBreakdown anomaly={activeHoldingAnomaly} />
          </div>

          <div className="lg:col-span-6 space-y-6">
            <VolumeSurveillance
              ticker={activeHoldingAnomaly?.ticker || "RELIANCE.NS"}
              volumeZScore={activeHoldingAnomaly?.metrics?.volume_z_score || activeHoldingAnomaly?.z_score}
            />
            <VolatilitySurveillance
              ticker={activeHoldingAnomaly?.ticker || "RELIANCE.NS"}
              garchVol={activeHoldingAnomaly?.metrics?.garch_volatility_pct || 38.4}
            />
          </div>
        </div>

        {/* G. Cross-Asset Decoupling Map */}
        <CrossAssetAnomalyMap anomaliesCount={anomalies.length} />

        {/* H. News Context */}
        <AnomalyNewsContext
          ticker={activeHoldingAnomaly?.ticker || "RELIANCE.NS"}
          news={news}
          isLoading={isDetailLoading}
        />

        {/* I. Ask MarketMind to Explain This Anomaly (AI Assistant) */}
        <AIAnomalyExplanation
          selectedTicker={activeHoldingAnomaly?.ticker}
          anomaly={activeHoldingAnomaly}
        />

        {/* Selected Anomaly Inspector Modal */}
        <AnomalyInspector
          anomaly={selectedAnomaly}
          isOpen={isInspectorOpen}
          onClose={() => setIsInspectorOpen(false)}
          onTriggerAI={(t) => handleScrollToAI()}
        />
      </div>
    </AppLayout>
  );
}
