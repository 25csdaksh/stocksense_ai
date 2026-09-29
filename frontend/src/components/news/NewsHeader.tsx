"use client";

import React from "react";
import { Badge } from "@/components/common/Badge";
import { Button } from "@/components/common/Button";
import { Newspaper, RotateCcw, Sparkles, BookOpen, Clock } from "lucide-react";
import { useRouter } from "next/navigation";

interface NewsHeaderProps {
  totalArticles: number;
  lastUpdated: string | null;
  isLoading: boolean;
  isDemo?: boolean;
  onRefresh: () => void;
  onOpenAI: () => void;
}

export const NewsHeader: React.FC<NewsHeaderProps> = ({
  totalArticles,
  lastUpdated,
  isLoading,
  isDemo,
  onRefresh,
  onOpenAI,
}) => {
  const router = useRouter();

  return (
    <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 bg-surface p-5 rounded-2xl border border-border shadow-card">
      <div className="space-y-1.5">
        <div className="flex flex-wrap items-center gap-2.5">
          <div className="w-8 h-8 rounded-xl bg-primary/10 flex items-center justify-center text-primary">
            <Newspaper className="w-4 h-4" />
          </div>
          <h1 className="text-xl sm:text-2xl font-bold tracking-tight text-content">
            FINANCIAL NEWS INTELLIGENCE
          </h1>
          <Badge variant="primary" size="sm">
            NLP Sentiment Polarity
          </Badge>
          <Badge variant="gold" size="sm">
            {totalArticles} Verified Wire Feeds
          </Badge>
          {isDemo && (
            <Badge variant="neutral" size="sm">
              DEMO DATA
            </Badge>
          )}
        </div>

        <p className="text-xs text-content-muted max-w-3xl leading-relaxed">
          Real-time financial intelligence feed annotated with NLP sentiment scoring, cross-asset ticker linking,
          sector-level sentiment aggregates, and direct AI research routing.
        </p>

        {lastUpdated && (
          <div className="flex items-center gap-1.5 text-[11px] text-content-muted font-tabular pt-0.5">
            <Clock className="w-3.5 h-3.5 text-primary" />
            <span>Feed Synchronized: {lastUpdated}</span>
          </div>
        )}
      </div>

      <div className="flex flex-wrap items-center gap-2.5 shrink-0">
        <Button
          variant="outline"
          size="sm"
          onClick={onRefresh}
          disabled={isLoading}
          leftIcon={<RotateCcw className={`w-3.5 h-3.5 ${isLoading ? "animate-spin" : ""}`} />}
        >
          Refresh Feed
        </Button>
        <Button
          variant="gold"
          size="sm"
          onClick={onOpenAI}
          leftIcon={<Sparkles className="w-3.5 h-3.5" />}
        >
          AI Summarize
        </Button>
        <Button
          variant="primary"
          size="sm"
          onClick={() => router.push("/research")}
          leftIcon={<BookOpen className="w-3.5 h-3.5" />}
        >
          Open Research
        </Button>
      </div>
    </div>
  );
};
