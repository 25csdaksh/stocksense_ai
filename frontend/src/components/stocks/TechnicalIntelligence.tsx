"use client";

import React from "react";
import { useStockTechnicals } from "@/hooks/useStockTechnicals";
import { Card, CardHeader, CardTitle, CardDescription, CardContent } from "@/components/common/Card";
import { Badge } from "@/components/common/Badge";
import { Skeleton } from "@/components/common/Skeleton";
import { Button } from "@/components/common/Button";
import { Activity, TrendingUp, TrendingDown, Gauge, BarChart3, AlertCircle, RefreshCw } from "lucide-react";
import { cn, formatCurrency } from "@/lib/utils";

export interface TechnicalIntelligenceProps {
  ticker: string;
  currency?: string;
  isDemo?: boolean;
}

export const TechnicalIntelligence: React.FC<TechnicalIntelligenceProps> = ({
  ticker,
  currency = "INR",
  isDemo: parentDemo = false,
}) => {
  const { technicals, isLoading, isError, error, isDemo, refresh } = useStockTechnicals(ticker);

  const displayDemo = parentDemo || isDemo;

  if (isLoading) {
    return (
      <Card className="border-border">
        <CardHeader>
          <Skeleton className="h-6 w-48" />
          <Skeleton className="h-4 w-72" />
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
            {[1, 2, 3, 4, 5, 6, 7, 8].map((i) => (
              <Skeleton key={i} className="h-24 rounded-xl" />
            ))}
          </div>
        </CardContent>
      </Card>
    );
  }

  if (isError || !technicals) {
    return (
      <Card className="border-border">
        <CardContent className="py-8 text-center space-y-3">
          <AlertCircle className="w-8 h-8 text-financial-loss mx-auto" />
          <p className="text-sm font-semibold text-content">Unable to load technical analytics</p>
          <p className="text-xs text-content-muted">{error || "Server response unavailable"}</p>
          <Button variant="outline" size="sm" onClick={() => refresh()}>
            Retry
          </Button>
        </CardContent>
      </Card>
    );
  }

  const {
    rsi_14,
    macd,
    sma_20,
    sma_50,
    ema_20,
    bollinger_bands,
    atr_14,
    realized_volatility_20d_pct,
    technical_bias,
  } = technicals;

  // RSI status classification
  const rsiClassification =
    rsi_14 >= 70 ? "OVERBOUGHT" : rsi_14 <= 30 ? "OVERSOLD" : "NEUTRAL ZONE";
  const rsiVariant =
    rsi_14 >= 70 ? "loss" : rsi_14 <= 30 ? "gain" : "neutral";

  // MACD calculation
  const macdVal = macd?.macd ?? macd?.macd_line ?? 0;
  const macdSignal = macd?.signal ?? macd?.signal_line ?? 0;
  const macdHist = macd?.histogram ?? (macdVal - macdSignal);
  const isMacdBullish = macdHist >= 0;

  // Bollinger Bands Bandwidth %
  const bbUpper = bollinger_bands?.upper ?? 0;
  const bbLower = bollinger_bands?.lower ?? 0;
  const bbMiddle = bollinger_bands?.middle ?? 0;
  const bbBandwidth =
    bollinger_bands?.bandwidth ??
    (bbMiddle > 0 ? (((bbUpper - bbLower) / bbMiddle) * 100).toFixed(2) : "—");

  const curr = (currency === "USD" ? "USD" : "INR") as "INR" | "USD";

  return (
    <Card className="border-border shadow-card">
      <CardHeader className="pb-3 border-b border-border/60 flex flex-col sm:flex-row sm:items-center justify-between gap-3">
        <div>
          <div className="flex items-center gap-2">
            <CardTitle className="text-lg font-bold flex items-center gap-2 text-content">
              <Activity className="w-5 h-5 text-primary" />
              Quantitative Technical Intelligence
            </CardTitle>
            {displayDemo && (
              <Badge variant="gold" size="sm">
                DEMO DATA
              </Badge>
            )}
            <Badge
              variant={
                technical_bias === "BULLISH"
                  ? "gain"
                  : technical_bias === "BEARISH"
                  ? "loss"
                  : "neutral"
              }
              size="md"
            >
              BIAS: {technical_bias || "NEUTRAL"}
            </Badge>
          </div>
          <CardDescription className="text-xs text-content-muted">
            Mathematical momentum oscillators, trend-following filters, and volatility envelopes
          </CardDescription>
        </div>

        <button
          onClick={() => refresh()}
          className="p-1.5 self-end sm:self-center rounded-lg text-content-muted hover:text-content hover:bg-surface-subtle transition-colors"
          title="Refresh Technicals"
        >
          <RefreshCw className="w-3.5 h-3.5" />
        </button>
      </CardHeader>

      <CardContent className="pt-4 space-y-4">
        {/* Indicators Grid */}
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-3.5">
          {/* 1. Relative Strength Index (RSI-14) */}
          <div className="p-3.5 rounded-xl bg-surface-subtle/70 border border-border space-y-2">
            <div className="flex items-center justify-between">
              <span className="text-[11px] font-bold text-content-muted uppercase tracking-wider">
                RSI (14-Day)
              </span>
              <Badge variant={rsiVariant as any} size="sm">
                {rsiClassification}
              </Badge>
            </div>
            <p className="text-2xl font-black text-content font-tabular">
              {rsi_14 !== undefined ? rsi_14.toFixed(1) : "—"}
            </p>
            {/* Visual Gauge Bar */}
            <div className="w-full bg-border h-1.5 rounded-full overflow-hidden">
              <div
                className={cn(
                  "h-full rounded-full transition-all duration-300",
                  rsi_14 >= 70
                    ? "bg-financial-loss"
                    : rsi_14 <= 30
                    ? "bg-financial-gain"
                    : "bg-primary"
                )}
                style={{ width: `${Math.min(100, Math.max(0, rsi_14))}%` }}
              />
            </div>
            <p className="text-[10px] text-content-muted">Baseline bands: 30 (Oversold) / 70 (Overbought)</p>
          </div>

          {/* 2. MACD (12, 26, 9) */}
          <div className="p-3.5 rounded-xl bg-surface-subtle/70 border border-border space-y-2">
            <div className="flex items-center justify-between">
              <span className="text-[11px] font-bold text-content-muted uppercase tracking-wider">
                MACD (12,26,9)
              </span>
              <Badge variant={isMacdBullish ? "gain" : "loss"} size="sm">
                {isMacdBullish ? "BULLISH CROSS" : "BEARISH CROSS"}
              </Badge>
            </div>
            <div className="flex items-baseline gap-2">
              <p className="text-2xl font-black text-content font-tabular">
                {macdVal >= 0 ? `+${macdVal.toFixed(2)}` : macdVal.toFixed(2)}
              </p>
              <span className="text-xs font-semibold text-content-muted font-tabular">
                Hist: {macdHist >= 0 ? `+${macdHist.toFixed(2)}` : macdHist.toFixed(2)}
              </span>
            </div>
            <div className="flex justify-between text-[10px] text-content-muted font-tabular">
              <span>MACD Line: {macdVal.toFixed(2)}</span>
              <span>Signal: {macdSignal.toFixed(2)}</span>
            </div>
          </div>

          {/* 3. Moving Averages (SMA & EMA) */}
          <div className="p-3.5 rounded-xl bg-surface-subtle/70 border border-border space-y-2">
            <div className="flex items-center justify-between">
              <span className="text-[11px] font-bold text-content-muted uppercase tracking-wider">
                Trend Averages
              </span>
              <span className="text-[10px] font-bold text-primary">SMA / EMA</span>
            </div>
            <div className="space-y-1 font-tabular text-xs">
              <div className="flex items-center justify-between">
                <span className="text-content-muted font-medium">EMA-20:</span>
                <span className="font-bold text-content">{formatCurrency(ema_20, curr)}</span>
              </div>
              <div className="flex items-center justify-between">
                <span className="text-content-muted font-medium">SMA-20:</span>
                <span className="font-bold text-content">{formatCurrency(sma_20, curr)}</span>
              </div>
              <div className="flex items-center justify-between">
                <span className="text-content-muted font-medium">SMA-50:</span>
                <span className="font-bold text-content">{formatCurrency(sma_50, curr)}</span>
              </div>
            </div>
          </div>

          {/* 4. Volatility & ATR */}
          <div className="p-3.5 rounded-xl bg-surface-subtle/70 border border-border space-y-2">
            <div className="flex items-center justify-between">
              <span className="text-[11px] font-bold text-content-muted uppercase tracking-wider">
                ATR & Realized Vol
              </span>
              <span className="text-[10px] font-bold text-accent">20D Window</span>
            </div>
            <div className="space-y-1 font-tabular text-xs">
              <div className="flex items-center justify-between">
                <span className="text-content-muted font-medium">ATR (14-Day):</span>
                <span className="font-bold text-content">{formatCurrency(atr_14, curr)}</span>
              </div>
              <div className="flex items-center justify-between">
                <span className="text-content-muted font-medium">Realized Vol (20d):</span>
                <span className="font-bold text-content">{realized_volatility_20d_pct?.toFixed(1)}% Ann.</span>
              </div>
              <div className="flex items-center justify-between">
                <span className="text-content-muted font-medium">BB Bandwidth:</span>
                <span className="font-bold text-content">{bbBandwidth}%</span>
              </div>
            </div>
          </div>
        </div>

        {/* Bollinger Bands Visual Strip */}
        <div className="p-3 bg-surface rounded-xl border border-border flex flex-col md:flex-row md:items-center justify-between gap-2 text-xs font-tabular">
          <div className="flex items-center gap-2">
            <BarChart3 className="w-4 h-4 text-primary flex-shrink-0" />
            <span className="font-bold text-content">Bollinger Bands (20, 2σ):</span>
          </div>
          <div className="flex flex-wrap items-center gap-4 text-content-muted">
            <span>
              Upper Band: <strong className="text-content">{formatCurrency(bbUpper, curr)}</strong>
            </span>
            <span>•</span>
            <span>
              Basis (SMA-20): <strong className="text-content">{formatCurrency(bbMiddle, curr)}</strong>
            </span>
            <span>•</span>
            <span>
              Lower Band: <strong className="text-content">{formatCurrency(bbLower, curr)}</strong>
            </span>
          </div>
        </div>
      </CardContent>
    </Card>
  );
};

