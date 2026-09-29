"use client";

import React, { useState } from "react";
import {
  Sparkles,
  Search,
  FileText,
  Bot,
  Layers,
  Database,
  ShieldCheck,
  CheckCircle2,
} from "lucide-react";
import { api } from "@/lib/api";
import { DocumentCitation } from "@/types";
import AgentChatDrawer from "@/components/agent/AgentChatDrawer";

export default function ResearchPage() {
  const [searchQuery, setSearchQuery] = useState("");
  const [selectedTicker, setSelectedTicker] = useState("ALL");
  const [searchResults, setSearchResults] = useState<DocumentCitation[]>([]);
  const [isSearching, setIsSearching] = useState(false);

  const handleSearch = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!searchQuery.trim()) return;

    setIsSearching(true);
    try {
      const res = await api.searchFilings({
        query: searchQuery,
        ticker: selectedTicker === "ALL" ? undefined : selectedTicker,
        top_k: 5,
      });
      setSearchResults(res.citations || []);
    } catch (err) {
      console.error("SEC RAG search error:", err);
    } finally {
      setIsSearching(false);
    }
  };

  return (
    <div className="space-y-6 max-w-7xl mx-auto">
      {/* Header */}
      <div className="bg-white p-6 rounded-2xl border border-border shadow-sm flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <div className="flex items-center gap-2 mb-1">
            <Bot className="w-5 h-5 text-primary" />
            <h1 className="text-2xl font-black text-slate-900 tracking-tight font-mono">
              AI Multi-Agent Studio & RAG Regulatory Search
            </h1>
          </div>
          <p className="text-xs text-slate-500">
            Powered by LangGraph multi-agent orchestration, Google Gemini, and Qdrant semantic vector index across SEC 10-K/10-Q filings.
          </p>
        </div>
        <div className="flex items-center gap-2 text-xs font-mono bg-emerald-50 text-emerald-800 border border-emerald-200 px-3 py-1.5 rounded-xl font-bold">
          <CheckCircle2 className="w-4 h-4 text-emerald-600" />
          <span>RAG KNOWLEDGE INDEX ACTIVE</span>
        </div>
      </div>

      {/* Main Grid: Streaming Agent Drawer & Dedicated SEC 10-K Search */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
        {/* Left: AI Multi-Agent Console (7 cols) */}
        <div className="lg:col-span-7">
          <AgentChatDrawer />
        </div>

        {/* Right: Direct SEC 10-K RAG Search Explorer (5 cols) */}
        <div className="lg:col-span-5 bg-white p-6 rounded-xl border border-border shadow-sm flex flex-col justify-between space-y-4">
          <div>
            <div className="flex items-center justify-between pb-3 border-b border-border mb-4">
              <div className="flex items-center gap-2">
                <FileText className="w-4 h-4 text-primary" />
                <h3 className="text-sm font-bold text-slate-900">
                  SEC Regulatory Filings Search
                </h3>
              </div>
              <span className="text-[10px] font-mono font-bold bg-slate-100 text-slate-600 px-2 py-0.5 rounded">
                DENSE RETRIEVAL
              </span>
            </div>

            {/* Search Input Form */}
            <form onSubmit={handleSearch} className="space-y-3 mb-4">
              <div className="flex gap-2">
                <input
                  type="text"
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  placeholder="e.g. 'foundry TSMC risk', 'cloud gross margin'..."
                  className="flex-1 px-3.5 py-2 text-xs rounded-lg border border-border bg-slate-50 focus:outline-none focus:ring-2 focus:ring-primary/40"
                />
                <select
                  value={selectedTicker}
                  onChange={(e) => setSelectedTicker(e.target.value)}
                  className="px-2.5 py-2 text-xs rounded-lg border border-border bg-slate-50 font-mono font-bold"
                >
                  <option value="ALL">All</option>
                  <option value="AAPL">AAPL</option>
                  <option value="MSFT">MSFT</option>
                  <option value="NVDA">NVDA</option>
                  <option value="GOOGL">GOOGL</option>
                  <option value="TSLA">TSLA</option>
                  <option value="JPM">JPM</option>
                </select>
                <button
                  type="submit"
                  disabled={isSearching || !searchQuery.trim()}
                  className="px-3.5 py-2 rounded-lg bg-primary hover:bg-primary-hover disabled:opacity-50 text-white text-xs font-bold transition"
                >
                  <Search className="w-3.5 h-3.5" />
                </button>
              </div>
            </form>

            {/* Citations List */}
            <div className="space-y-3 overflow-y-auto max-h-[500px]">
              {searchResults.length === 0 ? (
                <div className="text-center py-16 text-slate-400 text-xs space-y-2">
                  <Database className="w-8 h-8 text-slate-300 mx-auto" />
                  <p>Query SEC 10-K disclosures to inspect verbatim citations and page references.</p>
                </div>
              ) : (
                searchResults.map((c) => (
                  <div
                    key={c.id}
                    className="p-3.5 rounded-xl border border-slate-200 bg-slate-50/80 hover:bg-slate-50 space-y-2 transition"
                  >
                    <div className="flex items-center justify-between text-xs font-mono font-bold text-primary">
                      <span>
                        {c.ticker} {c.filing_type} (FY{c.fiscal_year})
                      </span>
                      <span className="text-[10px] bg-slate-200 text-slate-700 px-1.5 py-0.5 rounded">
                        Page {c.page_number}
                      </span>
                    </div>

                    <div className="text-[11px] font-semibold text-slate-700 font-mono">
                      {c.section}
                    </div>

                    <p className="text-xs text-slate-600 italic font-serif leading-relaxed">
                      "{c.content_snippet}"
                    </p>

                    <div className="flex items-center justify-between text-[10px] font-mono text-slate-400 pt-1 border-t border-slate-200">
                      <span>Relevance: {(c.relevance_score * 100).toFixed(1)}%</span>
                      <span>Verified Regulatory Match</span>
                    </div>
                  </div>
                ))
              )}
            </div>
          </div>

          <div className="p-3 bg-slate-50 border border-slate-200 rounded-xl text-[11px] text-slate-500 flex items-center gap-2">
            <ShieldCheck className="w-4 h-4 text-primary shrink-0" />
            <span>
              All regulatory citations are retrieved with exact document hashes and metadata verification.
            </span>
          </div>
        </div>
      </div>
    </div>
  );
}
