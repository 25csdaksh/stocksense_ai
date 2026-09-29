"use client";

import React, { useState, useEffect } from "react";
import {
  ShieldCheck,
  Plus,
  Trash2,
  RefreshCw,
  TrendingDown,
  DollarSign,
  PieChart,
  ShieldAlert,
} from "lucide-react";
import { api } from "@/lib/api";

interface Holding {
  ticker: string;
  shares: number;
  price: number;
  sector: string;
  beta: number;
}

export default function PortfolioPage() {
  const [holdings, setHoldings] = useState<Holding[]>([
    { ticker: "AAPL", shares: 50, price: 224.50, sector: "Information Technology", beta: 1.12 },
    { ticker: "NVDA", shares: 80, price: 121.40, sector: "Information Technology", beta: 1.68 },
    { ticker: "MSFT", shares: 40, price: 428.10, sector: "Information Technology", beta: 0.95 },
    { ticker: "JPM", shares: 60, price: 218.40, sector: "Financials", beta: 1.08 },
    { ticker: "SPY", shares: 30, price: 570.20, sector: "Index ETF", beta: 1.00 },
  ]);

  const [stressResults, setStressResults] = useState<any>(null);
  const [loading, setLoading] = useState(false);

  const totalValue = holdings.reduce((sum, h) => sum + h.shares * h.price, 0);

  const weightedBeta =
    totalValue > 0
      ? holdings.reduce((sum, h) => sum + (h.shares * h.price * h.beta) / totalValue, 0)
      : 1.0;

  const runStressTest = async () => {
    setLoading(true);
    try {
      const res = await api.stressTestPortfolio(holdings);
      setStressResults(res);
    } catch (err) {
      console.error("Portfolio stress test failed:", err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    runStressTest();
  }, []);

  const handleRemoveHolding = (index: number) => {
    const updated = holdings.filter((_, idx) => idx !== index);
    setHoldings(updated);
  };

  const handleAddHolding = () => {
    setHoldings([
      ...holdings,
      { ticker: "AMZN", shares: 25, price: 186.50, sector: "Consumer Discretionary", beta: 1.25 },
    ]);
  };

  return (
    <div className="space-y-6 max-w-7xl mx-auto">
      {/* Header Bar */}
      <div className="bg-white p-6 rounded-2xl border border-border shadow-sm flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <div className="flex items-center gap-2 mb-1">
            <ShieldCheck className="w-5 h-5 text-primary" />
            <h1 className="text-2xl font-black text-slate-900 tracking-tight font-mono">
              Portfolio Risk & Crisis Stress Testing
            </h1>
          </div>
          <p className="text-xs text-slate-500">
            Multi-asset portfolio risk decomposition, factor exposure modeling, and systemic crisis drawdown replay.
          </p>
        </div>

        <button
          onClick={runStressTest}
          disabled={loading}
          className="flex items-center gap-2 px-4 py-2 rounded-xl bg-primary hover:bg-primary-hover disabled:opacity-50 text-white text-xs font-bold shadow-sm transition"
        >
          {loading ? (
            <RefreshCw className="w-4 h-4 animate-spin" />
          ) : (
            <RefreshCw className="w-4 h-4 text-gold" />
          )}
          <span>Recompute Portfolio Risk</span>
        </button>
      </div>

      {/* Top Metrics Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
        <div className="bg-white p-5 rounded-xl border border-border shadow-sm">
          <span className="text-xs font-semibold text-slate-500">Total Portfolio Value</span>
          <div className="text-3xl font-black font-mono text-slate-900 mt-2">
            ${totalValue.toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 })}
          </div>
          <div className="text-[11px] text-slate-400 font-mono mt-1">{holdings.length} Active Positions</div>
        </div>

        <div className="bg-white p-5 rounded-xl border border-border shadow-sm">
          <span className="text-xs font-semibold text-slate-500">Portfolio Weighted Beta</span>
          <div className="text-3xl font-black font-mono text-primary mt-2">
            {weightedBeta.toFixed(2)}x
          </div>
          <div className="text-[11px] text-slate-400 font-mono mt-1">Relative to S&P 500</div>
        </div>

        <div className="bg-white p-5 rounded-xl border border-border shadow-sm">
          <span className="text-xs font-semibold text-slate-500">Parametric VaR (95% Daily)</span>
          <div className="text-3xl font-black font-mono text-financial-loss mt-2">
            -{(weightedBeta * 1.65 * 1.15).toFixed(2)}%
          </div>
          <div className="text-[11px] text-slate-400 font-mono mt-1">1-Day Value at Risk</div>
        </div>
      </div>

      {/* Holdings Editor Table */}
      <div className="bg-white rounded-2xl border border-border shadow-sm overflow-hidden">
        <div className="p-5 border-b border-border flex items-center justify-between">
          <h3 className="text-sm font-bold text-slate-900">Custom Portfolio Composition</h3>
          <button
            onClick={handleAddHolding}
            className="flex items-center gap-1.5 px-3 py-1 rounded-lg bg-surface hover:bg-slate-200 text-slate-700 text-xs font-bold border border-border transition"
          >
            <Plus className="w-3.5 h-3.5 text-primary" />
            <span>Add Position</span>
          </button>
        </div>

        <div className="overflow-x-auto">
          <table className="w-full text-left financial-table">
            <thead>
              <tr>
                <th>Ticker</th>
                <th>Shares</th>
                <th>Price</th>
                <th>Position Value</th>
                <th>Weight (%)</th>
                <th>Sector</th>
                <th>Beta</th>
                <th>Action</th>
              </tr>
            </thead>
            <tbody>
              {holdings.map((h, idx) => {
                const posVal = h.shares * h.price;
                const weight = totalValue > 0 ? (posVal / totalValue) * 100 : 0;
                return (
                  <tr key={idx} className="hover:bg-slate-50/70 transition">
                    <td className="font-mono font-bold text-primary">{h.ticker}</td>
                    <td className="font-mono">{h.shares}</td>
                    <td className="font-mono">${h.price.toFixed(2)}</td>
                    <td className="font-mono font-bold">${posVal.toLocaleString(undefined, { minimumFractionDigits: 2 })}</td>
                    <td className="font-mono">{weight.toFixed(1)}%</td>
                    <td className="text-slate-600">{h.sector}</td>
                    <td className="font-mono">{h.beta.toFixed(2)}</td>
                    <td>
                      <button
                        onClick={() => handleRemoveHolding(idx)}
                        className="text-slate-400 hover:text-financial-loss transition p-1"
                      >
                        <Trash2 className="w-4 h-4" />
                      </button>
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      </div>

      {/* Historical Stress Crisis Replay for the Portfolio */}
      {stressResults?.scenario_impacts && (
        <div className="bg-white p-6 rounded-2xl border border-border shadow-sm space-y-4">
          <div className="flex items-center justify-between pb-3 border-b border-border">
            <div>
              <h3 className="text-sm font-bold text-slate-900">
                Portfolio Crisis Drawdown Projections
              </h3>
              <p className="text-xs text-slate-500">
                Simulated portfolio loss across historical crisis drawdowns
              </p>
            </div>
            <span className="text-[10px] font-mono font-bold bg-amber-50 text-amber-800 border border-amber-200 px-2 py-0.5 rounded">
              BETA-ADJUSTED STRESS MODEL
            </span>
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
            {Object.entries(stressResults.scenario_impacts).map(([key, item]: [string, any]) => (
              <div
                key={key}
                className="p-4 rounded-xl border border-slate-200 bg-slate-50/70 space-y-2 flex flex-col justify-between"
              >
                <div>
                  <div className="flex items-center justify-between">
                    <h4 className="font-bold text-slate-900 text-xs truncate">{item.scenario_name}</h4>
                    <span className="px-1.5 py-0.5 rounded text-[11px] font-mono font-bold bg-financial-loss-bg text-financial-loss">
                      {item.portfolio_drawdown_pct.toFixed(1)}%
                    </span>
                  </div>
                  <div className="text-xs font-mono text-slate-500 mt-2">
                    Stressed Value: ${item.stressed_value.toLocaleString(undefined, { minimumFractionDigits: 0, maximumFractionDigits: 0 })}
                  </div>
                </div>

                <div className="pt-2 border-t border-slate-200 flex justify-between items-center text-xs font-mono">
                  <span className="text-slate-500 font-sans">Est. Loss:</span>
                  <span className="font-bold text-financial-loss">
                    -${item.dollar_drawdown.toLocaleString(undefined, { minimumFractionDigits: 0, maximumFractionDigits: 0 })}
                  </span>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Academic Disclaimer */}
      <div className="p-4 bg-amber-50/80 border border-amber-200/80 rounded-xl text-amber-900 text-xs flex items-center gap-3">
        <ShieldAlert className="w-5 h-5 text-amber-700 shrink-0" />
        <p className="leading-relaxed">
          <strong>Academic & Analytical Notice:</strong> Portfolio stress testing models provide mathematical approximations of systemic asset contagion. Actual market drawdowns can vary based on market liquidity, correlation regime breakdown, and unexpected macro shifts.
        </p>
      </div>
    </div>
  );
}
