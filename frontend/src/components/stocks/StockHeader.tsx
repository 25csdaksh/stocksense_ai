"use client";

import React, { useState } from "react";
import { StockQuote } from "@/types";
import { Badge } from "@/components/common/Badge";
import { Button } from "@/components/common/Button";
import {
  Bookmark,
  BookmarkCheck,
  Sparkles,
  ArrowRightLeft,
  Share2,
  Clock,
  Building2,
  Check,
} from "lucide-react";
import { formatCurrency, cn } from "@/lib/utils";

export interface StockHeaderProps {
  ticker: string;
  name?: string;
  exchange?: string;
  sector?: string;
  industry?: string;
  quote: StockQuote | null;
  isInWatchlist: boolean;
  onToggleWatchlist: () => Promise<void>;
  onOpenAIResearch?: (prompt?: string) => void;
  onOpenCompare?: () => void;
  isDemo?: boolean;
}

export const StockHeader: React.FC<StockHeaderProps> = ({
  ticker,
  name,
  exchange = "NSE",
  sector = "Large Cap Equity",
  industry,
  quote,
  isInWatchlist,
  onToggleWatchlist,
  onOpenAIResearch,
  onOpenCompare,
  isDemo = false,
}) => {
  const [isWatchlistBusy, setIsWatchlistBusy] = useState(false);
  const [copied, setCopied] = useState(false);

  // Check market status based on Indian standard trading hours (09:15 to 15:30 IST, Mon-Fri)
  const isMarketOpen = (() => {
    const now = new Date();
    // UTC offset for IST is +5.5 hours
    const istOffset = 5.5 * 60 * 60 * 1000;
    const istDate = new Date(now.getTime() + istOffset);
    const day = istDate.getUTCDay(); // 0 = Sun, 6 = Sat
    if (day === 0 || day === 6) return false;
    const hours = istDate.getUTCHours();
    const minutes = istDate.getUTCMinutes();
    const timeInMinutes = hours * 60 + minutes;
    // 9:15 is 555 min, 15:30 is 930 min
    return timeInMinutes >= 555 && timeInMinutes <= 930;
  })();

  const handleWatchlistClick = async () => {
    setIsWatchlistBusy(true);
    try {
      await onToggleWatchlist();
    } finally {
      setIsWatchlistBusy(false);
    }
  };

  const handleShare = () => {
    if (typeof window !== "undefined") {
      navigator.clipboard?.writeText(window.location.href);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    }
  };

  const displayName = name || (quote?.ticker === ticker ? (quote as any).name : undefined) || ticker;
  const displaySector = sector || "Equities";
  const avatarText = ticker.replace(/[^A-Z]/g, "").slice(0, 2) || "EQ";

  return (
    <div className="bg-surface border border-border rounded-2xl p-5 shadow-card">
      <div className="flex flex-col lg:flex-row lg:items-center justify-between gap-5">
        {/* Left: Avatar & Ticker Identity */}
        <div className="flex items-start sm:items-center gap-4">
          <div className="w-14 h-14 rounded-2xl bg-primary text-accent font-black text-xl flex items-center justify-center shadow-md flex-shrink-0 border border-primary-light/20">
            {avatarText}
          </div>

          <div className="space-y-1">
            <div className="flex flex-wrap items-center gap-2.5">
              <h1 className="text-2xl sm:text-3xl font-extrabold tracking-tight text-content">
                {ticker}
              </h1>
              <Badge variant="primary" size="md">
                {exchange}
              </Badge>
              {isDemo && (
                <Badge variant="gold" size="md">
                  DEMO DATA
                </Badge>
              )}
              {/* Market Status indicator */}
              <div
                className={cn(
                  "inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded-full text-[11px] font-semibold tracking-wide border",
                  isMarketOpen
                    ? "bg-financial-gain-bg text-financial-gain border-financial-gain/20"
                    : "bg-surface-subtle text-content-muted border-border"
                )}
              >
                <span
                  className={cn(
                    "w-2 h-2 rounded-full",
                    isMarketOpen ? "bg-financial-gain animate-pulse" : "bg-content-muted"
                  )}
                />
                {isMarketOpen ? "MARKET OPEN" : "MARKET CLOSED"}
              </div>
            </div>

            <div className="flex flex-wrap items-center gap-x-3 gap-y-1 text-xs text-content-muted font-medium">
              <span className="font-semibold text-content">{displayName}</span>
              <span className="text-border">•</span>
              <span className="flex items-center gap-1">
                <Building2 className="w-3.5 h-3.5 text-primary" />
                {displaySector} {industry ? `— ${industry}` : ""}
              </span>
              <span className="text-border">•</span>
              <span className="flex items-center gap-1">
                <Clock className="w-3.5 h-3.5 text-content-muted" />
                Updated: {quote?.timestamp ? new Date(quote.timestamp).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }) : "Real-Time"}
              </span>
            </div>
          </div>
        </div>

        {/* Right: Actions */}
        <div className="flex flex-wrap items-center gap-2.5 pt-2 lg:pt-0">
          <Button
            variant={isInWatchlist ? "secondary" : "outline"}
            size="sm"
            onClick={handleWatchlistClick}
            disabled={isWatchlistBusy}
            leftIcon={
              isInWatchlist ? (
                <BookmarkCheck className="w-4 h-4 text-accent" />
              ) : (
                <Bookmark className="w-4 h-4 text-content-muted" />
              )
            }
          >
            {isInWatchlist ? "In Watchlist" : "Add to Watchlist"}
          </Button>

          <Button
            variant="outline"
            size="sm"
            onClick={onOpenCompare}
            leftIcon={<ArrowRightLeft className="w-4 h-4 text-secondary" />}
          >
            Compare
          </Button>

          <Button
            variant="gold"
            size="sm"
            onClick={() => onOpenAIResearch?.()}
            leftIcon={<Sparkles className="w-4 h-4" />}
          >
            AI Research
          </Button>

          <button
            onClick={handleShare}
            className="p-2 rounded-lg border border-border hover:bg-surface-subtle text-content-muted hover:text-content transition-colors"
            title="Copy Workspace Link"
            aria-label="Copy Workspace Link"
          >
            {copied ? <Check className="w-4 h-4 text-financial-gain" /> : <Share2 className="w-4 h-4" />}
          </button>
        </div>
      </div>
    </div>
  );
};
