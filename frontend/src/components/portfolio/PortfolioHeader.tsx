"use client";

import React from "react";
import { Badge } from "@/components/common/Badge";
import { Button } from "@/components/common/Button";
import {
  Plus,
  RefreshCw,
  Sparkles,
  ShieldAlert,
  Clock,
  Briefcase,
  Activity,
} from "lucide-react";

export interface PortfolioHeaderProps {
  portfolioName?: string;
  portfolioId?: string;
  lastUpdated: Date;
  isMarketOpen?: boolean;
  isDemo?: boolean;
  isLoading?: boolean;
  onRefresh: () => void;
  onAddTransaction: () => void;
  onAIAnalyze: () => void;
  onStressTest: () => void;
}

export const PortfolioHeader: React.FC<PortfolioHeaderProps> = ({
  portfolioName = "Main Institutional Portfolio",
  portfolioId = "PORT-IN-001",
  lastUpdated,
  isMarketOpen = true,
  isDemo = false,
  isLoading = false,
  onRefresh,
  onAddTransaction,
  onAIAnalyze,
  onStressTest,
}) => {
  const formattedTime = lastUpdated.toLocaleTimeString("en-IN", {
    hour: "2-digit",
    minute: "2-digit",
    second: "2-digit",
  });

  return (
    <div className="flex flex-col lg:flex-row lg:items-center lg:justify-between gap-4 pb-6 border-b border-border">
      <div>
        <div className="flex flex-wrap items-center gap-2.5">
          <div className="w-9 h-9 rounded-xl bg-primary-light flex items-center justify-center text-primary">
            <Briefcase className="w-5 h-5" />
          </div>
          <div>
            <div className="flex items-center gap-2">
              <h1 className="text-2xl font-bold tracking-tight text-content font-heading">
                {portfolioName}
              </h1>
              <Badge variant="neutral" size="sm" className="font-mono text-[11px]">
                {portfolioId}
              </Badge>
              {isDemo && (
                <Badge variant="gold" size="sm" className="font-bold text-[10px] tracking-wider">
                  DEMO DATA
                </Badge>
              )}
            </div>
            <div className="flex flex-wrap items-center gap-3 text-xs text-content-muted mt-1">
              <span className="flex items-center gap-1">
                <Clock className="w-3.5 h-3.5" />
                Updated at {formattedTime}
              </span>
              <span className="text-border-subtle">•</span>
              <span className="flex items-center gap-1.5 font-medium">
                <span
                  className={`w-2 h-2 rounded-full ${
                    isMarketOpen ? "bg-emerald-500 animate-pulse" : "bg-rose-500"
                  }`}
                />
                <span className={isMarketOpen ? "text-financial-gain font-semibold" : "text-financial-loss font-semibold"}>
                  {isMarketOpen ? "NSE/BSE MARKET OPEN" : "NSE/BSE MARKET CLOSED"}
                </span>
              </span>
              <span className="text-border-subtle">•</span>
              <span className="flex items-center gap-1 text-[11px] text-content-muted">
                <Activity className="w-3.5 h-3.5 text-accent" />
                Parametric VaR & Real-Time Mark-to-Market
              </span>
            </div>
          </div>
        </div>
      </div>

      {/* Action Buttons */}
      <div className="flex flex-wrap items-center gap-2">
        <Button
          variant="outline"
          size="sm"
          onClick={onRefresh}
          disabled={isLoading}
          leftIcon={<RefreshCw className={`w-3.5 h-3.5 ${isLoading ? "animate-spin" : ""}`} />}
        >
          Refresh
        </Button>
        <Button
          variant="outline"
          size="sm"
          onClick={onStressTest}
          leftIcon={<ShieldAlert className="w-3.5 h-3.5 text-accent-dark" />}
        >
          Stress Test
        </Button>
        <Button
          variant="secondary"
          size="sm"
          onClick={onAIAnalyze}
          leftIcon={<Sparkles className="w-3.5 h-3.5 text-accent" />}
        >
          AI Analyze
        </Button>
        <Button
          variant="gold"
          size="sm"
          onClick={onAddTransaction}
          leftIcon={<Plus className="w-4 h-4" />}
        >
          Add Transaction
        </Button>
      </div>
    </div>
  );
};
