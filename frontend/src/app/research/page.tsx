"use client";

import React, { useState } from "react";
import { AppLayout } from "@/components/layout/AppLayout";
import { Card, CardHeader, CardTitle, CardDescription, CardContent } from "@/components/common/Card";
import { Button } from "@/components/common/Button";
import { Badge } from "@/components/common/Badge";
import { Brain, Sparkles, Send, FileText, Database, ShieldAlert, CheckCircle2 } from "lucide-react";

export default function ResearchPage() {
  const [query, setQuery] = useState("");
  const [isProcessing, setIsProcessing] = useState(false);

  const sampleQueries = [
    "Compare TCS.NS and INFY.NS fundamentals with 10-K regulatory risk factors",
    "Analyze NVIDIA 10-K risk factors and realized volatility",
    "Simulate 2020 COVID macro shock on RELIANCE.NS stock price",
  ];

  return (
    <AppLayout>
      <div className="space-y-6">
        {/* Header */}
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
          <div>
            <div className="flex items-center gap-2">
              <h1 className="text-2xl font-bold tracking-tight text-content">AI Research Terminal</h1>
              <Badge variant="gold" size="md">
                LangGraph Multi-Agent
              </Badge>
            </div>
            <p className="text-xs text-content-muted mt-0.5">
              Autonomous financial synthesis across live market data, SEC 10-K filings, and ML analytics.
            </p>
          </div>
        </div>

        {/* Query Input Box */}
        <Card className="border-primary/30 shadow-card">
          <CardContent className="p-4 space-y-3">
            <div className="relative">
              <textarea
                rows={3}
                placeholder="Ask any institutional research inquiry (e.g. 'Evaluate TCS.NS valuation multiples vs sector average and retrieve SEC 10-K risk disclosures')..."
                value={query}
                onChange={(e: React.ChangeEvent<HTMLTextAreaElement>) => setQuery(e.target.value)}
                className="w-full rounded-xl border border-border bg-surface-subtle/50 p-3.5 text-sm text-content placeholder:text-content-muted/60 focus:outline-none focus:ring-2 focus:ring-primary/20 focus:border-primary resize-none transition-all"
              />
            </div>

            <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2">
              <div className="flex flex-wrap items-center gap-1.5">
                <span className="text-[11px] font-semibold text-content-muted">Sample prompts:</span>
                {sampleQueries.map((sq, i) => (
                  <button
                    key={i}
                    onClick={() => setQuery(sq)}
                    className="text-[11px] px-2 py-0.5 rounded-md bg-surface-subtle border border-border text-content-muted hover:text-primary hover:border-primary/30 transition-colors truncate max-w-xs"
                  >
                    {sq}
                  </button>
                ))}
              </div>

              <Button
                variant="primary"
                size="md"
                isLoading={isProcessing}
                onClick={() => setIsProcessing(true)}
                rightIcon={<Send className="w-4 h-4" />}
              >
                Synthesize
              </Button>
            </div>
          </CardContent>
        </Card>

        {/* Structured Research Response Sections Placeholder */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Main 2 Cols: Research Output */}
          <div className="lg:col-span-2 space-y-4">
            <Card>
              <CardHeader className="border-b border-border">
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-2">
                    <Brain className="w-4 h-4 text-primary" />
                    <CardTitle className="text-sm">Structured Research Findings</CardTitle>
                  </div>
                  <Badge variant="primary" size="sm">
                    Grounded Synthesis
                  </Badge>
                </div>
              </CardHeader>
              <CardContent className="p-6 space-y-6">
                {/* Data Summary */}
                <div className="space-y-1.5">
                  <h4 className="text-xs font-bold uppercase tracking-wider text-primary flex items-center gap-1.5">
                    <Database className="w-3.5 h-3.5 text-primary" />
                    1. Concrete Market Data
                  </h4>
                  <p className="text-xs text-content-muted leading-relaxed">
                    Quantitative inputs, spot quotes in INR/USD, 24-hour volume changes, and valuation multiples.
                  </p>
                </div>

                {/* Analysis */}
                <div className="space-y-1.5">
                  <h4 className="text-xs font-bold uppercase tracking-wider text-secondary flex items-center gap-1.5">
                    <CheckCircle2 className="w-3.5 h-3.5 text-secondary" />
                    2. Institutional Analysis
                  </h4>
                  <p className="text-xs text-content-muted leading-relaxed">
                    Statistical findings, Fama-French 5-Factor Stock DNA deciles, and comparative margin health.
                  </p>
                </div>

                {/* Assumptions & Uncertainty */}
                <div className="space-y-1.5">
                  <h4 className="text-xs font-bold uppercase tracking-wider text-accent flex items-center gap-1.5">
                    <ShieldAlert className="w-3.5 h-3.5 text-accent" />
                    3. Assumptions & Uncertainties
                  </h4>
                  <p className="text-xs text-content-muted leading-relaxed">
                    Methodological constraints, volatility boundaries, and non-deterministic assumptions.
                  </p>
                </div>
              </CardContent>
            </Card>
          </div>

          {/* Right Col: RAG Citations Inspector */}
          <div className="space-y-4">
            <Card>
              <CardHeader className="border-b border-border">
                <div className="flex items-center gap-2">
                  <FileText className="w-4 h-4 text-primary" />
                  <CardTitle className="text-sm">Verified Document Citations</CardTitle>
                </div>
                <CardDescription>SEC 10-K & Annual Report Extracts</CardDescription>
              </CardHeader>
              <CardContent className="p-4 space-y-3">
                <div className="p-3 rounded-xl bg-surface-subtle border border-border text-xs space-y-1.5">
                  <div className="flex items-center justify-between">
                    <Badge variant="primary" size="sm">[Source 1]</Badge>
                    <span className="text-[10px] text-content-muted">FY2025 • Item 1A</span>
                  </div>
                  <p className="text-[11px] text-content-muted leading-relaxed line-clamp-3">
                    Regulatory risks, competition, and macroeconomic dependency disclosures indexed from official regulatory filings.
                  </p>
                </div>
              </CardContent>
            </Card>
          </div>
        </div>
      </div>
    </AppLayout>
  );
}
