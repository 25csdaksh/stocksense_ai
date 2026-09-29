"use client";

import React, { useState } from "react";
import Link from "next/link";
import { AppLayout } from "@/components/layout/AppLayout";
import { Card, CardHeader, CardTitle, CardDescription, CardContent } from "@/components/common/Card";
import { Input } from "@/components/common/Input";
import { Badge } from "@/components/common/Badge";
import { Button } from "@/components/common/Button";
import { POPULAR_INDIAN_STOCKS, POPULAR_US_DEMO_STOCKS, MAJOR_INDICES } from "@/lib/constants";
import { Search, ArrowUpRight, Filter } from "lucide-react";

export default function StocksPage() {
  const [filter, setFilter] = useState<"ALL" | "NSE" | "DEMO">("ALL");
  const [search, setSearch] = useState("");

  const allAssets = [
    ...MAJOR_INDICES.map((i) => ({ ...i, type: "Index" })),
    ...POPULAR_INDIAN_STOCKS.map((s) => ({ ...s, country: "India", is_demo: false, type: "Equity" })),
    ...POPULAR_US_DEMO_STOCKS.map((s) => ({ ...s, country: "USA", type: "Equity" })),
  ];

  const filteredAssets = allAssets.filter((item) => {
    if (filter === "NSE" && item.exchange !== "NSE") return false;
    if (filter === "DEMO" && !item.is_demo) return false;
    if (search.trim()) {
      return (
        item.ticker.toLowerCase().includes(search.toLowerCase()) ||
        item.name.toLowerCase().includes(search.toLowerCase())
      );
    }
    return true;
  });

  return (
    <AppLayout>
      <div className="space-y-6">
        {/* Page Header */}
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
          <div>
            <h1 className="text-2xl font-bold tracking-tight text-content">Market Screener & Directory</h1>
            <p className="text-xs text-content-muted mt-0.5">
              Live multi-exchange coverage across NSE, BSE, and US Benchmark Equities.
            </p>
          </div>
          <div className="flex items-center gap-2">
            <Button
              variant={filter === "ALL" ? "primary" : "outline"}
              size="sm"
              onClick={() => setFilter("ALL")}
            >
              All Assets
            </Button>
            <Button
              variant={filter === "NSE" ? "primary" : "outline"}
              size="sm"
              onClick={() => setFilter("NSE")}
            >
              NSE India
            </Button>
            <Button
              variant={filter === "DEMO" ? "gold" : "outline"}
              size="sm"
              onClick={() => setFilter("DEMO")}
            >
              US Demo Data
            </Button>
          </div>
        </div>

        {/* Search & Filter Bar */}
        <div className="max-w-md">
          <Input
            placeholder="Filter by ticker or company name..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            leftIcon={<Search className="w-4 h-4" />}
          />
        </div>

        {/* Assets Grid */}
        <Card>
          <CardHeader>
            <CardTitle>Constituents & Benchmark Assets</CardTitle>
            <CardDescription>Showing {filteredAssets.length} tracked instruments</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              {filteredAssets.map((stock) => (
                <Link
                  key={stock.ticker}
                  href={`/stocks/${encodeURIComponent(stock.ticker)}`}
                  className="p-4 rounded-xl border border-border bg-surface hover:bg-surface-subtle hover:border-content-muted/20 transition-all flex flex-col justify-between gap-3 group"
                >
                  <div className="flex items-start justify-between">
                    <div>
                      <div className="flex items-center gap-2">
                        <span className="text-sm font-bold text-content group-hover:text-primary transition-colors">
                          {stock.ticker}
                        </span>
                        {stock.is_demo && (
                          <Badge variant="gold" size="sm">
                            DEMO
                          </Badge>
                        )}
                        {!stock.is_demo && (
                          <Badge variant="primary" size="sm">
                            {stock.exchange}
                          </Badge>
                        )}
                      </div>
                      <p className="text-xs text-content-muted mt-1 line-clamp-1">{stock.name}</p>
                    </div>
                    <ArrowUpRight className="w-4 h-4 text-content-muted group-hover:text-primary transition-colors shrink-0" />
                  </div>
                  <div className="flex items-center justify-between text-xs pt-2 border-t border-border-subtle">
                    <span className="text-content-muted font-medium">{stock.type}</span>
                    <span className="text-primary font-semibold group-hover:underline">Deep-Dive</span>
                  </div>
                </Link>
              ))}
            </div>
          </CardContent>
        </Card>
      </div>
    </AppLayout>
  );
}
