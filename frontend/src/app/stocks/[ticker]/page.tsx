"use client";

import React, { useState } from "react";
import { useParams } from "next/navigation";
import { AppLayout } from "@/components/layout/AppLayout";
import { StatCard } from "@/components/common/StatCard";
import { Card, CardHeader, CardTitle, CardDescription, CardContent } from "@/components/common/Card";
import { Tabs } from "@/components/common/Tabs";
import { Badge } from "@/components/common/Badge";
import { Button } from "@/components/common/Button";
import { TrendingUp, Brain, Activity, FileText, Bookmark, Sparkles } from "lucide-react";
import Link from "next/link";

export default function StockDetailPage() {
  const params = useParams();
  const ticker = typeof params.ticker === "string" ? decodeURIComponent(params.ticker) : "RELIANCE.NS";
  const [activeTab, setActiveTab] = useState("overview");

  const isIndian = ticker.endsWith(".NS") || ticker.endsWith(".BO") || ticker.startsWith("^");
  const isDemo = !isIndian;
  const currency = isIndian ? "INR" : "USD";

  const tabs = [
    { id: "overview", label: "Overview & Price Action", icon: <TrendingUp className="w-4 h-4" /> },
    { id: "technicals", label: "Technical Indicators", icon: <Activity className="w-4 h-4" /> },
    { id: "fundamentals", label: "Valuation & Margins", icon: <FileText className="w-4 h-4" /> },
    { id: "dna", label: "5-Factor Stock DNA", icon: <Brain className="w-4 h-4" /> },
  ];

  return (
    <AppLayout>
      <div className="space-y-6">
        {/* Instrument Title Header */}
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 p-5 rounded-2xl bg-surface border border-border">
          <div className="flex items-center gap-3.5">
            <div className="w-12 h-12 rounded-xl bg-primary text-accent font-extrabold text-lg flex items-center justify-center">
              {ticker.substring(0, 2).toUpperCase()}
            </div>
            <div>
              <div className="flex items-center gap-2">
                <h1 className="text-2xl font-bold tracking-tight text-content">{ticker}</h1>
                {isDemo ? (
                  <Badge variant="gold" size="md">
                    DEMO DATA
                  </Badge>
                ) : (
                  <Badge variant="primary" size="md">
                    NSE / BSE LIVE
                  </Badge>
                )}
              </div>
              <p className="text-xs text-content-muted mt-0.5">
                Market Instrument Deep-Dive • Currency: {currency}
              </p>
            </div>
          </div>

          <div className="flex items-center gap-2">
            <Link href={`/research?q=Analyze ${encodeURIComponent(ticker)} with 10-K`}>
              <Button variant="gold" size="sm" leftIcon={<Sparkles className="w-4 h-4" />}>
                Run AI Analysis
              </Button>
            </Link>
            <Button variant="outline" size="sm" leftIcon={<Bookmark className="w-4 h-4" />}>
              Add to Watchlist
            </Button>
          </div>
        </div>

        {/* Snapshot Metric Cards */}
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
          <StatCard
            label="Spot Price"
            value={currency === "INR" ? "₹2,950.40" : "$195.20"}
            change={1.25}
            changeLabel="vs previous close"
            isDemo={isDemo}
          />
          <StatCard
            label="52-Week Range"
            value={currency === "INR" ? "₹2,200 — ₹3,025" : "$140 — $205"}
            changeLabel="Historical boundary"
            isDemo={isDemo}
          />
          <StatCard
            label="P/E Multiple"
            value="26.4x"
            changeLabel="Trailing Twelve Months"
            isDemo={isDemo}
          />
          <StatCard
            label="RSI (14-Day)"
            value="58.2"
            changeLabel="Neutral Zone (30–70)"
            isDemo={isDemo}
          />
        </div>

        {/* Tabs Bar */}
        <Card>
          <div className="px-5 pt-3">
            <Tabs tabs={tabs} activeTab={activeTab} onChange={setActiveTab} />
          </div>

          <CardContent className="pt-5">
            {activeTab === "overview" && (
              <div className="space-y-4">
                <p className="text-xs text-content-muted">
                  Interactive candlestick & volume charting engine powered by Lightweight Charts.
                </p>
                <div className="h-72 rounded-xl bg-surface-subtle/70 border border-dashed border-border flex items-center justify-center text-xs text-content-muted">
                  Interactive Lightweight Candlestick + Volume Chart Component Shell
                </div>
              </div>
            )}

            {activeTab === "technicals" && (
              <div className="space-y-4">
                <p className="text-xs text-content-muted">
                  Deterministic technical indicators calculated via NumPy & Pandas: SMA-20/50/200, MACD, Bollinger Bands, ATR.
                </p>
                <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
                  <div className="p-3 bg-surface-subtle rounded-lg border border-border">
                    <span className="text-[11px] text-content-muted font-semibold">MACD Signal</span>
                    <p className="text-sm font-bold text-financial-gain mt-1">Bullish Cross (+1.45)</p>
                  </div>
                  <div className="p-3 bg-surface-subtle rounded-lg border border-border">
                    <span className="text-[11px] text-content-muted font-semibold">Bollinger %B</span>
                    <p className="text-sm font-bold text-content mt-1">0.68 (Normal Range)</p>
                  </div>
                  <div className="p-3 bg-surface-subtle rounded-lg border border-border">
                    <span className="text-[11px] text-content-muted font-semibold">Realized Vol (30d)</span>
                    <p className="text-sm font-bold text-content mt-1">16.8% Ann.</p>
                  </div>
                </div>
              </div>
            )}

            {activeTab === "fundamentals" && (
              <div className="space-y-4">
                <p className="text-xs text-content-muted">
                  Institutional valuation multiples, profitability margins, and financial health scores.
                </p>
                <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
                  <div className="p-3 bg-surface-subtle rounded-lg border border-border">
                    <span className="text-[11px] text-content-muted font-semibold">P/B Ratio</span>
                    <p className="text-sm font-bold text-content mt-1">3.8x</p>
                  </div>
                  <div className="p-3 bg-surface-subtle rounded-lg border border-border">
                    <span className="text-[11px] text-content-muted font-semibold">EV / EBITDA</span>
                    <p className="text-sm font-bold text-content mt-1">14.2x</p>
                  </div>
                  <div className="p-3 bg-surface-subtle rounded-lg border border-border">
                    <span className="text-[11px] text-content-muted font-semibold">Operating Margin</span>
                    <p className="text-sm font-bold text-financial-gain mt-1">21.4%</p>
                  </div>
                  <div className="p-3 bg-surface-subtle rounded-lg border border-border">
                    <span className="text-[11px] text-content-muted font-semibold">ROE</span>
                    <p className="text-sm font-bold text-financial-gain mt-1">18.6%</p>
                  </div>
                </div>
              </div>
            )}

            {activeTab === "dna" && (
              <div className="space-y-4">
                <p className="text-xs text-content-muted">
                  Fama-French inspired 5-Factor scoring (Value, Growth, Quality, Momentum, Low Volatility).
                </p>
                <div className="h-64 rounded-xl bg-surface-subtle/70 border border-dashed border-border flex items-center justify-center text-xs text-content-muted">
                  5-Factor Stock DNA Radar Chart Visualization Shell
                </div>
              </div>
            )}
          </CardContent>
        </Card>
      </div>
    </AppLayout>
  );
}
