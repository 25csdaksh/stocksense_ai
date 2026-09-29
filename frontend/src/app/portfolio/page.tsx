"use client";

import React from "react";
import { AppLayout } from "@/components/layout/AppLayout";
import { Card, CardHeader, CardTitle, CardDescription, CardContent } from "@/components/common/Card";
import { StatCard } from "@/components/common/StatCard";
import { DataTable } from "@/components/common/DataTable";
import { Button } from "@/components/common/Button";
import { Badge } from "@/components/common/Badge";
import { Briefcase, Plus, ShieldCheck, PieChart as PieIcon } from "lucide-react";

export default function PortfolioPage() {
  const samplePositions = [
    { ticker: "RELIANCE.NS", name: "Reliance Industries", quantity: 50, avgPrice: "₹2,840.00", currentPrice: "₹2,950.40", pnl: "+3.88%", weight: "40%" },
    { ticker: "TCS.NS", name: "Tata Consultancy Services", quantity: 30, avgPrice: "₹4,120.00", currentPrice: "₹4,250.00", pnl: "+3.15%", weight: "35%" },
    { ticker: "HDFCBANK.NS", name: "HDFC Bank", quantity: 75, avgPrice: "₹1,620.00", currentPrice: "₹1,655.00", pnl: "+2.16%", weight: "25%" },
  ];

  const columns = [
    {
      key: "ticker",
      header: "Asset",
      render: (pos: typeof samplePositions[0]) => (
        <div>
          <span className="font-bold text-content">{pos.ticker}</span>
          <p className="text-[11px] text-content-muted">{pos.name}</p>
        </div>
      ),
    },
    { key: "quantity", header: "Quantity", align: "right" as const },
    { key: "avgPrice", header: "Avg Price", align: "right" as const },
    { key: "currentPrice", header: "Spot Price", align: "right" as const },
    {
      key: "pnl",
      header: "Unrealized P&L",
      align: "right" as const,
      render: (pos: typeof samplePositions[0]) => (
        <span className="font-bold text-financial-gain">{pos.pnl}</span>
      ),
    },
    { key: "weight", header: "Weight", align: "right" as const },
  ];

  return (
    <AppLayout>
      <div className="space-y-6">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
          <div>
            <div className="flex items-center gap-2">
              <h1 className="text-2xl font-bold tracking-tight text-content">Institutional Portfolio Risk</h1>
              <Badge variant="primary" size="md">
                TimescaleDB Hypertable
              </Badge>
            </div>
            <p className="text-xs text-content-muted mt-0.5">
              Multi-asset portfolio persistence, weighted portfolio beta, and 95% parametric VaR.
            </p>
          </div>
          <Button variant="gold" size="sm" leftIcon={<Plus className="w-4 h-4" />}>
            Add Position
          </Button>
        </div>

        {/* Portfolio Stats */}
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
          <StatCard
            label="Total Value"
            value="₹4,98,645"
            change={3.24}
            changeLabel="overall unrealized P&L"
            icon={<Briefcase className="w-4 h-4 text-primary" />}
          />
          <StatCard
            label="Daily 95% VaR"
            value="₹7,080 (1.42%)"
            changeLabel="Max expected 24h loss"
            icon={<ShieldCheck className="w-4 h-4 text-secondary" />}
          />
          <StatCard
            label="Weighted Beta"
            value="0.94"
            changeLabel="Relative to NIFTY 50"
            icon={<ShieldCheck className="w-4 h-4 text-accent" />}
          />
          <StatCard
            label="Cash Balance"
            value="₹50,000"
            changeLabel="Liquid capital"
            icon={<Briefcase className="w-4 h-4 text-content-muted" />}
          />
        </div>

        {/* Positions Table */}
        <Card>
          <CardHeader className="flex flex-row items-center justify-between">
            <div>
              <CardTitle>Holdings & Allocations</CardTitle>
              <CardDescription>Live real-time position tracking and weights</CardDescription>
            </div>
            <Badge variant="neutral" size="sm">
              3 Active Assets
            </Badge>
          </CardHeader>
          <CardContent>
            <DataTable
              columns={columns}
              data={samplePositions}
              keyExtractor={(pos) => pos.ticker}
            />
          </CardContent>
        </Card>
      </div>
    </AppLayout>
  );
}
