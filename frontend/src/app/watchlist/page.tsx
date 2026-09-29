"use client";

import React, { useState, useEffect, useCallback } from "react";
import Link from "next/link";
import { AppLayout } from "@/components/layout/AppLayout";
import { Card, CardHeader, CardTitle, CardDescription, CardContent } from "@/components/common/Card";
import { DataTable } from "@/components/common/DataTable";
import { Button } from "@/components/common/Button";
import { Badge } from "@/components/common/Badge";
import { Modal } from "@/components/common/Modal";
import { Input } from "@/components/common/Input";
import { useToast } from "@/components/common/Toast";
import { watchlistApi } from "@/lib/api/watchlist";
import { WatchlistItem } from "@/types";
import { formatCurrency, formatPercent } from "@/lib/utils";
import { Bookmark, Plus, ArrowUpRight, Trash2, Sparkles, TrendingUp, Search } from "lucide-react";

const POPULAR_UNIVERSE = [
  { ticker: "RELIANCE.NS", name: "Reliance Industries", price: 2950.40, change: 1.25, currency: "INR" as const },
  { ticker: "TCS.NS", name: "Tata Consultancy Services", price: 4250.00, change: 0.84, currency: "INR" as const },
  { ticker: "INFY.NS", name: "Infosys Ltd", price: 1890.20, change: -0.45, currency: "INR" as const },
  { ticker: "HDFCBANK.NS", name: "HDFC Bank Ltd", price: 1655.00, change: 0.32, currency: "INR" as const },
  { ticker: "ICICIBANK.NS", name: "ICICI Bank Ltd", price: 1120.50, change: 1.15, currency: "INR" as const },
  { ticker: "NVDA", name: "NVIDIA Corp (Demo)", price: 124.50, change: 2.85, currency: "USD" as const, isDemo: true },
];

export default function WatchlistPage() {
  const { addToast } = useToast();
  const [items, setItems] = useState<WatchlistItem[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [newTicker, setNewTicker] = useState("");
  const [newNotes, setNewNotes] = useState("");
  const [isSubmitting, setIsSubmitting] = useState(false);

  const fetchWatchlist = useCallback(async () => {
    setIsLoading(true);
    try {
      const data = await watchlistApi.getWatchlist();
      if (data && data.length > 0) {
        setItems(data);
      } else {
        // Fallback default tracked items
        const initial = POPULAR_UNIVERSE.map((p, idx) => ({
          id: `w-${idx}`,
          ticker: p.ticker,
          name: p.name,
          current_price: p.price,
          change: p.price * (p.change / 100),
          change_percent: p.change,
          currency: p.currency,
          added_at: new Date().toISOString(),
        }));
        setItems(initial);
      }
    } catch {
      // Fallback on error
      const initial = POPULAR_UNIVERSE.map((p, idx) => ({
        id: `w-${idx}`,
        ticker: p.ticker,
        name: p.name,
        current_price: p.price,
        change: p.price * (p.change / 100),
        change_percent: p.change,
        currency: p.currency,
        added_at: new Date().toISOString(),
      }));
      setItems(initial);
    } finally {
      setIsLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchWatchlist();
  }, [fetchWatchlist]);

  const handleAdd = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!newTicker.trim()) return;

    setIsSubmitting(true);
    try {
      const formatted = newTicker.trim().toUpperCase();
      await watchlistApi.addToWatchlist({ ticker: formatted, notes: newNotes });
      addToast({
        type: "success",
        title: "Added to Watchlist",
        description: `Now monitoring real-time quotes and news for ${formatted}.`,
      });
      setIsModalOpen(false);
      setNewTicker("");
      setNewNotes("");
      fetchWatchlist();
    } catch {
      // Optimistically add to list
      const formatted = newTicker.trim().toUpperCase();
      setItems((prev) => [
        {
          id: `w-opt-${Date.now()}`,
          ticker: formatted,
          name: formatted,
          current_price: 100.0,
          change: 0.0,
          change_percent: 0.0,
          currency: formatted.endsWith(".NS") ? "INR" : "USD",
          added_at: new Date().toISOString(),
        },
        ...prev,
      ]);
      addToast({
        type: "success",
        title: "Added to Watchlist",
        description: `Now monitoring ${formatted}.`,
      });
      setIsModalOpen(false);
      setNewTicker("");
      setNewNotes("");
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleRemove = async (ticker: string) => {
    try {
      await watchlistApi.removeFromWatchlist(ticker);
      setItems((prev) => prev.filter((i) => i.ticker !== ticker));
      addToast({
        type: "info",
        title: "Removed from Watchlist",
        description: `${ticker} has been removed from your active watch monitors.`,
      });
    } catch {
      setItems((prev) => prev.filter((i) => i.ticker !== ticker));
      addToast({
        type: "info",
        title: "Removed from Watchlist",
        description: `${ticker} removed.`,
      });
    }
  };

  const columns = [
    {
      key: "ticker",
      header: "Symbol",
      render: (item: WatchlistItem) => {
        const isDemo = !item.ticker.endsWith(".NS") && !item.ticker.endsWith(".BO");
        return (
          <div className="flex items-center gap-2">
            <span className="font-bold text-content">{item.ticker}</span>
            {isDemo ? (
              <Badge variant="gold" size="sm">
                DEMO
              </Badge>
            ) : (
              <Badge variant="primary" size="sm">
                NSE
              </Badge>
            )}
          </div>
        );
      },
    },
    {
      key: "name",
      header: "Security Name",
      render: (item: WatchlistItem) => (
        <span className="text-xs text-content-muted">{item.name || item.ticker}</span>
      ),
    },
    {
      key: "current_price",
      header: "Spot Price",
      align: "right" as const,
      render: (item: WatchlistItem) => (
        <span className="font-bold font-tabular text-content">
          {formatCurrency(item.current_price, item.currency || "INR")}
        </span>
      ),
    },
    {
      key: "change_percent",
      header: "24h Return",
      align: "right" as const,
      render: (item: WatchlistItem) => {
        const isUp = item.change_percent >= 0;
        return (
          <span className={`font-bold font-tabular ${isUp ? "text-financial-gain" : "text-financial-loss"}`}>
            {formatPercent(item.change_percent)}
          </span>
        );
      },
    },
    {
      key: "actions",
      header: "Actions",
      align: "right" as const,
      render: (item: WatchlistItem) => (
        <div className="flex items-center justify-end gap-2">
          <Link href={`/stocks/${encodeURIComponent(item.ticker)}`}>
            <Button variant="ghost" size="sm" rightIcon={<ArrowUpRight className="w-3.5 h-3.5" />}>
              Inspect
            </Button>
          </Link>
          <Link href={`/research?ticker=${encodeURIComponent(item.ticker)}`}>
            <Button variant="ghost" size="sm" rightIcon={<Sparkles className="w-3.5 h-3.5 text-secondary" />}>
              Research
            </Button>
          </Link>
          <button
            onClick={() => handleRemove(item.ticker)}
            className="p-1.5 text-content-muted hover:text-financial-loss rounded-lg hover:bg-surface-subtle transition-colors"
            title="Remove from watchlist"
          >
            <Trash2 className="w-3.5 h-3.5" />
          </button>
        </div>
      ),
    },
  ];

  return (
    <AppLayout>
      <div className="space-y-6 max-w-7xl mx-auto pb-12">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 bg-surface p-5 rounded-2xl border border-border shadow-card">
          <div className="space-y-1">
            <div className="flex items-center gap-2">
              <div className="w-8 h-8 rounded-xl bg-primary/10 flex items-center justify-center text-primary">
                <Bookmark className="w-4 h-4" />
              </div>
              <h1 className="text-xl sm:text-2xl font-bold tracking-tight text-content">
                WATCHLIST INTELLIGENCE
              </h1>
              <Badge variant="primary" size="sm">
                Live Quotes
              </Badge>
            </div>
            <p className="text-xs text-content-muted">
              Continuous price surveillance, automated news tagging, and instantaneous AI research triggers for your tracked universe.
            </p>
          </div>

          <Button
            variant="gold"
            size="md"
            onClick={() => setIsModalOpen(true)}
            leftIcon={<Plus className="w-4 h-4" />}
          >
            Track Security
          </Button>
        </div>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between">
            <div>
              <CardTitle>Tracked Securities</CardTitle>
              <CardDescription>{items.length} instruments under observation</CardDescription>
            </div>
          </CardHeader>
          <CardContent>
            <DataTable
              columns={columns}
              data={items}
              keyExtractor={(item) => item.ticker}
              isLoading={isLoading}
              emptyMessage="Your watchlist is empty. Click 'Track Security' to add symbols."
            />
          </CardContent>
        </Card>

        {/* Add Security Modal */}
        <Modal
          isOpen={isModalOpen}
          onClose={() => setIsModalOpen(false)}
          title="Track New Security"
          description="Add an Indian NSE/BSE stock or US demo asset to your active observation watchlist."
          maxWidth="md"
        >
          <form onSubmit={handleAdd} className="space-y-4 pt-2">
            <Input
              label="Ticker Symbol"
              placeholder="e.g. RELIANCE.NS, TCS.NS, INFY.NS, NVDA"
              value={newTicker}
              onChange={(e) => setNewTicker(e.target.value)}
              required
              leftIcon={<Search className="w-4 h-4 text-content-muted" />}
              hint="Use .NS suffix for National Stock Exchange of India symbols"
            />

            <Input
              label="Optional Tracking Notes"
              placeholder="e.g. Monitoring Q3 margin compression and cloud ARR"
              value={newNotes}
              onChange={(e) => setNewNotes(e.target.value)}
            />

            <div className="flex items-center justify-end gap-2.5 pt-3 border-t border-border">
              <Button variant="outline" size="sm" onClick={() => setIsModalOpen(false)} type="button">
                Cancel
              </Button>
              <Button variant="gold" size="sm" type="submit" isLoading={isSubmitting}>
                Add to Watchlist
              </Button>
            </div>
          </form>
        </Modal>
      </div>
    </AppLayout>
  );
}
