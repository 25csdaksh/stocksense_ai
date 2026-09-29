"use client";

import React from "react";
import { useRouter } from "next/navigation";
import { Modal } from "@/components/common/Modal";
import { Button } from "@/components/common/Button";
import { Badge } from "@/components/common/Badge";
import { formatCurrency, formatPercent } from "@/lib/utils";
import { PortfolioHolding } from "@/types";
import {
  ExternalLink,
  Bookmark,
  BookmarkCheck,
  TrendingUp,
  TrendingDown,
  Layers,
  Shield,
} from "lucide-react";

export interface PositionDetailPanelProps {
  holding: PortfolioHolding | null;
  isOpen: boolean;
  onClose: () => void;
  isInWatchlist: boolean;
  onToggleWatchlist: (ticker: string) => void;
}

export const PositionDetailPanel: React.FC<PositionDetailPanelProps> = ({
  holding,
  isOpen,
  onClose,
  isInWatchlist,
  onToggleWatchlist,
}) => {
  const router = useRouter();

  if (!holding) return null;

  const isProfit = (holding.unrealized_pnl ?? 0) >= 0;
  const totalCost = holding.avg_price * holding.shares;

  const handleNavigateStock = () => {
    onClose();
    router.push(`/stocks/${encodeURIComponent(holding.ticker)}`);
  };

  return (
    <Modal
      isOpen={isOpen}
      onClose={onClose}
      title={`Position Intelligence: ${holding.ticker}`}
      description={holding.company_name || holding.ticker}
      maxWidth="lg"
    >
      <div className="space-y-6 pt-2">
        {/* Header Badge Strip */}
        <div className="flex items-center justify-between p-3 bg-surface-subtle/80 rounded-xl border border-border">
          <div className="flex items-center gap-2.5">
            <div className="w-8 h-8 rounded-lg bg-primary-light flex items-center justify-center text-primary font-bold text-sm">
              {holding.ticker.slice(0, 2)}
            </div>
            <div>
              <span className="font-bold text-content text-sm">{holding.ticker}</span>
              <p className="text-[11px] text-content-muted">{holding.sector || "Equities"}</p>
            </div>
          </div>
          <Badge variant="primary" size="sm">
            {holding.sector || "Information Technology"}
          </Badge>
        </div>

        {/* Key Valuation Highlight Banner */}
        <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 p-4 bg-surface-subtle rounded-xl border border-border">
          <div>
            <span className="text-[11px] text-content-muted block font-medium">Market Value</span>
            <span className="text-lg font-bold text-content font-tabular">
              {formatCurrency(holding.market_value, "INR")}
            </span>
          </div>

          <div>
            <span className="text-[11px] text-content-muted block font-medium">Total Cost Basis</span>
            <span className="text-lg font-bold text-content font-tabular">
              {formatCurrency(totalCost, "INR")}
            </span>
          </div>

          <div>
            <span className="text-[11px] text-content-muted block font-medium">Unrealized P&L</span>
            <span
              className={`text-lg font-bold font-tabular flex items-center gap-1 ${
                isProfit ? "text-financial-gain" : "text-financial-loss"
              }`}
            >
              {isProfit ? <TrendingUp className="w-4 h-4" /> : <TrendingDown className="w-4 h-4" />}
              {isProfit ? "+" : ""}
              {formatCurrency(holding.unrealized_pnl, "INR")}
            </span>
          </div>

          <div>
            <span className="text-[11px] text-content-muted block font-medium">Return %</span>
            <span
              className={`text-lg font-bold font-tabular ${
                isProfit ? "text-financial-gain" : "text-financial-loss"
              }`}
            >
              {formatPercent(holding.unrealized_pnl_pct)}
            </span>
          </div>
        </div>

        {/* Detailed Position Metrics Grid */}
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
          <div className="space-y-3 p-3.5 border border-border rounded-xl bg-surface">
            <h4 className="text-xs font-bold text-content-muted uppercase tracking-wider flex items-center gap-1.5">
              <Layers className="w-3.5 h-3.5 text-primary" />
              Holding Mechanics
            </h4>
            <div className="space-y-2 text-xs">
              <div className="flex justify-between py-1 border-b border-border/50">
                <span className="text-content-muted">Quantity (Shares)</span>
                <span className="font-bold text-content font-tabular">{holding.shares} Units</span>
              </div>
              <div className="flex justify-between py-1 border-b border-border/50">
                <span className="text-content-muted">Average Purchase Price</span>
                <span className="font-bold text-content font-tabular">
                  {formatCurrency(holding.avg_price, "INR")}
                </span>
              </div>
              <div className="flex justify-between py-1 border-b border-border/50">
                <span className="text-content-muted">Current Spot Price</span>
                <span className="font-bold text-content font-tabular">
                  {formatCurrency(holding.current_price, "INR")}
                </span>
              </div>
              <div className="flex justify-between py-1">
                <span className="text-content-muted">Portfolio Allocation Weight</span>
                <span className="font-bold text-primary font-tabular">
                  {formatPercent(holding.weight_pct)}
                </span>
              </div>
            </div>
          </div>

          <div className="space-y-3 p-3.5 border border-border rounded-xl bg-surface">
            <h4 className="text-xs font-bold text-content-muted uppercase tracking-wider flex items-center gap-1.5">
              <Shield className="w-3.5 h-3.5 text-secondary" />
              Risk &amp; Factor Analytics
            </h4>
            <div className="space-y-2 text-xs">
              <div className="flex justify-between py-1 border-b border-border/50">
                <span className="text-content-muted">Beta to NIFTY 50 (β)</span>
                <span className="font-bold text-content font-tabular">
                  {(holding.beta ?? 1.0).toFixed(2)}
                </span>
              </div>
              <div className="flex justify-between py-1 border-b border-border/50">
                <span className="text-content-muted">Sector Classification</span>
                <span className="font-bold text-content">{holding.sector || "Information Technology"}</span>
              </div>
              <div className="flex justify-between py-1 border-b border-border/50">
                <span className="text-content-muted">1-Day Session Change</span>
                <span className="font-bold text-financial-gain font-tabular">
                  {formatPercent(holding.daily_change_pct || 0.8)}
                </span>
              </div>
              <div className="flex justify-between py-1">
                <span className="text-content-muted">Exchange / Market</span>
                <span className="font-bold text-content">NSE (National Stock Exchange)</span>
              </div>
            </div>
          </div>
        </div>

        {/* Modal Action Bar */}
        <div className="flex flex-col sm:flex-row items-center justify-between gap-3 pt-3 border-t border-border">
          <Button
            variant="outline"
            size="sm"
            onClick={() => onToggleWatchlist(holding.ticker)}
            leftIcon={
              isInWatchlist ? (
                <BookmarkCheck className="w-4 h-4 text-primary" />
              ) : (
                <Bookmark className="w-4 h-4 text-content-muted" />
              )
            }
          >
            {isInWatchlist ? "In Watchlist" : "Add to Watchlist"}
          </Button>

          <div className="flex items-center gap-2 w-full sm:w-auto justify-end">
            <Button variant="ghost" size="sm" onClick={onClose}>
              Close
            </Button>
            <Button
              variant="primary"
              size="sm"
              onClick={handleNavigateStock}
              rightIcon={<ExternalLink className="w-3.5 h-3.5" />}
            >
              View Stock Intelligence
            </Button>
          </div>
        </div>
      </div>
    </Modal>
  );
};
