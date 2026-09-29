"use client";

import React, { useState, useEffect } from "react";
import { useSearchParams } from "next/navigation";
import {
  FlaskConical,
  Play,
  Sliders,
  TrendingDown,
  TrendingUp,
  ShieldAlert,
  History,
  Globe,
  RefreshCw,
} from "lucide-react";
import { api } from "@/lib/api";
import { MonteCarloResult } from "@/types";
import FanChart from "@/components/charts/FanChart";
import DistributionChart from "@/components/charts/DistributionChart";

export default function ScenarioSimulatorPage() {
  const searchParams = useSearchParams();
  const initialTicker = searchParams.get("ticker") || "NVDA";

  const [activeTab, setActiveTab] = useState<"monte_carlo" | "historical" | "macro">("monte_carlo");
  const [ticker, setTicker] = useState(initialTicker);

  // Monte Carlo State
  const [days, setDays] = useState(90);
  const [iterations, setIterations] = useState(5000);
  const [drift, setDrift] = useState(8.0); // %
  const [volatility, setVolatility] = useState(28.0); // %
  const [jumpIntensity, setJumpIntensity] = useState(5.0); // %
  const [mcResult, setMcResult] = useState<MonteCarloResult | null>(null);
  const [mcLoading, setMcLoading] = useState(false);

  // Historical Stress State
  const [histResult, setHistResult] = useState<any>(null);

  // Macro Shock State
  const [rateShock, setRateShock] = useState(100); // bps
  const [inflationShock, setInflationShock] = useState(1.5); // %
  const [oilShock, setOilShock] = useState(20); // %
  const [gdpShock, setGdpShock] = useState(-1.0); // %
  const [macroResult, setMacroResult] = useState<any>(null);

  const runMonteCarlo = async () => {
    setMcLoading(true);
    try {
      const res = await api.runMonteCarlo({
        ticker,
        drift_annualized: drift / 100.0,
        volatility_annualized: volatility / 100.0,
        days: Number(days),
        iterations: Number(iterations),
        jump_intensity: jumpIntensity / 100.0,
      });
      setMcResult(res);
    } catch (err) {
      console.error("Monte Carlo run failed:", err);
    } finally {
      setMcLoading(false);
    }
  };

  const runHistorical = async () => {
    try {
      const res = await api.runHistoricalStress({ ticker });
      setHistResult(res);
    } catch (err) {
      console.error("Historical stress run failed:", err);
    }
  };

  const runMacro = async () => {
    try {
      const res = await api.runMacroShock({
        ticker,
        rate_shock_bps: Number(rateShock),
        inflation_shock_pct: Number(inflationShock),
        oil_shock_pct: Number(oilShock),
        gdp_shock_pct: Number(gdpShock),
      });
      setMacroResult(res);
    } catch (err) {
      console.error("Macro shock run failed:", err);
    }
  };

  useEffect(() => {
    runMonteCarlo();
    runHistorical();
    runMacro();
  }, [ticker]);

  return (
    <div className="space-y-6 max-w-7xl mx-auto">
      {/* Header Bar */}
      <div className="bg-white p-6 rounded-2xl border border-border shadow-sm flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <div className="flex items-center gap-2 mb-1">
            <FlaskConical className="w-5 h-5 text-primary" />
            <h1 className="text-2xl font-black text-slate-900 tracking-tight font-mono">
              Quantitative Scenario Simulator
            </h1>
          </div>
          <p className="text-xs text-slate-500">
            Simulate Jump-Diffusion Monte Carlo paths, replay historical liquidity crises, and model macroeconomic factor shocks.
          </p>
        </div>

        {/* Ticker Selector */}
        <div className="flex items-center gap-2">
          <span className="text-xs font-bold text-slate-500 uppercase font-mono">ASSET:</span>
          <select
            value={ticker}
            onChange={(e) => setTicker(e.target.value)}
            className="px-3 py-1.5 rounded-lg border border-border bg-surface text-slate-900 font-mono font-bold text-xs focus:outline-none focus:ring-2 focus:ring-primary/40"
          >
            {["AAPL", "MSFT", "NVDA", "GOOGL", "AMZN", "TSLA", "JPM", "SPY", "QQQ"].map((t) => (
              <option key={t} value={t}>
                {t}
              </option>
            ))}
          </select>
        </div>
      </div>

      {/* Tab Switcher */}
      <div className="flex items-center gap-2 border-b border-border pb-3">
        <button
          onClick={() => setActiveTab("monte_carlo")}
          className={`px-4 py-2 rounded-xl text-xs font-bold transition flex items-center gap-2 ${
            activeTab === "monte_carlo"
              ? "bg-primary text-white shadow-sm"
              : "bg-white text-slate-600 hover:bg-surface border border-border"
          }`}
        >
          <Sliders className="w-3.5 h-3.5" />
          <span>Merton Jump Diffusion Monte Carlo</span>
        </button>
        <button
          onClick={() => setActiveTab("historical")}
          className={`px-4 py-2 rounded-xl text-xs font-bold transition flex items-center gap-2 ${
            activeTab === "historical"
              ? "bg-primary text-white shadow-sm"
              : "bg-white text-slate-600 hover:bg-surface border border-border"
          }`}
        >
          <History className="w-3.5 h-3.5" />
          <span>Historical Crisis Replay</span>
        </button>
        <button
          onClick={() => setActiveTab("macro")}
          className={`px-4 py-2 rounded-xl text-xs font-bold transition flex items-center gap-2 ${
            activeTab === "macro"
              ? "bg-primary text-white shadow-sm"
              : "bg-white text-slate-600 hover:bg-surface border border-border"
          }`}
        >
          <Globe className="w-3.5 h-3.5" />
          <span>Macroeconomic Factor Shocks</span>
        </button>
      </div>

      {/* TAB 1: MONTE CARLO SIMULATOR */}
      {activeTab === "monte_carlo" && (
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Controls Panel */}
          <div className="bg-white p-5 rounded-2xl border border-border shadow-sm space-y-5">
            <div className="flex items-center justify-between pb-3 border-b border-border">
              <h3 className="text-xs font-bold text-slate-900 uppercase tracking-wider font-mono">
                Stochastic Parameters
              </h3>
              <span className="text-[10px] font-mono text-slate-400">GBM + POISSON</span>
            </div>

            {/* Parameter: Days Horizon */}
            <div className="space-y-1.5">
              <div className="flex justify-between text-xs font-mono">
                <span className="text-slate-600 font-sans">Horizon:</span>
                <span className="font-bold text-slate-900">{days} Days</span>
              </div>
              <input
                type="range"
                min="10"
                max="252"
                step="5"
                value={days}
                onChange={(e) => setDays(Number(e.target.value))}
                className="w-full accent-primary"
              />
            </div>

            {/* Parameter: Iterations */}
            <div className="space-y-1.5">
              <div className="flex justify-between text-xs font-mono">
                <span className="text-slate-600 font-sans">Sample Trajectories:</span>
                <span className="font-bold text-slate-900">{iterations.toLocaleString()} Paths</span>
              </div>
              <input
                type="range"
                min="500"
                max="10000"
                step="500"
                value={iterations}
                onChange={(e) => setIterations(Number(e.target.value))}
                className="w-full accent-primary"
              />
            </div>

            {/* Parameter: Expected Drift (mu) */}
            <div className="space-y-1.5">
              <div className="flex justify-between text-xs font-mono">
                <span className="text-slate-600 font-sans">Annualized Drift (μ):</span>
                <span className="font-bold text-slate-900">{drift > 0 ? `+${drift}` : drift}%</span>
              </div>
              <input
                type="range"
                min="-20"
                max="40"
                step="1"
                value={drift}
                onChange={(e) => setDrift(Number(e.target.value))}
                className="w-full accent-primary"
              />
            </div>

            {/* Parameter: Implied Volatility (sigma) */}
            <div className="space-y-1.5">
              <div className="flex justify-between text-xs font-mono">
                <span className="text-slate-600 font-sans">Annualized Volatility (σ):</span>
                <span className="font-bold text-slate-900">{volatility}%</span>
              </div>
              <input
                type="range"
                min="10"
                max="80"
                step="1"
                value={volatility}
                onChange={(e) => setVolatility(Number(e.target.value))}
                className="w-full accent-primary"
              />
            </div>

            {/* Parameter: Jump Intensity */}
            <div className="space-y-1.5">
              <div className="flex justify-between text-xs font-mono">
                <span className="text-slate-600 font-sans">Jump Frequency (λ):</span>
                <span className="font-bold text-slate-900">{jumpIntensity}%</span>
              </div>
              <input
                type="range"
                min="0"
                max="20"
                step="1"
                value={jumpIntensity}
                onChange={(e) => setJumpIntensity(Number(e.target.value))}
                className="w-full accent-primary"
              />
            </div>

            <button
              onClick={runMonteCarlo}
              disabled={mcLoading}
              className="w-full py-2.5 rounded-xl bg-primary hover:bg-primary-hover disabled:opacity-50 text-white font-bold text-xs flex items-center justify-center gap-2 shadow-sm transition"
            >
              {mcLoading ? (
                <RefreshCw className="w-4 h-4 animate-spin" />
              ) : (
                <Play className="w-4 h-4 text-gold" />
              )}
              <span>Run Monte Carlo Engine</span>
            </button>
          </div>

          {/* Visualization Area */}
          <div className="lg:col-span-2 space-y-6">
            {/* Risk Metrics Cards */}
            {mcResult && (
              <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
                <div className="bg-white p-3.5 rounded-xl border border-border text-center">
                  <div className="text-[11px] text-slate-500 font-semibold">P50 Target (Median)</div>
                  <div className="text-lg font-black font-mono text-primary mt-1">
                    ${mcResult.expected_terminal_price_p50.toFixed(2)}
                  </div>
                </div>
                <div className="bg-white p-3.5 rounded-xl border border-border text-center">
                  <div className="text-[11px] text-slate-500 font-semibold">VaR (95% Confidence)</div>
                  <div className="text-lg font-black font-mono text-financial-loss mt-1">
                    {mcResult.value_at_risk_95_pct.toFixed(2)}%
                  </div>
                </div>
                <div className="bg-white p-3.5 rounded-xl border border-border text-center">
                  <div className="text-[11px] text-slate-500 font-semibold">CVaR (99% Shortfall)</div>
                  <div className="text-lg font-black font-mono text-financial-loss mt-1">
                    {mcResult.cvar_expected_shortfall_99_pct.toFixed(2)}%
                  </div>
                </div>
                <div className="bg-white p-3.5 rounded-xl border border-border text-center">
                  <div className="text-[11px] text-slate-500 font-semibold">Prob. of Profit</div>
                  <div className="text-lg font-black font-mono text-financial-gain mt-1">
                    {mcResult.probability_of_profit_pct.toFixed(1)}%
                  </div>
                </div>
              </div>
            )}

            {/* Fan Chart */}
            {mcResult?.fan_chart && <FanChart data={mcResult.fan_chart} height={340} />}

            {/* Distribution Histogram */}
            {mcResult?.distribution_histogram && (
              <DistributionChart
                data={mcResult.distribution_histogram}
                var95={mcResult.value_at_risk_95_pct}
                height={260}
              />
            )}
          </div>
        </div>
      )}

      {/* TAB 2: HISTORICAL CRISIS REPLAY */}
      {activeTab === "historical" && (
        <div className="bg-white p-6 rounded-2xl border border-border shadow-sm space-y-6">
          <div>
            <h3 className="text-sm font-bold text-slate-900">
              Historical Crisis Stress Testing ({ticker})
            </h3>
            <p className="text-xs text-slate-500">
              Evaluates asset performance and drawdown resilience under major macroeconomic collapse events.
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {histResult?.scenario_results &&
              Object.entries(histResult.scenario_results).map(([key, item]: [string, any]) => (
                <div key={key} className="p-4 rounded-xl border border-slate-200 bg-slate-50/70 space-y-3">
                  <div className="flex items-center justify-between">
                    <div>
                      <h4 className="font-bold text-slate-900 text-sm">{item.scenario_name}</h4>
                      <span className="text-[10px] font-mono text-slate-500">{item.period}</span>
                    </div>
                    <span className="px-2 py-0.5 rounded text-xs font-mono font-bold bg-financial-loss-bg text-financial-loss">
                      {item.projected_drawdown_pct.toFixed(1)}%
                    </span>
                  </div>

                  <p className="text-xs text-slate-600 leading-relaxed font-sans">{item.description}</p>

                  <div className="grid grid-cols-2 gap-2 pt-2 border-t border-slate-200 text-xs font-mono">
                    <div>
                      <span className="text-slate-400 block text-[10px]">Stressed Price</span>
                      <span className="font-bold text-slate-800">${item.stressed_price.toFixed(2)}</span>
                    </div>
                    <div>
                      <span className="text-slate-400 block text-[10px]">Est. Dollar Drawdown</span>
                      <span className="font-bold text-financial-loss">-${item.estimated_loss_per_share.toFixed(2)}</span>
                    </div>
                  </div>
                </div>
              ))}
          </div>
        </div>
      )}

      {/* TAB 3: MACROECONOMIC FACTOR SHOCKS */}
      {activeTab === "macro" && (
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Shock Parameter Sliders */}
          <div className="bg-white p-5 rounded-2xl border border-border shadow-sm space-y-5">
            <h3 className="text-xs font-bold text-slate-900 uppercase tracking-wider font-mono pb-3 border-b border-border">
              Macro Factor Adjusters
            </h3>

            {/* Interest Rates Shock */}
            <div className="space-y-1.5">
              <div className="flex justify-between text-xs font-mono">
                <span className="text-slate-600 font-sans">Interest Rate Shift:</span>
                <span className="font-bold text-slate-900">
                  {rateShock > 0 ? `+${rateShock}` : rateShock} bps
                </span>
              </div>
              <input
                type="range"
                min="-200"
                max="300"
                step="25"
                value={rateShock}
                onChange={(e) => setRateShock(Number(e.target.value))}
                className="w-full accent-primary"
              />
            </div>

            {/* Inflation Shock */}
            <div className="space-y-1.5">
              <div className="flex justify-between text-xs font-mono">
                <span className="text-slate-600 font-sans">CPI Inflation Shock:</span>
                <span className="font-bold text-slate-900">
                  {inflationShock > 0 ? `+${inflationShock}` : inflationShock}%
                </span>
              </div>
              <input
                type="range"
                min="-3"
                max="6"
                step="0.5"
                value={inflationShock}
                onChange={(e) => setInflationShock(Number(e.target.value))}
                className="w-full accent-primary"
              />
            </div>

            {/* Crude Oil Shock */}
            <div className="space-y-1.5">
              <div className="flex justify-between text-xs font-mono">
                <span className="text-slate-600 font-sans">Crude Oil Spike:</span>
                <span className="font-bold text-slate-900">
                  {oilShock > 0 ? `+${oilShock}` : oilShock}%
                </span>
              </div>
              <input
                type="range"
                min="-40"
                max="60"
                step="5"
                value={oilShock}
                onChange={(e) => setOilShock(Number(e.target.value))}
                className="w-full accent-primary"
              />
            </div>

            {/* GDP Contraction / Expansion */}
            <div className="space-y-1.5">
              <div className="flex justify-between text-xs font-mono">
                <span className="text-slate-600 font-sans">Real GDP Shift:</span>
                <span className="font-bold text-slate-900">{gdpShock > 0 ? `+${gdpShock}` : gdpShock}%</span>
              </div>
              <input
                type="range"
                min="-5"
                max="4"
                step="0.5"
                value={gdpShock}
                onChange={(e) => setGdpShock(Number(e.target.value))}
                className="w-full accent-primary"
              />
            </div>

            <button
              onClick={runMacro}
              className="w-full py-2.5 rounded-xl bg-primary hover:bg-primary-hover text-white font-bold text-xs flex items-center justify-center gap-2 shadow-sm transition"
            >
              <RefreshCw className="w-4 h-4 text-gold" />
              <span>Recompute Macro Impact</span>
            </button>
          </div>

          {/* Macro Impact Analysis */}
          <div className="lg:col-span-2 bg-white p-6 rounded-2xl border border-border shadow-sm space-y-6 flex flex-col justify-between">
            <div>
              <h3 className="text-sm font-bold text-slate-900">Macro Elasticity Decomposition</h3>
              <p className="text-xs text-slate-500">
                Sensitivity factor breakdown for {ticker} under active macro shock parameters.
              </p>
            </div>

            {macroResult && (
              <div className="space-y-4">
                <div className="p-4 rounded-xl bg-slate-50 border border-slate-200 flex items-center justify-between font-mono">
                  <div>
                    <span className="text-xs text-slate-500 font-sans">Projected Asset Price</span>
                    <div className="text-2xl font-black text-slate-900">
                      ${macroResult.projected_price.toFixed(2)}
                    </div>
                  </div>
                  <div className="text-right">
                    <span className="text-xs text-slate-500 font-sans">Total Projected Return</span>
                    <div
                      className={`text-2xl font-black ${
                        macroResult.total_projected_return_pct >= 0
                          ? "text-financial-gain"
                          : "text-financial-loss"
                      }`}
                    >
                      {macroResult.total_projected_return_pct >= 0 ? "+" : ""}
                      {macroResult.total_projected_return_pct.toFixed(2)}%
                    </div>
                  </div>
                </div>

                <div className="space-y-2 text-xs font-mono">
                  <div className="flex justify-between p-2 rounded bg-slate-50">
                    <span className="text-slate-600 font-sans">Interest Rates Impact</span>
                    <span className="font-bold">
                      {macroResult.factor_decomposition.rates_effect_pct.toFixed(2)}%
                    </span>
                  </div>
                  <div className="flex justify-between p-2 rounded bg-slate-50">
                    <span className="text-slate-600 font-sans">Inflation Impact</span>
                    <span className="font-bold">
                      {macroResult.factor_decomposition.inflation_effect_pct.toFixed(2)}%
                    </span>
                  </div>
                  <div className="flex justify-between p-2 rounded bg-slate-50">
                    <span className="text-slate-600 font-sans">Crude Oil Impact</span>
                    <span className="font-bold">
                      {macroResult.factor_decomposition.oil_effect_pct.toFixed(2)}%
                    </span>
                  </div>
                  <div className="flex justify-between p-2 rounded bg-slate-50">
                    <span className="text-slate-600 font-sans">GDP Growth Impact</span>
                    <span className="font-bold">
                      {macroResult.factor_decomposition.gdp_effect_pct.toFixed(2)}%
                    </span>
                  </div>
                </div>
              </div>
            )}

            <div className="p-3 bg-amber-50/80 border border-amber-200/80 rounded-xl text-amber-900 text-xs flex items-center gap-2">
              <ShieldAlert className="w-4 h-4 text-amber-700 shrink-0" />
              <span>
                Macro elasticity models are parametric linear approximations based on historical factor beta matrices.
              </span>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
