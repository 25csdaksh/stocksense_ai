"use client";

import React, { useEffect, useState } from "react";
import Link from "next/link";
import { Activity, ShieldAlert, Cpu, Sparkles, TrendingUp, Radio } from "lucide-react";
import { MarketIndex } from "@/types";

export default function Navbar() {
  const [indices, setIndices] = useState<MarketIndex[]>([
    { symbol: "^GSPC", name: "S&P 500", price: 5742.10, change: +24.30, change_pct: +0.43 },
    { symbol: "^IXIC", name: "NASDAQ", price: 18120.40, change: +142.10, change_pct: +0.79 },
    { symbol: "^TNX", name: "10Y Yield", price: 4.18, change: -0.04, change_pct: -0.95 },
    { symbol: "^VIX", name: "VIX", price: 14.85, change: -0.62, change_pct: -4.01 },
  ]);

  return (
    <header className="sticky top-0 z-40 w-full bg-white border-b border-border shadow-sm">
      {/* Top Ticker Marquee */}
      <div className="bg-surface-subtle border-b border-border-subtle px-4 py-1.5 flex items-center justify-between text-xs">
        <div className="flex items-center gap-6 overflow-x-auto no-scrollbar">
          <div className="flex items-center gap-1.5 font-semibold text-primary">
            <Radio className="w-3.5 h-3.5 text-financial-gain animate-pulse" />
            <span className="uppercase tracking-wider font-mono text-[11px]">MARKET STREAM</span>
          </div>
          {indices.map((idx) => {
            const isPos = idx.change_pct >= 0;
            return (
              <div key={idx.symbol} className="flex items-center gap-2 font-mono whitespace-nowrap">
                <span className="text-slate-500 font-medium">{idx.name}</span>
                <span className="font-semibold text-slate-800">${idx.price.toLocaleString()}</span>
                <span
                  className={`px-1.5 py-0.5 rounded text-[10px] font-bold ${
                    isPos ? "bg-financial-gain-bg text-financial-gain" : "bg-financial-loss-bg text-financial-loss"
                  }`}
                >
                  {isPos ? "+" : ""}
                  {idx.change_pct.toFixed(2)}%
                </span>
              </div>
            );
          })}
        </div>

        <div className="hidden md:flex items-center gap-2 text-slate-500">
          <span className="inline-flex items-center px-2 py-0.5 rounded-full text-[10px] font-semibold bg-emerald-50 text-emerald-700 border border-emerald-200">
            ● SYSTEM ACTIVE
          </span>
          <span className="text-[11px] font-mono text-slate-400">UTC {new Date().toISOString().substring(11, 19)}</span>
        </div>
      </div>

      {/* Main Navigation Bar */}
      <div className="px-6 h-14 flex items-center justify-between">
        <div className="flex items-center gap-8">
          <Link href="/" className="flex items-center gap-2.5">
            <div className="w-8 h-8 rounded-lg bg-primary flex items-center justify-center text-white shadow-sm font-bold text-lg font-mono">
              M
            </div>
            <div>
              <div className="flex items-center gap-2">
                <span className="font-extrabold text-slate-900 tracking-tight text-lg">MARKETMIND</span>
                <span className="px-1.5 py-0.5 rounded text-[10px] font-bold bg-gold-light text-gold-dark border border-gold-border tracking-wider font-mono">
                  AI v1.0
                </span>
              </div>
              <p className="text-[10px] text-slate-600 font-medium tracking-wide">
                Stock Market Intelligence & Scenario Analysis Platform
              </p>
            </div>
          </Link>
        </div>

        {/* Global Action / Disclaimer Pill */}
        <div className="flex items-center gap-3">
          <div className="hidden lg:flex items-center gap-2 px-3 py-1 rounded-md bg-amber-50/80 border border-amber-200/80 text-amber-900 text-xs">
            <ShieldAlert className="w-3.5 h-3.5 text-amber-700 shrink-0" />
            <span className="text-[11px] font-medium">Academic & Quantitative Research Platform — Non-Advisory</span>
          </div>

          <Link
            href="/research"
            className="flex items-center gap-1.5 px-3.5 py-1.5 rounded-lg bg-primary hover:bg-primary-hover text-white text-xs font-semibold shadow-sm transition"
          >
            <Sparkles className="w-3.5 h-3.5 text-gold" />
            <span>AI Co-Pilot</span>
          </Link>
        </div>
      </div>
    </header>
  );
}
