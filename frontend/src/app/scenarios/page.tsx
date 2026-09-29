"use client";

import React, { useState } from "react";
import { AppLayout } from "@/components/layout/AppLayout";
import { Card, CardHeader, CardTitle, CardDescription, CardContent } from "@/components/common/Card";
import { StatCard } from "@/components/common/StatCard";
import { Select } from "@/components/common/Select";
import { Button } from "@/components/common/Button";
import { Badge } from "@/components/common/Badge";
import { Activity, Play, AlertOctagon, HelpCircle } from "lucide-react";

export default function ScenariosPage() {
  const [selectedTicker, setSelectedTicker] = useState("RELIANCE.NS");
  const [selectedCrisis, setSelectedCrisis] = useState("2020_COVID");

  const tickerOptions = [
    { value: "RELIANCE.NS", label: "RELIANCE.NS (NSE India)" },
    { value: "TCS.NS", label: "TCS.NS (NSE India)" },
    { value: "INFY.NS", label: "INFY.NS (NSE India)" },
    { value: "NVDA", label: "NVDA (Demo Data)" },
  ];

  const crisisOptions = [
    { value: "2020_COVID", label: "2020 COVID Market Crash (-38% Index Drawdown)" },
    { value: "2008_GFC", label: "2008 Global Financial Crisis (-54% Liquidity Freeze)" },
    { value: "2022_TECH_SELLOFF", label: "2022 Tech Rate Hike Selloff (-32% Multiple Compression)" },
  ];

  return (
    <AppLayout>
      <div className="space-y-6">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
          <div>
            <div className="flex items-center gap-2">
              <h1 className="text-2xl font-bold tracking-tight text-content">Scenario Simulation & Stress Engine</h1>
              <Badge variant="primary" size="md">
                Merton Jump Diffusion
              </Badge>
            </div>
            <p className="text-xs text-content-muted mt-0.5">
              1,000+ Path Monte Carlo stochastic simulations and historical crisis replay.
            </p>
          </div>
        </div>

        {/* Configuration Bar */}
        <Card>
          <CardHeader>
            <CardTitle>Simulation Parameters</CardTitle>
            <CardDescription>Configure stochastic paths, horizon, and historical stress overlays</CardDescription>
          </CardHeader>
          <CardContent className="grid grid-cols-1 md:grid-cols-3 gap-4 items-end">
            <Select
              label="Target Instrument"
              options={tickerOptions}
              value={selectedTicker}
              onChange={(e) => setSelectedTicker(e.target.value)}
            />
            <Select
              label="Historical Crisis Replay"
              options={crisisOptions}
              value={selectedCrisis}
              onChange={(e) => setSelectedCrisis(e.target.value)}
            />
            <Button variant="gold" size="md" leftIcon={<Play className="w-4 h-4" />}>
              Run Monte Carlo Simulation
            </Button>
          </CardContent>
        </Card>

        {/* Quantile Metrics */}
        <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
          <StatCard
            label="95% Value-at-Risk (VaR)"
            value="-5.84%"
            changeLabel="30-Day Simulated Horizon"
            icon={<AlertOctagon className="w-4 h-4 text-financial-loss" />}
          />
          <StatCard
            label="Expected Shortfall (CVaR)"
            value="-8.12%"
            changeLabel="Tail risk beyond 95th percentile"
            icon={<AlertOctagon className="w-4 h-4 text-financial-loss" />}
          />
          <StatCard
            label="Median Path (p50)"
            value="+2.40%"
            changeLabel="Expected drift return"
            icon={<Activity className="w-4 h-4 text-primary" />}
          />
        </div>

        {/* Simulation Chart Shell */}
        <Card>
          <CardHeader className="flex flex-row items-center justify-between">
            <div>
              <CardTitle>Stochastic Quantile Cone (p05 – p95)</CardTitle>
              <CardDescription>1,000 simulated price trajectories across 30 trading days</CardDescription>
            </div>
            <div className="flex items-center gap-1.5 text-[11px] text-content-muted">
              <HelpCircle className="w-3.5 h-3.5" />
              <span>Simulation, not financial prediction</span>
            </div>
          </CardHeader>
          <CardContent>
            <div className="h-72 rounded-xl bg-surface-subtle/70 border border-dashed border-border flex items-center justify-center text-xs text-content-muted">
              Simulation Cone Distribution Recharts AreaLine Chart Shell
            </div>
          </CardContent>
        </Card>
      </div>
    </AppLayout>
  );
}
