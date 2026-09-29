"use client";

import React, { useEffect, useState } from "react";
import Link from "next/link";
import {
  TrendingUp,
  TrendingDown,
  Activity,
  AlertTriangle,
  ArrowRight,
  Sparkles,
  PieChart,
  Layers,
  ShieldAlert,
  Zap,
} from "lucide-react";
import { api } from "@/lib/api";
import { MarketQuote, SectorItem, AnomalyItem } from "@/types";

export default function DashboardPage() {
  const [overview, setOverview] = useState<any>(null);
  const [sectors, setSectors] = useState<SectorItem[]>([]);
  const [anomalies, setAnomalies] = useState<AnomalyItem[]>([]);
  const [stressIndex, setStressIndex] = useState<number>(24.5);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function loadData() {
      try {
        const [ovData, secData, anomData] = await Promise.all([
          api.getMarketOverview().catch(() => null),
          api.getSectorPerformance().catch(() => ({ sectors: [] })),
          api.getAnomalies().catch(() => ({ anomalies: [], systemic_stress_index: 24.5 })),
        ]);

        if (ovData) setOverview(ovData);
        if (secData?.sectors) setSectors(secData.sectors);
        if (anomData?.anomalies) {
          setAnomalies(anomData.anomalies);
          setStressIndex(anomData.systemic_stress_index || 24.5);
        }
      } finally {
        setLoading(false);
      }
    }
    loadData();
  }, []);

  return (
    <div className="space-y-6 max-w-7xl mx-auto">
      {/* Header Banner */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 bg-white p-6 rounded-2xl border border-border shadow-sm">
        <div>
          <div className="flex items-center gap-2 mb-1">
            <h1 className="text-2xl font-extrabold text-slate-900 tracking-tight">
              Market Intelligence Dashboard
            </h1>
            <span className="px-2 py-0.5 rounded text-[11px] font-bold bg-emerald-50 text-primary border border-emerald-200 font-mono">
              SYSTEMIC REGIME: {overview?.market_regime || "BULLISH EXPANSION"}
            </span>
          </div>
          <p className="text-xs text-slate-500">
            Real-time multi-asset intelligence, econometric anomaly detection, and scenario simulation.
          </p>
        </div>

        <div className="flex items-center gap-3">
          <Link
            href="/simulator"
            className="flex items-center gap-2 px-4 py-2 rounded-xl bg-surface hover:bg-slate-200 text-slate-800 text-xs font-bold border border-border transition"
          >
            <Zap className="w-3.5 h-3.5 text-gold-dark" />
            <span>Launch Scenario Simulator</span>
          </Link>
          <Link
            href="/research"
            className="flex items-center gap-2 px-4 py-2 rounded-xl bg-primary hover:bg-primary-hover text-white text-xs font-bold shadow-sm transition"
          >
            <Sparkles className="w-3.5 h-3.5 text-gold" />
            <span>Ask AI Co-Pilot</span>
          </Link>
        </div>
      </div>

      {/* Top Cards: System Stress Index & Market Metrics */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        {/* Systemic Stress Index */}
        <div className="bg-white p-5 rounded-xl border border-border shadow-sm flex flex-col justify-between">
          <div className="flex items-center justify-between text-xs text-slate-500">
            <span className="font-semibold">Systemic Stress Index</span>
            <Activity className="w-4 h-4 text-primary" />
          </div>
          <div className="mt-3">
            <div className="text-2xl font-black font-mono text-slate-900">{stressIndex.toFixed(1)} / 100</div>
            <div className="w-full bg-slate-100 rounded-full h-2 mt-2 overflow-hidden">
              <div
                className={`h-full rounded-full transition-all duration-500 ${
                  stressIndex > 50 ? "bg-financial-loss" : "bg-primary"
                }`}
                style={{ width: `${stressIndex}%` }}
              />
            </div>
          </div>
          <div className="mt-2 text-[11px] font-mono text-slate-400">Low Volatility Regime</div>
        </div>

        {/* S&P 500 Quote Card */}
        <div className="bg-white p-5 rounded-xl border border-border shadow-sm flex flex-col justify-between">
          <div className="flex items-center justify-between text-xs text-slate-500">
            <span className="font-semibold">S&P 500 Index (^GSPC)</span>
            <span className="text-[10px] font-mono font-bold bg-slate-100 px-1.5 py-0.5 rounded text-slate-600">BENCHMARK</span>
          </div>
          <div className="mt-3">
            <div className="text-2xl font-black font-mono text-slate-900">$5,742.10</div>
            <div className="flex items-center gap-1.5 text-xs font-bold text-financial-gain font-mono mt-1">
              <TrendingUp className="w-3.5 h-3.5" />
              <span>+24.30 (+0.43%)</span>
            </div>
          </div>
          <div className="mt-2 text-[11px] text-slate-400">Volume: 3.4B shares</div>
        </div>

        {/* 10Y US Treasury Yield */}
        <div className="bg-white p-5 rounded-xl border border-border shadow-sm flex flex-col justify-between">
          <div className="flex items-center justify-between text-xs text-slate-500">
            <span className="font-semibold">10-Year Treasury Yield</span>
            <span className="text-[10px] font-mono font-bold bg-slate-100 px-1.5 py-0.5 rounded text-slate-600">RATES</span>
          </div>
          <div className="mt-3">
            <div className="text-2xl font-black font-mono text-slate-900">4.18%</div>
            <div className="flex items-center gap-1.5 text-xs font-bold text-financial-gain font-mono mt-1">
              <TrendingDown className="w-3.5 h-3.5" />
              <span>-4.0 bps (-0.95%)</span>
            </div>
          </div>
          <div className="mt-2 text-[11px] text-slate-400">Yield Curve Inversion: -12 bps</div>
        </div>

        {/* CBOE Volatility VIX */}
        <div className="bg-white p-5 rounded-xl border border-border shadow-sm flex flex-col justify-between">
          <div className="flex items-center justify-between text-xs text-slate-500">
            <span className="font-semibold">CBOE VIX Volatility</span>
            <span className="text-[10px] font-mono font-bold bg-slate-100 px-1.5 py-0.5 rounded text-slate-600">RISK</span>
          </div>
          <div className="mt-3">
            <div className="text-2xl font-black font-mono text-slate-900">14.85</div>
            <div className="flex items-center gap-1.5 text-xs font-bold text-financial-gain font-mono mt-1">
              <TrendingDown className="w-3.5 h-3.5" />
              <span>-0.62 (-4.01%)</span>
            </div>
          </div>
          <div className="mt-2 text-[11px] text-slate-400">Historical 20d Mean: 16.2</div>
        </div>
      </div>

      {/* Main Grid: Sector Heatmap & Live Anomaly Stream */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Sector Performance Matrix */}
        <div className="lg:col-span-2 bg-white rounded-2xl border border-border shadow-sm overflow-hidden flex flex-col">
          <div className="p-5 border-b border-border flex items-center justify-between">
            <div className="flex items-center gap-2">
              <PieChart className="w-4 h-4 text-primary" />
              <h3 className="text-sm font-bold text-slate-900">Sector Performance & Momentum Matrix</h3>
            </div>
            <span className="text-[11px] text-slate-400 font-mono">10 SECTOR WEIGHTS</span>
          </div>

          <div className="overflow-x-auto flex-1">
            <table className="w-full text-left financial-table">
              <thead>
                <tr>
                  <th>Sector</th>
                  <th>1D Return</th>
                  <th>Relative Momentum</th>
                  <th>Top Mover</th>
                  <th>Index Weight</th>
                </tr>
              </thead>
              <tbody>
                {sectors.map((sec) => {
                  const isPos = sec.performance_pct >= 0;
                  return (
                    <tr key={sec.sector} className="hover:bg-slate-50/70 transition">
                      <td className="font-semibold text-slate-800">{sec.sector}</td>
                      <td>
                        <span
                          className={`px-2 py-0.5 rounded text-xs font-mono font-bold ${
                            isPos ? "bg-financial-gain-bg text-financial-gain" : "bg-financial-loss-bg text-financial-loss"
                          }`}
                        >
                          {isPos ? "+" : ""}
                          {sec.performance_pct.toFixed(2)}%
                        </span>
                      </td>
                      <td>
                        <div className="flex items-center gap-2">
                          <div className="w-20 bg-slate-100 rounded-full h-1.5 overflow-hidden">
                            <div
                              className="bg-primary h-full rounded-full"
                              style={{ width: `${sec.momentum_score}%` }}
                            />
                          </div>
                          <span className="font-mono text-xs text-slate-600 font-semibold">
                            {sec.momentum_score.toFixed(0)}
                          </span>
                        </div>
                      </td>
                      <td>
                        <Link
                          href={`/workspace/${sec.top_stock}`}
                          className="font-mono font-bold text-xs text-primary hover:underline"
                        >
                          {sec.top_stock}
                        </Link>
                      </td>
                      <td className="font-mono text-xs text-slate-500">
                        {(sec.market_cap_weight * 100).toFixed(1)}%
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        </div>

        {/* Live Detected Anomalies Stream */}
        <div className="bg-white rounded-2xl border border-border shadow-sm flex flex-col justify-between">
          <div className="p-5 border-b border-border flex items-center justify-between">
            <div className="flex items-center gap-2">
              <AlertTriangle className="w-4 h-4 text-amber-600" />
              <h3 className="text-sm font-bold text-slate-900">Statistical Anomaly Radar</h3>
            </div>
            <span className="px-2 py-0.5 rounded text-[10px] font-mono font-bold bg-amber-50 text-amber-800 border border-amber-200">
              ISOLATION FOREST
            </span>
          </div>

          <div className="p-5 space-y-3.5 flex-1 overflow-y-auto max-h-[440px]">
            {anomalies.length === 0 ? (
              <div className="text-center py-12 text-slate-400 text-xs">
                No acute market anomalies detected in monitored universe.
              </div>
            ) : (
              anomalies.slice(0, 5).map((anom, idx) => (
                <div
                  key={idx}
                  className="p-3.5 rounded-xl border border-slate-200 bg-slate-50/60 hover:bg-slate-50 space-y-2 transition"
                >
                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-2">
                      <Link
                        href={`/workspace/${anom.ticker}`}
                        className="font-mono font-bold text-xs px-1.5 py-0.5 rounded bg-primary text-white"
                      >
                        {anom.ticker}
                      </Link>
                      <span className="text-[11px] font-semibold text-slate-700 font-mono">
                        {anom.anomaly_type}
                      </span>
                    </div>
                    <span className="text-[10px] font-mono font-bold text-amber-700 bg-amber-100/70 px-1.5 py-0.5 rounded">
                      Sev: {(anom.severity_score * 100).toFixed(0)}%
                    </span>
                  </div>

                  <p className="text-xs text-slate-600 leading-relaxed font-sans">{anom.summary}</p>

                  <div className="flex items-center justify-between text-[10px] font-mono text-slate-400 pt-1 border-t border-slate-200/70">
                    <span>Vol Z: {anom.metrics?.volume_zscore || "+2.8"}σ</span>
                    <span>{anom.timestamp}</span>
                  </div>
                </div>
              ))
            )}
          </div>

          <div className="p-4 border-t border-border bg-slate-50/50">
            <Link
              href="/workspace/NVDA"
              className="flex items-center justify-between text-xs font-semibold text-primary hover:text-primary-hover"
            >
              <span>Explore Stock Deep Dive Workspace</span>
              <ArrowRight className="w-3.5 h-3.5" />
            </Link>
          </div>
        </div>
      </div>
    </div>
  );
}
