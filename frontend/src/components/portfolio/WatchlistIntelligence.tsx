"use client";

import React from "react";
import { WatchlistContext } from "@/types/portfolio-copilot";
import { Bookmark, TrendingUp, TrendingDown, Eye, Activity } from "lucide-react";

interface WatchlistIntelligenceProps {
  watchlist: WatchlistContext;
  onSelectSymbol?: (symbol: string) => void;
}

export const WatchlistIntelligence: React.FC<WatchlistIntelligenceProps> = ({
  watchlist,
  onSelectSymbol,
}) => {
  return (
    <div className="bg-surface border border-border rounded-2xl p-6 shadow-card space-y-5">
      <div className="flex items-center justify-between border-b border-border pb-4">
        <div className="flex items-center gap-2">
          <div className="p-2 rounded-xl bg-primary/10 text-primary border border-primary/20">
            <Bookmark className="w-5 h-5" />
          </div>
          <div>
            <h3 className="text-sm font-black text-content uppercase tracking-wider">
              Watchlist Intelligence
            </h3>
            <p className="text-xs text-content-muted">
              Real-time telemetry and momentum indicators for tracked assets ({watchlist.total_items} items)
            </p>
          </div>
        </div>
      </div>

      {watchlist.items.length > 0 ? (
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 text-xs">
          {watchlist.items.map((item) => {
            const isGain = item.change_pct >= 0;
            return (
              <div
                key={item.ticker}
                onClick={() => onSelectSymbol && onSelectSymbol(item.ticker)}
                className="p-3.5 bg-surface-subtle rounded-xl border border-border/70 hover:border-primary/50 cursor-pointer transition-all space-y-2"
              >
                <div className="flex items-center justify-between">
                  <span className="font-bold text-content font-mono text-sm">{item.ticker}</span>
                  <div className={`flex items-center gap-1 font-bold font-tabular ${isGain ? "text-financial-gain" : "text-financial-loss"}`}>
                    {isGain ? <TrendingUp className="w-3.5 h-3.5" /> : <TrendingDown className="w-3.5 h-3.5" />}
                    <span>{isGain ? "+" : ""}{item.change_pct}%</span>
                  </div>
                </div>

                <div className="flex items-center justify-between font-tabular text-content-muted">
                  <span>Price: <strong className="text-content">₹{item.current_price.toLocaleString("en-IN")}</strong></span>
                  {item.target_price && (
                    <span className="text-[10px]">Target: ₹{item.target_price}</span>
                  )}
                </div>

                {item.notes && (
                  <p className="text-[10px] text-content-muted line-clamp-1 italic font-sans">
                    {item.notes}
                  </p>
                )}
              </div>
            );
          })}
        </div>
      ) : (
        <p className="text-xs text-content-muted italic">
          No watchlist assets registered for current user profile.
        </p>
      )}
    </div>
  );
};
