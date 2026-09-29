"use client";

import React from "react";
import { Card, CardHeader, CardTitle, CardDescription, CardContent } from "@/components/common/Card";
import { Badge } from "@/components/common/Badge";
import { formatPercent } from "@/lib/utils";
import { Gauge, Activity, TrendingUp, ShieldAlert } from "lucide-react";

export interface VolatilitySurveillanceProps {
  ticker: string;
  garchVol?: number;
  realizedVol?: number;
  ewmaVol?: number;
  forecast5d?: number[];
  regime?: string;
}

export const VolatilitySurveillance: React.FC<VolatilitySurveillanceProps> = ({
  ticker,
  garchVol = 38.4,
  realizedVol = 24.8,
  ewmaVol = 22.1,
  forecast5d = [36.2, 34.5, 32.8, 30.1, 28.4],
  regime = "HIGH_VOLATILITY_EXPANSION",
}) => {
  return (
    <Card>
      <CardHeader className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-2 pb-2">
        <div>
          <div className="flex items-center gap-2">
            <CardTitle className="flex items-center gap-2">
              <Gauge className="w-4 h-4 text-primary" />
              GARCH Volatility Regime &amp; Forecast: {ticker}
            </CardTitle>
            <Badge variant="loss" size="sm" className="font-mono text-[9px]">
              MODEL-DERIVED
            </Badge>
          </div>
          <CardDescription>
            Autoregressive conditional heteroskedasticity modeling and forward volatility path.
          </CardDescription>
        </div>
      </CardHeader>

      <CardContent className="space-y-4">
        <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
          <div className="p-3 bg-surface-subtle rounded-xl border border-border space-y-1">
            <span className="text-[10px] uppercase font-bold text-content-muted">GARCH(1,1) Volatility</span>
            <div className="text-base font-bold text-financial-loss font-tabular">
              {formatPercent(garchVol)}
            </div>
            <span className="text-[10px] text-content-muted">Annualized conditional σ</span>
          </div>

          <div className="p-3 bg-surface-subtle rounded-xl border border-border space-y-1">
            <span className="text-[10px] uppercase font-bold text-content-muted">20-Day Realized Vol</span>
            <div className="text-base font-bold text-content font-tabular">
              {formatPercent(realizedVol)}
            </div>
            <span className="text-[10px] text-content-muted">Historical sample σ</span>
          </div>

          <div className="p-3 bg-surface-subtle rounded-xl border border-border space-y-1">
            <span className="text-[10px] uppercase font-bold text-content-muted">EWMA Volatility</span>
            <div className="text-base font-bold text-secondary font-tabular">
              {formatPercent(ewmaVol)}
            </div>
            <span className="text-[10px] text-content-muted">λ = 0.94 decay</span>
          </div>

          <div className="p-3 bg-surface-subtle rounded-xl border border-border space-y-1">
            <span className="text-[10px] uppercase font-bold text-content-muted">Regime State</span>
            <div className="text-xs font-bold text-amber-600 truncate mt-1">
              {regime.replace(/_/g, " ")}
            </div>
            <span className="text-[10px] text-content-muted">Variance clustering</span>
          </div>
        </div>

        {/* 5-Day GARCH Horizon Forecast Table */}
        <div className="p-3.5 bg-surface-subtle/50 rounded-xl border border-border space-y-2">
          <div className="flex items-center justify-between text-xs">
            <span className="font-semibold text-content">GARCH(1,1) 5-Day Volatility Mean-Reversion Horizon</span>
            <span className="text-[10px] text-content-muted">Projected conditional paths</span>
          </div>

          <div className="grid grid-cols-5 gap-2 text-center pt-1">
            {forecast5d.map((val, idx) => (
              <div key={idx} className="p-2 bg-surface rounded-lg border border-border space-y-1">
                <span className="text-[10px] text-content-muted block font-medium">Day +{idx + 1}</span>
                <span className="text-xs font-bold text-primary font-tabular block">
                  {val.toFixed(1)}%
                </span>
              </div>
            ))}
          </div>
          <p className="text-[10px] text-content-muted pt-1">
            * Forward volatility forecasts represent econometric model simulations and do not guarantee future market behavior.
          </p>
        </div>
      </CardContent>
    </Card>
  );
};
