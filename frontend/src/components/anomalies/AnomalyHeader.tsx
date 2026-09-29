"use client";

import React from "react";
import { Badge } from "@/components/common/Badge";
import { Button } from "@/components/common/Button";
import {
  ShieldAlert,
  RefreshCw,
  Sparkles,
  Activity,
  Clock,
  Zap,
} from "lucide-react";

export interface AnomalyHeaderProps {
  totalActiveCount: number;
  criticalCount: number;
  systemicStressIndex: number;
  lastUpdated: Date;
  isMarketOpen?: boolean;
  isDemo?: boolean;
  isLoading?: boolean;
  onRefresh: () => void;
  onAIInvestigate: () => void;
}

export const AnomalyHeader: React.FC<AnomalyHeaderProps> = ({
  totalActiveCount,
  criticalCount,
  systemicStressIndex,
  lastUpdated,
  isMarketOpen = true,
  isDemo = false,
  isLoading = false,
  onRefresh,
  onAIInvestigate,
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
          <div className="w-9 h-9 rounded-xl bg-financial-loss-bg flex items-center justify-center text-financial-loss">
            <ShieldAlert className="w-5 h-5" />
          </div>
          <div>
            <div className="flex items-center gap-2">
              <h1 className="text-2xl font-bold tracking-tight text-content font-heading">
                Market Anomaly &amp; Systemic Risk Surveillance
              </h1>
              <Badge variant="loss" size="sm" className="font-bold text-[10px] tracking-wider">
                Isolation Forest + GARCH
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
                  {isMarketOpen ? "NSE/BSE SURVEILLANCE ACTIVE" : "MARKET CLOSED (OFF-HOURS REPLAY)"}
                </span>
              </span>
              <span className="text-border-subtle">•</span>
              <span className="flex items-center gap-1 font-semibold text-content">
                <Activity className="w-3.5 h-3.5 text-accent" />
                Systemic Stress Index: <span className="font-mono text-financial-loss">{systemicStressIndex.toFixed(1)} / 100</span>
              </span>
            </div>
          </div>
        </div>
      </div>

      {/* Action Controls */}
      <div className="flex flex-wrap items-center gap-2">
        <Button
          variant="outline"
          size="sm"
          onClick={onRefresh}
          disabled={isLoading}
          leftIcon={<RefreshCw className={`w-3.5 h-3.5 ${isLoading ? "animate-spin" : ""}`} />}
        >
          Refresh Feeds
        </Button>
        <Button
          variant="gold"
          size="sm"
          onClick={onAIInvestigate}
          leftIcon={<Sparkles className="w-3.5 h-3.5 text-primary" />}
        >
          AI Anomaly Investigation
        </Button>
      </div>
    </div>
  );
};
