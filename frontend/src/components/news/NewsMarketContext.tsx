"use client";

import React from "react";
import { NewsArticle } from "@/types";
import { Activity, AlertTriangle, TrendingUp, Info } from "lucide-react";
import { Badge } from "@/components/common/Badge";
import { useRouter } from "next/navigation";

interface NewsMarketContextProps {
  articles: NewsArticle[];
}

export const NewsMarketContext: React.FC<NewsMarketContextProps> = ({ articles }) => {
  const router = useRouter();

  // Pick articles with known active tickers
  const contextualArticles = articles
    .filter((a) => a.ticker || (a.related_tickers && a.related_tickers.length > 0))
    .slice(0, 3);

  if (contextualArticles.length === 0) {
    return null;
  }

  return (
    <div className="bg-surface p-5 rounded-2xl border border-border shadow-card space-y-3.5">
      <div className="flex items-center justify-between border-b border-border pb-3">
        <div className="flex items-center gap-2">
          <Activity className="w-4 h-4 text-primary" />
          <h3 className="text-xs font-bold text-content uppercase tracking-wider">
            News-to-Market Cross Telemetry
          </h3>
        </div>
        <span className="text-[10px] text-content-muted">Coinciding Signals</span>
      </div>

      <div className="space-y-3">
        {contextualArticles.map((art) => {
          const ticker = art.ticker || art.related_tickers?.[0] || "MARKET";

          return (
            <div
              key={art.id}
              className="p-3 bg-surface-subtle/50 rounded-xl border border-border space-y-2"
            >
              <div className="flex items-center justify-between text-xs">
                <span className="font-bold text-content">{ticker}</span>
                <Badge variant="outline" size="sm">
                  {art.source}
                </Badge>
              </div>

              <p className="text-xs font-semibold text-content line-clamp-1">
                {art.title}
              </p>

              <div className="flex flex-wrap items-center gap-2 pt-1 border-t border-border/60 text-[11px] text-content-muted">
                <span className="flex items-center gap-1">
                  <Activity className="w-3 h-3 text-secondary" />
                  <span>Wire Coincides with Price Volatility</span>
                </span>
                <button
                  onClick={() => router.push(`/anomalies?ticker=${encodeURIComponent(ticker)}`)}
                  className="text-financial-loss hover:underline font-semibold ml-auto flex items-center gap-1"
                >
                  <AlertTriangle className="w-3 h-3" />
                  <span>Check Anomalies</span>
                </button>
              </div>
            </div>
          );
        })}
      </div>

      <div className="bg-surface-subtle p-2.5 rounded-xl border border-border flex items-start gap-2 text-[10px] text-content-muted">
        <Info className="w-3.5 h-3.5 text-primary shrink-0 mt-0.5" />
        <p>
          Telemetry linkages describe temporal coincidence between media wire timestamps and quantitative pricing deviations, not confirmed causality.
        </p>
      </div>
    </div>
  );
};
