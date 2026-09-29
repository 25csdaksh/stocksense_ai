"use client";

import React, { useState, useEffect } from "react";
import { useRouter } from "next/navigation";
import { Modal } from "@/components/common/Modal";
import { Input } from "@/components/common/Input";
import { Badge } from "@/components/common/Badge";
import { POPULAR_INDIAN_STOCKS, POPULAR_US_DEMO_STOCKS, MAJOR_INDICES } from "@/lib/constants";
import { Search, TrendingUp, Brain, Briefcase, AlertTriangle, ArrowRight, CornerDownLeft } from "lucide-react";

export interface GlobalSearchProps {
  isOpen: boolean;
  onClose: () => void;
}

export const GlobalSearch: React.FC<GlobalSearchProps> = ({ isOpen, onClose }) => {
  const [query, setQuery] = useState("");
  const router = useRouter();

  // Keyboard shortcut listener (Cmd+K or Ctrl+K)
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if ((e.metaKey || e.ctrlKey) && e.key === "k") {
        e.preventDefault();
        if (isOpen) {
          onClose();
        } else {
          // Open handled by parent or custom event
          window.dispatchEvent(new CustomEvent("marketmind:open-search"));
        }
      }
    };
    window.addEventListener("keydown", handleKeyDown);
    return () => window.removeEventListener("keydown", handleKeyDown);
  }, [isOpen, onClose]);

  const allItems = [
    ...MAJOR_INDICES.map((i) => ({
      ticker: i.ticker,
      name: i.name,
      exchange: i.exchange,
      category: "Index",
      url: `/stocks/${encodeURIComponent(i.ticker)}`,
      is_demo: i.is_demo,
    })),
    ...POPULAR_INDIAN_STOCKS.map((s) => ({
      ticker: s.ticker,
      name: s.name,
      exchange: s.exchange,
      category: "Indian Equity",
      url: `/stocks/${encodeURIComponent(s.ticker)}`,
      is_demo: false,
    })),
    ...POPULAR_US_DEMO_STOCKS.map((s) => ({
      ticker: s.ticker,
      name: s.name,
      exchange: s.exchange,
      category: "US Equity",
      url: `/stocks/${encodeURIComponent(s.ticker)}`,
      is_demo: true,
    })),
  ];

  const filteredItems = query.trim()
    ? allItems.filter(
        (item) =>
          item.ticker.toLowerCase().includes(query.toLowerCase()) ||
          item.name.toLowerCase().includes(query.toLowerCase()) ||
          item.exchange.toLowerCase().includes(query.toLowerCase())
      )
    : allItems.slice(0, 6);

  const quickActions = [
    { label: "AI Financial Research", icon: <Brain className="w-4 h-4 text-primary" />, url: `/research?q=${encodeURIComponent(query)}` },
    { label: "Market Anomalies & Spikes", icon: <AlertTriangle className="w-4 h-4 text-financial-loss" />, url: "/anomalies" },
    { label: "Portfolio Risk & VaR", icon: <Briefcase className="w-4 h-4 text-secondary" />, url: "/portfolio" },
  ];

  const handleSelect = (url: string) => {
    router.push(url);
    onClose();
    setQuery("");
  };

  return (
    <Modal isOpen={isOpen} onClose={onClose} maxWidth="xl" className="p-0 overflow-hidden">
      <div className="p-4 border-b border-border bg-surface">
        <Input
          autoFocus
          placeholder="Search Indian stocks (TCS.NS, RELIANCE.NS), US demo, indices, or AI queries..."
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          leftIcon={<Search className="w-4 h-4 text-content-muted" />}
          rightIcon={
            <kbd className="hidden sm:inline-flex items-center gap-1 px-2 py-0.5 text-[10px] font-mono font-medium text-content-muted bg-surface-subtle border border-border rounded">
              ESC
            </kbd>
          }
          className="border-none bg-surface-subtle/60 focus:ring-0 text-base"
        />
      </div>

      <div className="max-h-96 overflow-y-auto p-4 space-y-4">
        {/* Quick AI Search trigger if user typed a query */}
        {query.trim().length > 2 && (
          <div
            onClick={() => handleSelect(`/research?q=${encodeURIComponent(query)}`)}
            className="flex items-center justify-between p-3 rounded-xl bg-primary-light/50 border border-primary/20 hover:bg-primary-light cursor-pointer transition-colors"
          >
            <div className="flex items-center gap-2.5">
              <div className="p-2 rounded-lg bg-primary text-white">
                <Brain className="w-4 h-4" />
              </div>
              <div>
                <p className="text-xs font-bold text-primary">Run Deep AI Research</p>
                <p className="text-xs text-content-muted">Analyze &ldquo;{query}&rdquo; via LangGraph + SEC 10-K RAG</p>
              </div>
            </div>
            <ArrowRight className="w-4 h-4 text-primary" />
          </div>
        )}

        {/* Matching Stocks & Indices */}
        <div>
          <p className="text-[11px] font-bold uppercase tracking-wider text-content-muted mb-2">
            {query.trim() ? "Search Results" : "Featured Markets & Stocks"}
          </p>
          <div className="space-y-1">
            {filteredItems.map((item) => (
              <div
                key={item.ticker}
                onClick={() => handleSelect(item.url)}
                className="flex items-center justify-between p-2.5 rounded-lg hover:bg-surface-subtle transition-colors cursor-pointer group"
              >
                <div className="flex items-center gap-3">
                  <div className="w-8 h-8 rounded-lg bg-surface-subtle border border-border flex items-center justify-center font-bold text-xs text-content">
                    <TrendingUp className="w-4 h-4 text-primary" />
                  </div>
                  <div>
                    <div className="flex items-center gap-2">
                      <span className="text-xs font-bold text-content group-hover:text-primary transition-colors">
                        {item.ticker}
                      </span>
                      {item.is_demo && (
                        <Badge variant="gold" size="sm">
                          DEMO
                        </Badge>
                      )}
                    </div>
                    <p className="text-[11px] text-content-muted">{item.name}</p>
                  </div>
                </div>
                <div className="flex items-center gap-2">
                  <span className="text-[11px] font-medium text-content-muted">
                    {item.exchange}
                  </span>
                  <CornerDownLeft className="w-3.5 h-3.5 text-content-muted opacity-0 group-hover:opacity-100 transition-opacity" />
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Quick Navigation Actions */}
        {!query.trim() && (
          <div>
            <p className="text-[11px] font-bold uppercase tracking-wider text-content-muted mb-2">
              Quick Workspaces
            </p>
            <div className="grid grid-cols-1 sm:grid-cols-3 gap-2">
              {quickActions.map((act) => (
                <div
                  key={act.label}
                  onClick={() => handleSelect(act.url)}
                  className="flex items-center gap-2.5 p-2.5 rounded-lg border border-border hover:bg-surface-subtle cursor-pointer transition-colors"
                >
                  <div className="p-1.5 rounded-md bg-surface-subtle">{act.icon}</div>
                  <span className="text-xs font-semibold text-content">{act.label}</span>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>

      <div className="p-3 bg-surface-subtle/60 border-t border-border flex items-center justify-between text-[11px] text-content-muted px-4">
        <span>Press <kbd className="font-mono bg-surface px-1.5 py-0.5 border border-border rounded text-[10px]">Enter</kbd> to select</span>
        <span>MarketMind AI • Indian NSE/BSE + US Multi-Asset</span>
      </div>
    </Modal>
  );
};
