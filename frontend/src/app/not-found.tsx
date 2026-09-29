"use client";

import React from "react";
import Link from "next/link";
import { AppLayout } from "@/components/layout/AppLayout";
import { Button } from "@/components/common/Button";
import { Badge } from "@/components/common/Badge";
import { Search, LayoutDashboard, Brain, ArrowLeft } from "lucide-react";

export default function NotFound() {
  const handleOpenSearch = () => {
    if (typeof window !== "undefined") {
      window.dispatchEvent(new CustomEvent("marketmind:open-search"));
    }
  };

  return (
    <AppLayout>
      <div className="min-h-[70vh] flex flex-col items-center justify-center text-center px-4 max-w-2xl mx-auto space-y-6">
        <Badge variant="loss" size="md">
          404 ERROR • RESOURCE NOT LOCATED
        </Badge>

        <div className="space-y-2">
          <h1 className="text-3xl sm:text-4xl font-extrabold tracking-tight text-content">
            Security or Workspace Not Found
          </h1>
          <p className="text-xs sm:text-sm text-content-muted leading-relaxed max-w-md mx-auto">
            The market intelligence route, instrument symbol, or research session you requested is either unavailable or has been archived.
          </p>
        </div>

        <div className="flex flex-wrap items-center justify-center gap-3 pt-2">
          <Link href="/dashboard">
            <Button variant="primary" size="md" leftIcon={<LayoutDashboard className="w-4 h-4" />}>
              Return to Dashboard
            </Button>
          </Link>
          <Button
            variant="gold"
            size="md"
            onClick={handleOpenSearch}
            leftIcon={<Search className="w-4 h-4" />}
          >
            Search Securities (Cmd+K)
          </Button>
        </div>

        {/* Quick Route Suggestions */}
        <div className="grid grid-cols-1 sm:grid-cols-3 gap-3 w-full pt-8 border-t border-border">
          <Link
            href="/stocks"
            className="p-3.5 bg-surface rounded-xl border border-border hover:border-primary/40 text-left transition-all group"
          >
            <span className="text-xs font-bold text-content group-hover:text-primary">Stock Intelligence →</span>
            <p className="text-[11px] text-content-muted mt-0.5">Explore NSE/BSE & US equities</p>
          </Link>

          <Link
            href="/research"
            className="p-3.5 bg-surface rounded-xl border border-border hover:border-primary/40 text-left transition-all group"
          >
            <span className="text-xs font-bold text-content group-hover:text-primary">Deep AI Research →</span>
            <p className="text-[11px] text-content-muted mt-0.5">Multi-agent SEC & filing RAG</p>
          </Link>

          <Link
            href="/anomalies"
            className="p-3.5 bg-surface rounded-xl border border-border hover:border-primary/40 text-left transition-all group"
          >
            <span className="text-xs font-bold text-content group-hover:text-primary">Anomaly Center →</span>
            <p className="text-[11px] text-content-muted mt-0.5">Isolation Forest outliers</p>
          </Link>
        </div>
      </div>
    </AppLayout>
  );
}
