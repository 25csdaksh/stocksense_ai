"use client";

import React from "react";
import Link from "next/link";
import { AppLayout } from "@/components/layout/AppLayout";
import { StatCard } from "@/components/common/StatCard";
import { Card, CardHeader, CardTitle, CardDescription, CardContent } from "@/components/common/Card";
import { Badge } from "@/components/common/Badge";
import { Button } from "@/components/common/Button";
import { POPULAR_INDIAN_STOCKS, MAJOR_INDICES } from "@/lib/constants";
import {
  Brain,
  TrendingUp,
  AlertTriangle,
  Activity,
  ArrowUpRight,
  Sparkles,
  Zap,
} from "lucide-react";

export default function DashboardPage() {
  return (
    <AppLayout>
      <div className="space-y-6">
        {/* Top Intelligence Banner */}
        <div className="relative overflow-hidden rounded-2xl bg-gradient-to-r from-primary to-secondary p-6 text-white shadow-card">
          <div className="relative z-10 flex flex-col md:flex-row items-start md:items-center justify-between gap-4">
            <div className="space-y-1">
              <div className="flex items-center gap-2">
                <span className="text-xs font-bold uppercase tracking-wider text-accent">
                  Phase 5.1 Foundation Active
                </span>
                <span className="w-1.5 h-1.5 rounded-full bg-accent" />
                <span className="text-xs text-white/80">NSE & BSE Connected</span>
              </div>
              <h1 className="text-2xl lg:text-3xl font-extrabold tracking-tight">
                Executive Market Intelligence
              </h1>
              <p className="text-xs lg:text-sm text-white/80 max-w-xl">
                Multi-agent LangGraph research, real-time statistical anomaly detection, and Merton jump diffusion scenario engine.
              </p>
            </div>

            <div className="flex items-center gap-3">
              <Link href="/research">
                <Button variant="gold" size="md" leftIcon={<Sparkles className="w-4 h-4" />}>
                  AI Research Agent
                </Button>
              </Link>
            </div>
          </div>
          {/* Subtle Background Accent Pattern */}
          <div className="absolute -right-10 -bottom-10 w-64 h-64 rounded-full bg-accent/10 blur-2xl pointer-events-none" />
        </div>

        {/* Top Stat Cards */}
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
          <StatCard
            label="NIFTY 50 (Spot)"
            value="₹24,836.10"
            change={0.45}
            changeLabel="vs prev close"
            icon={<TrendingUp className="w-4 h-4 text-financial-gain" />}
          />
          <StatCard
            label="SENSEX (BSE)"
            value="₹81,332.72"
            change={0.38}
            changeLabel="vs prev close"
            icon={<TrendingUp className="w-4 h-4 text-financial-gain" />}
          />
          <StatCard
            label="Market Anomalies"
            value="3 Active"
            change={-12.5}
            changeLabel="24h volume surge"
            icon={<AlertTriangle className="w-4 h-4 text-financial-loss" />}
          />
          <StatCard
            label="Portfolio 95% VaR"
            value="1.42%"
            change={-0.15}
            changeLabel="daily risk metric"
            icon={<Activity className="w-4 h-4 text-primary" />}
          />
        </div>

        {/* Grid: Featured Indian Stocks & Quick Analytics */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Left 2 Cols: Indian Equities Hub */}
          <div className="lg:col-span-2 space-y-6">
            <Card>
              <CardHeader className="flex flex-row items-center justify-between">
                <div>
                  <CardTitle>Core Indian Market Equities</CardTitle>
                  <CardDescription>NSE large-cap constituents with live metrics</CardDescription>
                </div>
                <Link href="/stocks">
                  <Button variant="ghost" size="sm" rightIcon={<ArrowUpRight className="w-3.5 h-3.5" />}>
                    View Screener
                  </Button>
                </Link>
              </CardHeader>
              <CardContent>
                <div className="divide-y divide-border-subtle">
                  {POPULAR_INDIAN_STOCKS.slice(0, 5).map((stock) => (
                    <Link
                      key={stock.ticker}
                      href={`/stocks/${encodeURIComponent(stock.ticker)}`}
                      className="flex items-center justify-between py-3 px-2 rounded-lg hover:bg-surface-subtle transition-colors group"
                    >
                      <div className="flex items-center gap-3">
                        <div className="w-9 h-9 rounded-xl bg-surface-subtle border border-border flex items-center justify-center font-bold text-xs text-primary group-hover:border-primary/40 transition-colors">
                          {stock.ticker.substring(0, 2)}
                        </div>
                        <div>
                          <div className="flex items-center gap-2">
                            <span className="text-xs font-bold text-content group-hover:text-primary transition-colors">
                              {stock.ticker}
                            </span>
                            <Badge variant="primary" size="sm">
                              {stock.exchange}
                            </Badge>
                          </div>
                          <p className="text-[11px] text-content-muted">{stock.name}</p>
                        </div>
                      </div>
                      <div className="text-right">
                        <span className="text-xs font-semibold text-primary flex items-center gap-1 group-hover:underline">
                          Deep Dive <ArrowUpRight className="w-3 h-3" />
                        </span>
                      </div>
                    </Link>
                  ))}
                </div>
              </CardContent>
            </Card>
          </div>

          {/* Right Col: AI & RAG Quick Access */}
          <div className="space-y-6">
            <Card className="border-primary/20 bg-surface">
              <CardHeader>
                <div className="flex items-center gap-2 text-primary font-bold text-xs uppercase tracking-wider">
                  <Brain className="w-4 h-4 text-accent" />
                  <span>LangGraph Agent</span>
                </div>
                <CardTitle className="text-base mt-1">Autonomous Financial Research</CardTitle>
                <CardDescription>
                  Query multi-step SEC 10-K RAG, Fama-French Stock DNA, and risk factors.
                </CardDescription>
              </CardHeader>
              <CardContent className="space-y-3">
                <div className="p-3 rounded-xl bg-surface-subtle border border-border text-xs space-y-2">
                  <p className="font-semibold text-content">Sample Research Inquiries:</p>
                  <ul className="space-y-1.5 text-content-muted text-[11px]">
                    <li className="flex items-center gap-1.5">
                      <Zap className="w-3 h-3 text-accent" />
                      &ldquo;Analyze TCS.NS fundamentals vs INFY.NS&rdquo;
                    </li>
                    <li className="flex items-center gap-1.5">
                      <Zap className="w-3 h-3 text-accent" />
                      &ldquo;Search NVIDIA 10-K regulatory risk factors&rdquo;
                    </li>
                    <li className="flex items-center gap-1.5">
                      <Zap className="w-3 h-3 text-accent" />
                      &ldquo;Simulate 2020 COVID shock on RELIANCE.NS&rdquo;
                    </li>
                  </ul>
                </div>
                <Link href="/research" className="block w-full">
                  <Button variant="primary" size="md" className="w-full">
                    Open Research Terminal
                  </Button>
                </Link>
              </CardContent>
            </Card>
          </div>
        </div>
      </div>
    </AppLayout>
  );
}
