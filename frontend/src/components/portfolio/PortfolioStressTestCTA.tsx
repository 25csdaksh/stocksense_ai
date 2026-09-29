"use client";

import React from "react";
import { useRouter } from "next/navigation";
import { Card, CardHeader, CardTitle, CardDescription, CardContent } from "@/components/common/Card";
import { Badge } from "@/components/common/Badge";
import { Button } from "@/components/common/Button";
import { formatCurrency, formatPercent } from "@/lib/utils";
import { usePortfolioStressTest } from "@/hooks/usePortfolioStressTest";
import { ShieldAlert, ArrowRight, Zap, AlertOctagon } from "lucide-react";

export interface PortfolioStressTestCTAProps {
  portfolioId?: string;
  holdings?: Array<{ ticker: string; shares: number; price: number; sector?: string; beta?: number }>;
}

export const PortfolioStressTestCTA: React.FC<PortfolioStressTestCTAProps> = ({
  portfolioId = "main",
  holdings,
}) => {
  const router = useRouter();
  const { stressData, isLoading } = usePortfolioStressTest(holdings);

  const crisesList = Object.entries(stressData.crises_stress_results || {});

  const handleOpenScenarios = () => {
    router.push(`/scenarios?portfolioId=${encodeURIComponent(portfolioId)}`);
  };

  return (
    <Card className="border-accent/30 bg-gradient-to-r from-surface via-surface to-accent-light/20 overflow-hidden">
      <CardHeader className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-3 pb-3">
        <div>
          <div className="flex items-center gap-2">
            <div className="w-7 h-7 rounded-lg bg-financial-loss-bg flex items-center justify-center text-financial-loss">
              <ShieldAlert className="w-4 h-4" />
            </div>
            <CardTitle className="text-base font-bold">Historical Crisis Stress Testing Engine</CardTitle>
            <Badge variant="gold" size="sm" className="font-semibold text-[10px]">
              Macro Shocks
            </Badge>
          </div>
          <CardDescription>
            Simulate instantaneous multi-crisis market drawdowns across historical liquidity and geopolitical shocks.
          </CardDescription>
        </div>

        <Button
          variant="gold"
          size="sm"
          onClick={handleOpenScenarios}
          rightIcon={<ArrowRight className="w-3.5 h-3.5" />}
        >
          Open Scenario Simulator
        </Button>
      </CardHeader>

      <CardContent className="space-y-3 pt-2">
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-3">
          {crisesList.map(([key, crisis]) => (
            <div
              key={key}
              className="p-3 bg-surface rounded-xl border border-border hover:border-financial-loss/40 transition-all space-y-1.5"
            >
              <div className="flex items-center justify-between">
                <span className="text-xs font-bold text-content truncate">{crisis.crisis_name}</span>
                <span className="text-xs font-bold font-tabular text-financial-loss">
                  {formatPercent(crisis.projected_drawdown_pct)}
                </span>
              </div>

              <div className="flex items-center justify-between text-[11px]">
                <span className="text-content-muted">Projected Loss:</span>
                <span className="font-bold text-financial-loss font-tabular">
                  -{formatCurrency(crisis.projected_portfolio_loss_dollars, "INR", { compact: true })}
                </span>
              </div>

              <div className="flex items-center justify-between text-[11px] pt-1 border-t border-border/50">
                <span className="text-content-muted">Stressed Value:</span>
                <span className="font-bold text-content font-tabular">
                  {formatCurrency(crisis.stressed_portfolio_value, "INR", { compact: true })}
                </span>
              </div>

              <p className="text-[10px] text-content-muted line-clamp-2 pt-0.5">{crisis.description}</p>
            </div>
          ))}
        </div>
      </CardContent>
    </Card>
  );
};
