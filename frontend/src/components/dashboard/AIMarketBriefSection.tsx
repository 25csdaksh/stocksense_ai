"use client";

import React from "react";
import Link from "next/link";
import { useMarketBrief } from "@/hooks/useMarketBrief";
import { Card, CardHeader, CardTitle, CardContent } from "@/components/common/Card";
import { Badge } from "@/components/common/Badge";
import { Button } from "@/components/common/Button";
import { Skeleton } from "@/components/common/Skeleton";
import { Sparkles, ArrowRight, ShieldCheck, RefreshCw } from "lucide-react";

export const AIMarketBriefSection: React.FC = () => {
  const { brief, isLoading, refresh } = useMarketBrief();

  return (
    <Card className="border-primary/30 bg-gradient-to-br from-surface to-primary/5 shadow-card relative overflow-hidden">
      {/* Decorative subtle gold accent glow */}
      <div className="absolute top-0 right-0 w-64 h-64 bg-accent/5 rounded-full blur-3xl pointer-events-none" />

      <CardHeader className="pb-3 border-b border-border/80 flex flex-row items-center justify-between">
        <div className="flex items-center gap-2.5">
          <div className="p-1.5 rounded-lg bg-primary text-accent shadow-xs">
            <Sparkles className="w-4 h-4 text-accent" />
          </div>
          <div>
            <CardTitle className="text-base font-bold text-primary-dark flex items-center gap-2">
              MarketMind Intelligence
              <Badge variant="secondary" size="sm" className="font-mono text-[10px]">
                LangGraph Multi-Agent
              </Badge>
            </CardTitle>
            <p className="text-xs text-content-muted mt-0.5">
              Multi-source neural market synthesis & cross-asset regime detection
            </p>
          </div>
        </div>

        <div className="flex items-center gap-2">
          <Badge variant="gold" size="sm" className="hidden sm:inline-flex">
            AI-GENERATED ANALYSIS
          </Badge>
          <Button
            variant="ghost"
            size="sm"
            onClick={refresh}
            className="h-7 w-7 p-0 text-content-muted hover:text-primary"
            aria-label="Refresh AI synthesis"
          >
            <RefreshCw className="w-3.5 h-3.5" />
          </Button>
        </div>
      </CardHeader>

      <CardContent className="p-4 sm:p-5 space-y-4">
        {isLoading ? (
          <div className="space-y-3">
            <Skeleton variant="text" className="h-4 w-3/4" />
            <Skeleton variant="text" className="h-4 w-full" />
            <Skeleton variant="text" className="h-4 w-5/6" />
          </div>
        ) : (
          <>
            {/* Executive Summary */}
            <div className="p-3.5 rounded-xl bg-surface border border-border shadow-xs">
              <div className="flex items-center justify-between mb-1.5">
                <span className="text-xs font-bold uppercase tracking-wider text-primary">
                  Current Regime: {brief.regime}
                </span>
                <span className="text-[11px] text-content-muted font-mono flex items-center gap-1">
                  <ShieldCheck className="w-3 h-3 text-gain" />
                  Verified @ {brief.timestamp}
                </span>
              </div>
              <p className="text-xs sm:text-sm text-content leading-relaxed">
                {brief.summary}
              </p>
            </div>

            {/* Synthesized Bullets Grid */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-2.5">
              {brief.bullets.map((b, i) => (
                <div
                  key={i}
                  className="p-3 rounded-xl bg-surface/80 border border-border/70 hover:border-primary/20 transition-all flex items-start gap-2.5"
                >
                  <div className="w-1.5 h-1.5 rounded-full bg-accent mt-1.5 shrink-0" />
                  <div className="space-y-0.5">
                    <div className="flex items-center gap-2">
                      <span className="text-xs font-bold text-content">{b.topic}</span>
                      {b.tag && (
                        <span className="text-[10px] px-1.5 py-0.2 rounded bg-surface-subtle border border-border text-content-muted font-mono">
                          {b.tag}
                        </span>
                      )}
                    </div>
                    <p className="text-xs text-content-muted leading-normal">{b.detail}</p>
                  </div>
                </div>
              ))}
            </div>

            {/* Action Footer */}
            <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 pt-2">
              <div className="flex items-center gap-2 text-[11px] text-content-muted">
                <span>Confidence: 94.2%</span>
                <span>•</span>
                <span>Grounding: SEC 10-K + NSE Live</span>
                <span>•</span>
                <span className="text-accent font-semibold">Not Investment Advice</span>
              </div>

              <Link href="/research?q=Explain%20current%20macro%20market%20regime%20and%20sector%20leadership">
                <Button
                  variant="primary"
                  size="sm"
                  rightIcon={<ArrowRight className="w-3.5 h-3.5 text-accent" />}
                  className="shadow-button w-full sm:w-auto"
                >
                  Ask MarketMind
                </Button>
              </Link>
            </div>
          </>
        )}
      </CardContent>
    </Card>
  );
};
