"use client";

import React from "react";
import Link from "next/link";
import { AppLayout } from "@/components/layout/AppLayout";
import { Card, CardHeader, CardTitle, CardDescription, CardContent } from "@/components/common/Card";
import { DataTable } from "@/components/common/DataTable";
import { Button } from "@/components/common/Button";
import { Badge } from "@/components/common/Badge";
import { Bookmark, Plus, ArrowUpRight } from "lucide-react";

export default function WatchlistPage() {
  const watchlistItems = [
    { ticker: "RELIANCE.NS", name: "Reliance Industries", exchange: "NSE", price: "₹2,950.40", change: "+1.25%", isUp: true },
    { ticker: "TCS.NS", name: "Tata Consultancy Services", exchange: "NSE", price: "₹4,250.00", change: "+0.84%", isUp: true },
    { ticker: "INFY.NS", name: "Infosys Ltd", exchange: "NSE", price: "₹1,890.20", change: "-0.45%", isUp: false },
    { ticker: "HDFCBANK.NS", name: "HDFC Bank", exchange: "NSE", price: "₹1,655.00", change: "+0.32%", isUp: true },
    { ticker: "NVDA", name: "NVIDIA Corp (Demo)", exchange: "NASDAQ", price: "$124.50", change: "+2.85%", isUp: true, isDemo: true },
  ];

  const columns = [
    {
      key: "ticker",
      header: "Symbol",
      render: (item: typeof watchlistItems[0]) => (
        <div className="flex items-center gap-2">
          <span className="font-bold text-content">{item.ticker}</span>
          {item.isDemo && <Badge variant="gold" size="sm">DEMO</Badge>}
        </div>
      ),
    },
    { key: "name", header: "Company Name" },
    { key: "exchange", header: "Exchange" },
    { key: "price", header: "Spot Price", align: "right" as const },
    {
      key: "change",
      header: "24h Change",
      align: "right" as const,
      render: (item: typeof watchlistItems[0]) => (
        <span className={`font-bold ${item.isUp ? "text-financial-gain" : "text-financial-loss"}`}>
          {item.change}
        </span>
      ),
    },
    {
      key: "actions",
      header: "Research",
      align: "right" as const,
      render: (item: typeof watchlistItems[0]) => (
        <Link href={`/stocks/${encodeURIComponent(item.ticker)}`}>
          <Button variant="ghost" size="sm" rightIcon={<ArrowUpRight className="w-3.5 h-3.5" />}>
            Inspect
          </Button>
        </Link>
      ),
    },
  ];

  return (
    <AppLayout>
      <div className="space-y-6">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
          <div>
            <div className="flex items-center gap-2">
              <h1 className="text-2xl font-bold tracking-tight text-content">Custom Watchlist</h1>
              <Badge variant="primary" size="md">
                PostgreSQL Store
              </Badge>
            </div>
            <p className="text-xs text-content-muted mt-0.5">
              Curated market watchlists persisted across sessions.
            </p>
          </div>
          <Button variant="gold" size="sm" leftIcon={<Plus className="w-4 h-4" />}>
            Track Instrument
          </Button>
        </div>

        <Card>
          <CardHeader>
            <CardTitle>Tracked Securities</CardTitle>
            <CardDescription>{watchlistItems.length} active securities under observation</CardDescription>
          </CardHeader>
          <CardContent>
            <DataTable
              columns={columns}
              data={watchlistItems}
              keyExtractor={(item) => item.ticker}
            />
          </CardContent>
        </Card>
      </div>
    </AppLayout>
  );
}
