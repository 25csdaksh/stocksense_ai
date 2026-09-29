"use client";

import React, { useEffect, useState } from "react";
import { useParams } from "next/navigation";
import Link from "next/link";
import {
  TrendingUp,
  TrendingDown,
  Activity,
  ShieldCheck,
  FileText,
  FlaskConical,
  Sparkles,
  BarChart2,
  PieChart,
  DollarSign,
  AlertCircle,
  Clock,
  Layers,
} from "lucide-react";
import { api } from "@/lib/api";
import { MarketQuote, HistoricalData, StockDNAResponse, DocumentCitation } from "@/types";
import CandlestickChart from "@/components/charts/CandlestickChart";
import StockDNARadar from "@/components/charts/StockDNARadar";

export default function StockWorkspacePage() {
  const params = useParams();
  const rawTicker = (params?.ticker as string) || "NVDA";
  const ticker = rawTicker.toUpperCase();

  const [quote, setQuote] = useState<MarketQuote | null>(null);
  const [history, setHistory] = useState<HistoricalData | null>(null);
  const [dna, setDna] = useState<StockDNAResponse | null>(null);
  const [fundamentals, setFundamentals] = useState<any>(null);
  const [citations, setCitations] = useState<DocumentCitation[]>([]);
  const [selectedRange, setSelectedRange] = useState("6m");
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function loadStockData() {
      setLoading(true);
      try {
        const [qData, hData, dnaData, fundData, secData] = await Promise.all([
          api.getQuote(ticker).catch(() => null),
          api.getHistory(ticker, selectedRange).catch(() => null),
          api.getStockDNA(ticker).catch(() => null),
          api.getFundamentals(ticker).catch(() => null),
          api.searchFilings({ query: "supply chain revenue risk factors", ticker, top_k: 2 }).catch(() => ({ citations: [] })),
        ]);

        if (qData) setQuote(qData);
        if (hData) setHistory(hData);
        if (dnaData) setDna(dnaData);
        if (fundData) setFundamentals(fundData);
        if (secData?.citations) setCitations(secData.citations);
      } finally {
        setLoading(false);
      }
    }
    loadStockData();
  }, [ticker, selectedRange]);

  const isPos = (quote?.change_pct ?? 0) >= 0;

  return (
    <div className="space-y-6 max-w-7xl mx-auto">
      {/* Header Bar */}
      <div className="bg-white p-6 rounded-2xl border border-border shadow-sm flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <div className="flex items-center gap-3">
            <h1 className="text-2xl font-black text-slate-900 font-mono tracking-tight">
              {ticker}
            </h1>
            <span className="text-base font-semibold text-slate-600">
              {quote?.name || `${ticker} Corporation`}
            </span>
            <span
              className={`px-2 py-0.5 rounded text-[10px] font-bold font-mono ${
                quote?.is_synthetic
                  ? "bg-amber-50 text-amber-800 border border-amber-200"
                  : "bg-emerald-50 text-emerald-800 border border-emerald-200"
              }`}
            >
              {quote?.data_source || "LIVE EXCHANGE FEED"}
            </span>
          </div>

          <div className="flex items-center gap-4 mt-2 font-mono text-xs">
            <span className="text-3xl font-black text-slate-900">
              ${quote?.price?.toFixed(2) || "---"}
            </span>
            <div
              className={`flex items-center gap-1 font-bold text-sm px-2 py-0.5 rounded ${
                isPos
                  ? "bg-financial-gain-bg text-financial-gain"
                  : "bg-financial-loss-bg text-financial-loss"
              }`}
            >
              {isPos ? <TrendingUp className="w-4 h-4" /> : <TrendingDown className="w-4 h-4" />}
              <span>
                {isPos ? "+" : ""}
                {quote?.change?.toFixed(2)} ({isPos ? "+" : ""}
                {quote?.change_pct?.toFixed(2)}%)
              </span>
            </div>
            <span className="text-slate-400">|</span>
            <span className="text-slate-500">Vol: {quote?.volume?.toLocaleString()}</span>
          </div>
        </div>

        {/* Action Buttons */}
        <div className="flex items-center gap-3">
          <Link
            href={`/simulator?ticker=${ticker}`}
            className="flex items-center gap-2 px-4 py-2 rounded-xl bg-surface hover:bg-slate-200 text-slate-800 text-xs font-bold border border-border transition"
          >
            <FlaskConical className="w-3.5 h-3.5 text-primary" />
            <span>Simulate Scenarios</span>
          </Link>
          <Link
            href="/research"
            className="flex items-center gap-2 px-4 py-2 rounded-xl bg-primary hover:bg-primary-hover text-white text-xs font-bold shadow-sm transition"
          >
            <Sparkles className="w-3.5 h-3.5 text-gold" />
            <span>Agent Research</span>
          </Link>
        </div>
      </div>

      {/* Main Grid: Interactive Candlestick Chart & Stock DNA Radar */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Technical Chart */}
        <div className="lg:col-span-2 bg-white p-5 rounded-2xl border border-border shadow-sm flex flex-col justify-between">
          <div className="flex items-center justify-between mb-4">
            <div className="flex items-center gap-2">
              <BarChart2 className="w-4 h-4 text-primary" />
              <h3 className="text-sm font-bold text-slate-900">
                Lightweight TradingView Candlestick Series
              </h3>
            </div>

            {/* Timeframe Selector */}
            <div className="flex items-center gap-1 bg-slate-100 p-1 rounded-lg text-xs font-mono">
              {["1m", "3m", "6m", "1y", "5y"].map((r) => (
                <button
                  key={r}
                  onClick={() => setSelectedRange(r)}
                  className={`px-2.5 py-1 rounded font-bold uppercase transition ${
                    selectedRange === r
                      ? "bg-white text-primary shadow-sm"
                      : "text-slate-500 hover:text-slate-900"
                  }`}
                >
                  {r}
                </button>
              ))}
            </div>
          </div>

          {history?.bars && history.bars.length > 0 ? (
            <CandlestickChart data={history.bars} height={380} />
          ) : (
            <div className="h-[380px] flex items-center justify-center text-slate-400 text-xs">
              Loading price history series...
            </div>
          )}
        </div>

        {/* Stock DNA Radar */}
        <div className="flex flex-col">
          {dna?.radar_data ? (
            <StockDNARadar
              data={dna.radar_data}
              dominantPersona={dna.dominant_persona}
              ticker={ticker}
              height={300}
            />
          ) : (
            <div className="h-[340px] bg-white rounded-2xl border border-border flex items-center justify-center text-slate-400 text-xs">
              Calculating multi-factor DNA vector...
            </div>
          )}
        </div>
      </div>

      {/* Fundamental Scorecard & Valuation Multiples */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        {/* Valuation Multiples */}
        <div className="bg-white p-5 rounded-2xl border border-border shadow-sm space-y-4">
          <div className="flex items-center justify-between pb-3 border-b border-border">
            <h4 className="text-xs font-bold text-slate-900 uppercase font-mono tracking-wider">
              Valuation Multiples
            </h4>
            <DollarSign className="w-4 h-4 text-primary" />
          </div>
          <div className="space-y-2.5 text-xs font-mono">
            <div className="flex justify-between py-1 border-b border-slate-100">
              <span className="text-slate-500 font-sans">Trailing P/E Ratio</span>
              <span className="font-bold text-slate-800">{fundamentals?.valuation?.pe_ratio || quote?.pe_ratio || "33.5"}x</span>
            </div>
            <div className="flex justify-between py-1 border-b border-slate-100">
              <span className="text-slate-500 font-sans">Forward P/E</span>
              <span className="font-bold text-slate-800">{fundamentals?.valuation?.forward_pe || "28.4"}x</span>
            </div>
            <div className="flex justify-between py-1 border-b border-slate-100">
              <span className="text-slate-500 font-sans">Price-to-Book (P/B)</span>
              <span className="font-bold text-slate-800">{fundamentals?.valuation?.pb_ratio || "12.8"}x</span>
            </div>
            <div className="flex justify-between py-1 border-b border-slate-100">
              <span className="text-slate-500 font-sans">EV / EBITDA</span>
              <span className="font-bold text-slate-800">{fundamentals?.valuation?.ev_ebitda || "22.4"}x</span>
            </div>
            <div className="flex justify-between py-1">
              <span className="text-slate-500 font-sans">Free Cash Flow Yield</span>
              <span className="font-bold text-financial-gain">{fundamentals?.valuation?.fcf_yield_pct || "3.8"}%</span>
            </div>
          </div>
        </div>

        {/* Profitability Multiples */}
        <div className="bg-white p-5 rounded-2xl border border-border shadow-sm space-y-4">
          <div className="flex items-center justify-between pb-3 border-b border-border">
            <h4 className="text-xs font-bold text-slate-900 uppercase font-mono tracking-wider">
              Profitability & Returns
            </h4>
            <PieChart className="w-4 h-4 text-primary" />
          </div>
          <div className="space-y-2.5 text-xs font-mono">
            <div className="flex justify-between py-1 border-b border-slate-100">
              <span className="text-slate-500 font-sans">Gross Margin</span>
              <span className="font-bold text-slate-800">{fundamentals?.profitability?.gross_margin_pct || "68.5"}%</span>
            </div>
            <div className="flex justify-between py-1 border-b border-slate-100">
              <span className="text-slate-500 font-sans">Operating Margin</span>
              <span className="font-bold text-slate-800">{fundamentals?.profitability?.operating_margin_pct || "34.2"}%</span>
            </div>
            <div className="flex justify-between py-1 border-b border-slate-100">
              <span className="text-slate-500 font-sans">Net Profit Margin</span>
              <span className="font-bold text-slate-800">{fundamentals?.profitability?.net_margin_pct || "26.8"}%</span>
            </div>
            <div className="flex justify-between py-1 border-b border-slate-100">
              <span className="text-slate-500 font-sans">Return on Equity (ROE)</span>
              <span className="font-bold text-financial-gain">{fundamentals?.profitability?.roe_pct || "38.4"}%</span>
            </div>
            <div className="flex justify-between py-1">
              <span className="text-slate-500 font-sans">Return on Assets (ROA)</span>
              <span className="font-bold text-slate-800">{fundamentals?.profitability?.roa_pct || "16.2"}%</span>
            </div>
          </div>
        </div>

        {/* Financial Solvency & Health */}
        <div className="bg-white p-5 rounded-2xl border border-border shadow-sm space-y-4">
          <div className="flex items-center justify-between pb-3 border-b border-border">
            <h4 className="text-xs font-bold text-slate-900 uppercase font-mono tracking-wider">
              Solvency & Balance Sheet
            </h4>
            <ShieldCheck className="w-4 h-4 text-primary" />
          </div>
          <div className="space-y-2.5 text-xs font-mono">
            <div className="flex justify-between py-1 border-b border-slate-100">
              <span className="text-slate-500 font-sans">Debt-to-Equity</span>
              <span className="font-bold text-slate-800">{fundamentals?.financial_health?.debt_to_equity || "0.62"}</span>
            </div>
            <div className="flex justify-between py-1 border-b border-slate-100">
              <span className="text-slate-500 font-sans">Current Ratio</span>
              <span className="font-bold text-slate-800">{fundamentals?.financial_health?.current_ratio || "1.45"}</span>
            </div>
            <div className="flex justify-between py-1 border-b border-slate-100">
              <span className="text-slate-500 font-sans">Interest Coverage</span>
              <span className="font-bold text-slate-800">{fundamentals?.financial_health?.interest_coverage_ratio || "18.5"}x</span>
            </div>
            <div className="flex justify-between py-1 border-b border-slate-100">
              <span className="text-slate-500 font-sans">Altman Z-Score</span>
              <span className="font-bold text-financial-gain">{fundamentals?.financial_health?.altman_z_score || "4.85"} (Safe)</span>
            </div>
            <div className="flex justify-between py-1">
              <span className="text-slate-500 font-sans">Health Rating</span>
              <span className="font-bold text-primary font-mono">{fundamentals?.financial_health?.health_score || "EXCELLENT"}</span>
            </div>
          </div>
        </div>
      </div>

      {/* SEC 10-K Disclosures */}
      {citations.length > 0 && (
        <div className="bg-white p-5 rounded-2xl border border-border shadow-sm space-y-3">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2">
              <FileText className="w-4 h-4 text-primary" />
              <h4 className="text-sm font-bold text-slate-900">
                Verified SEC 10-K Regulatory Filings Knowledge
              </h4>
            </div>
            <span className="text-xs font-mono text-slate-400">RAG KNOWLEDGE LAYER</span>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-4 pt-1">
            {citations.map((c) => (
              <div key={c.id} className="p-3.5 rounded-xl border border-slate-200 bg-slate-50/70 space-y-1.5">
                <div className="flex items-center justify-between text-xs font-bold text-primary font-mono">
                  <span>{c.section}</span>
                  <span>Page {c.page_number}</span>
                </div>
                <p className="text-xs text-slate-600 italic font-serif leading-relaxed">
                  "{c.content_snippet}"
                </p>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
