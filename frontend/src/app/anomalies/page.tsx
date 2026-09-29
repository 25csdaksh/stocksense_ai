"use client";

import React from "react";
import { AppLayout } from "@/components/layout/AppLayout";
import { StatCard } from "@/components/common/StatCard";
import { Card, CardHeader, CardTitle, CardDescription, CardContent } from "@/components/common/Card";
import { Badge } from "@/components/common/Badge";
import { AlertTriangle, TrendingDown, Zap, ShieldAlert } from "lucide-react";

export default function AnomaliesPage() {
  const anomalies = [
    {
      id: "anom-1",
      ticker: "TCS.NS",
      type: "VOLUME_SURGE",
      severity: "HIGH",
      price: "₹4,250.00",
      description: "Unusual volume spike exceeding 3.8 standard deviations with 4.2x average 30-day volume.",
      time: "25 mins ago",
    },
    {
      id: "anom-2",
      ticker: "RELIANCE.NS",
      type: "VOLATILITY_BURST",
      severity: "MEDIUM",
      price: "₹2,950.40",
      description: "GARCH(1,1) conditional volatility expanded to 32.4% annualized following block deal rumors.",
      time: "1 hour ago",
    },
    {
      id: "anom-3",
      ticker: "NVDA",
      type: "PRICE_SPIKE",
      severity: "LOW",
      price: "$124.50",
      description: "Intraday momentum deviation detected via Isolation Forest (Contamination score = 0.021).",
      time: "3 hours ago",
      isDemo: true,
    },
  ];

  return (
    <AppLayout>
      <div className="space-y-6">
        <div>
          <div className="flex items-center gap-2">
            <h1 className="text-2xl font-bold tracking-tight text-content">Market Anomalies & Volatility</h1>
            <Badge variant="loss" size="md">
              Isolation Forest + GARCH
            </Badge>
          </div>
          <p className="text-xs text-content-muted mt-0.5">
            Real-time multivariate statistical anomaly detection and abnormal volume surge detection.
          </p>
        </div>

        {/* Snapshot Cards */}
        <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
          <StatCard
            label="Active Anomalies"
            value="3 Detections"
            change={2}
            changeLabel="last 24 hours"
            icon={<AlertTriangle className="w-4 h-4 text-financial-loss" />}
          />
          <StatCard
            label="Max Volume Z-Score"
            value="+3.82σ"
            changeLabel="TCS.NS (NSE)"
            icon={<Zap className="w-4 h-4 text-accent" />}
          />
          <StatCard
            label="Average Market Vol"
            value="14.8%"
            change={-0.8}
            changeLabel="30-day EWMA"
            icon={<TrendingDown className="w-4 h-4 text-primary" />}
          />
        </div>

        {/* Anomalies List */}
        <Card>
          <CardHeader>
            <CardTitle>Detected Statistical Anomalies</CardTitle>
            <CardDescription>Multi-asset alerts scored by statistical deviation</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-3">
              {anomalies.map((item) => (
                <div
                  key={item.id}
                  className="p-4 rounded-xl border border-border bg-surface hover:bg-surface-subtle transition-colors flex flex-col md:flex-row md:items-center justify-between gap-4"
                >
                  <div className="space-y-1.5 flex-1">
                    <div className="flex items-center gap-2">
                      <span className="text-sm font-bold text-content">{item.ticker}</span>
                      <Badge
                        variant={item.severity === "HIGH" ? "loss" : item.severity === "MEDIUM" ? "gold" : "neutral"}
                        size="sm"
                      >
                        {item.severity} SEVERITY
                      </Badge>
                      <Badge variant="outline" size="sm">
                        {item.type}
                      </Badge>
                      {item.isDemo && (
                        <Badge variant="gold" size="sm">
                          DEMO
                        </Badge>
                      )}
                    </div>
                    <p className="text-xs text-content-muted leading-relaxed">{item.description}</p>
                  </div>
                  <div className="text-right shrink-0">
                    <p className="text-sm font-bold text-content font-tabular">{item.price}</p>
                    <p className="text-[11px] text-content-muted">{item.time}</p>
                  </div>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      </div>
    </AppLayout>
  );
}
