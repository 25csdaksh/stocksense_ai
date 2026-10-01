"use client";

import React, { useState, useMemo } from "react";
import { useRouter } from "next/navigation";
import { AppLayout } from "@/components/layout/AppLayout";
import {
  PortfolioHeader,
  PortfolioSummary,
  PortfolioPerformance,
  PortfolioAllocation,
  PortfolioHoldings,
  PositionDetailPanel,
  PortfolioRisk,
  ConcentrationAnalysis,
  PortfolioCorrelation,
  PortfolioDiversification,
  TransactionHistory,
  TransactionForm,
  AIPortfolioResearch,
  PortfolioStressTestCTA,
  PortfolioCopilotPanel,
} from "@/components/portfolio";
import { Card, CardHeader, CardTitle, CardContent } from "@/components/common/Card";
import { Skeleton } from "@/components/common/Skeleton";
import { ErrorState } from "@/components/common/ErrorState";
import { EmptyState } from "@/components/common/EmptyState";
import { Button } from "@/components/common/Button";
import { usePortfolio } from "@/hooks/usePortfolio";
import { useWatchlist } from "@/hooks/useWatchlist";
import { PortfolioHolding } from "@/types";
import { Briefcase, Plus, RefreshCw, Layers, ShieldCheck, PieChart, Sparkles } from "lucide-react";

export default function PortfolioPage() {
  const router = useRouter();

  // 1. Portfolio Hook
  const {
    portfolio,
    holdings,
    transactions,
    stockAllocation,
    sectorAllocation,
    assetClassAllocation,
    concentrationMetrics,
    riskMetrics,
    isLoading,
    isError,
    error,
    isDemo,
    lastUpdated,
    addTransaction,
    refresh,
  } = usePortfolio();

  // 2. Watchlist Hook
  const {
    watchlist,
    addToWatchlist,
    removeFromWatchlist,
  } = useWatchlist();

  // 3. Modals & Inspector States
  const [selectedHolding, setSelectedHolding] = useState<PortfolioHolding | null>(null);
  const [isDetailOpen, setIsDetailOpen] = useState<boolean>(false);
  const [isTxFormOpen, setIsTxFormOpen] = useState<boolean>(false);

  // Watchlist set for O(1) lookup
  const watchlistTickerSet = useMemo(() => {
    return new Set((watchlist || []).map((item) => item.ticker));
  }, [watchlist]);

  const handleToggleWatchlist = async (ticker: string) => {
    if (watchlistTickerSet.has(ticker)) {
      await removeFromWatchlist(ticker);
    } else {
      await addToWatchlist(ticker);
    }
  };

  const handleSelectHolding = (holding: PortfolioHolding) => {
    setSelectedHolding(holding);
    setIsDetailOpen(true);
  };

  const handleScrollToAI = () => {
    const el = document.getElementById("ai-portfolio-research");
    if (el) {
      el.scrollIntoView({ behavior: "smooth" });
    }
  };

  const handleOpenStressTest = () => {
    router.push("/scenarios?portfolioId=main");
  };

  const tickersList = useMemo(() => {
    return holdings.map((h) => h.ticker);
  }, [holdings]);

  const stressHoldings = useMemo(() => {
    return holdings.map((h) => ({
      ticker: h.ticker,
      shares: h.shares,
      price: h.current_price,
      sector: h.sector,
      beta: h.beta,
    }));
  }, [holdings]);

  // If initial load failed with no data
  if (isError && holdings.length === 0) {
    return (
      <AppLayout>
        <div className="py-12">
          <ErrorState
            title="Unable to Load Portfolio Intelligence"
            message={error || "An unexpected error occurred while communicating with the portfolio service."}
            onRetry={refresh}
          />
        </div>
      </AppLayout>
    );
  }

  // If empty portfolio
  const isEmptyPortfolio = !isLoading && holdings.length === 0;

  return (
    <AppLayout>
      <div className="space-y-6 pb-12">
        {/* A. Portfolio Header */}
        <PortfolioHeader
          portfolioName="Main Institutional Portfolio"
          portfolioId="PORT-IN-001"
          lastUpdated={lastUpdated}
          isMarketOpen={true}
          isDemo={isDemo}
          isLoading={isLoading}
          onRefresh={refresh}
          onAddTransaction={() => setIsTxFormOpen(true)}
          onAIAnalyze={handleScrollToAI}
          onStressTest={handleOpenStressTest}
        />

        {isEmptyPortfolio ? (
          <div className="py-16">
            <Card className="max-w-xl mx-auto text-center p-8 space-y-4">
              <div className="w-16 h-16 rounded-2xl bg-primary-light flex items-center justify-center text-primary mx-auto">
                <Briefcase className="w-8 h-8" />
              </div>
              <div className="space-y-1">
                <h3 className="text-xl font-bold text-content font-heading">Your Portfolio is Ready</h3>
                <p className="text-xs text-content-muted max-w-md mx-auto">
                  Add your first position to begin generating institutional analytics, quantitative risk metrics, intra-portfolio correlations, and AI insights.
                </p>
              </div>
              <div className="flex justify-center pt-2">
                <Button
                  variant="gold"
                  size="md"
                  onClick={() => setIsTxFormOpen(true)}
                  leftIcon={<Plus className="w-4 h-4" />}
                >
                  Add First Position
                </Button>
              </div>
            </Card>
          </div>
        ) : (
          <>
            {/* B. Portfolio Value Summary Cards */}
            <PortfolioSummary portfolio={portfolio} isLoading={isLoading} />

            {/* C & D. Performance Overview & Asset Allocation */}
            <div className="grid grid-cols-1 lg:grid-cols-12 gap-6 items-start">
              <div className="lg:col-span-7">
                <PortfolioPerformance
                  currentTotalValue={portfolio.total_value}
                  totalCost={portfolio.total_cost}
                />
              </div>

              <div className="lg:col-span-5">
                <PortfolioAllocation
                  stockAllocation={stockAllocation}
                  sectorAllocation={sectorAllocation}
                  assetClassAllocation={assetClassAllocation}
                  totalValue={portfolio.total_value}
                />
              </div>
            </div>

            {/* E. Holdings Intelligence Table */}
            <PortfolioHoldings
              holdings={holdings}
              watchlistTickers={watchlistTickerSet}
              onToggleWatchlist={handleToggleWatchlist}
              onSelectHolding={handleSelectHolding}
              isLoading={isLoading}
            />

            {/* F. Risk Intelligence Section */}
            <PortfolioRisk
              metrics={riskMetrics}
              totalValue={portfolio.total_value}
            />

            {/* G & H. Concentration & Intra-Portfolio Correlation */}
            <div className="grid grid-cols-1 lg:grid-cols-12 gap-6 items-start">
              <div className="lg:col-span-5">
                <ConcentrationAnalysis concentration={concentrationMetrics} />
              </div>

              <div className="lg:col-span-7">
                <PortfolioCorrelation tickers={tickersList} />
              </div>
            </div>

            {/* I. Portfolio Diversification Structure */}
            <PortfolioDiversification
              holdingsCount={holdings.length}
              sectorCount={sectorAllocation.length}
              concentration={concentrationMetrics}
              averageCorrelation={0.45}
            />

            {/* J. Historical Crisis Stress Testing Entry */}
            <PortfolioStressTestCTA
              portfolioId="PORT-IN-001"
              holdings={stressHoldings}
            />

            {/* K. Transaction History Ledger */}
            <TransactionHistory
              transactions={transactions}
              onAddTransaction={() => setIsTxFormOpen(true)}
            />

            {/* L. AI Portfolio Copilot & Personal Research Memory Workstation */}
            <div id="ai-portfolio-research" className="pt-4">
              <PortfolioCopilotPanel />
            </div>
          </>
        )}

        {/* Position Detail Modal */}
        <PositionDetailPanel
          holding={selectedHolding}
          isOpen={isDetailOpen}
          onClose={() => setIsDetailOpen(false)}
          isInWatchlist={selectedHolding ? watchlistTickerSet.has(selectedHolding.ticker) : false}
          onToggleWatchlist={handleToggleWatchlist}
        />

        {/* Add Transaction Modal */}
        <TransactionForm
          isOpen={isTxFormOpen}
          onClose={() => setIsTxFormOpen(false)}
          onSubmit={addTransaction}
        />
      </div>
    </AppLayout>
  );
}
