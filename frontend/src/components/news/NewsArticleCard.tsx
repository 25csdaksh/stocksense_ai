"use client";

import React, { useState } from "react";
import { NewsArticle } from "@/types";
import { Badge } from "@/components/common/Badge";
import { ExternalLink, Copy, Check, TrendingUp, Sparkles, BookOpen } from "lucide-react";
import { useRouter } from "next/navigation";

interface NewsArticleCardProps {
  article: NewsArticle;
  onSelectTicker?: (ticker: string) => void;
}

export const NewsArticleCard: React.FC<NewsArticleCardProps> = ({
  article,
  onSelectTicker,
}) => {
  const router = useRouter();
  const [copied, setCopied] = useState(false);

  const handleCopy = () => {
    navigator.clipboard.writeText(`${article.title} (${article.source})`);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  const handleResearch = () => {
    const primaryTicker = article.ticker || (article.related_tickers && article.related_tickers[0]);
    const query = encodeURIComponent(article.title);
    if (primaryTicker) {
      router.push(`/research?ticker=${encodeURIComponent(primaryTicker)}&q=${query}`);
    } else {
      router.push(`/research?q=${query}`);
    }
  };

  const sentimentLabel = article.sentiment_label?.toUpperCase();
  const sentimentVariant =
    sentimentLabel === "POSITIVE" || sentimentLabel === "BULLISH"
      ? "gain"
      : sentimentLabel === "NEGATIVE" || sentimentLabel === "BEARISH"
      ? "loss"
      : "neutral";

  const allTickers = Array.from(
    new Set([article.ticker, ...(article.related_tickers || [])].filter(Boolean) as string[])
  );

  return (
    <div className="p-4 bg-surface rounded-xl border border-border hover:border-primary/40 transition-all shadow-sm hover:shadow space-y-2.5">
      {/* Header strip */}
      <div className="flex flex-wrap items-center justify-between gap-2">
        <div className="flex flex-wrap items-center gap-2">
          <span className="text-xs font-bold text-content">{article.source}</span>
          <span className="text-[11px] text-content-muted">• {article.published_at}</span>
          <Badge variant={sentimentVariant} size="sm">
            {sentimentLabel || "NEUTRAL"}
          </Badge>
          {typeof article.sentiment_score === "number" && (
            <span className="text-[10px] font-tabular font-semibold text-content-muted">
              Score: {article.sentiment_score > 0 ? `+` : ``}{article.sentiment_score.toFixed(2)}
            </span>
          )}
        </div>

        <div className="flex items-center gap-1.5 shrink-0">
          <button
            onClick={handleCopy}
            title="Copy headline"
            className="p-1 rounded text-content-muted hover:text-content hover:bg-surface-subtle transition-colors"
          >
            {copied ? <Check className="w-3.5 h-3.5 text-financial-gain" /> : <Copy className="w-3.5 h-3.5" />}
          </button>
          {article.url && article.url !== "#" && (
            <a
              href={article.url}
              target="_blank"
              rel="noopener noreferrer"
              title="Open source article"
              className="p-1 rounded text-content-muted hover:text-primary hover:bg-surface-subtle transition-colors"
            >
              <ExternalLink className="w-3.5 h-3.5" />
            </a>
          )}
        </div>
      </div>

      {/* Headline & Summary */}
      <h3
        onClick={handleResearch}
        className="text-sm font-bold text-content hover:text-primary transition-colors cursor-pointer leading-snug"
      >
        {article.title}
      </h3>

      {article.summary && (
        <p className="text-xs text-content-muted leading-relaxed line-clamp-2">
          {article.summary}
        </p>
      )}

      {/* Footer ticker tags & action links */}
      <div className="flex flex-wrap items-center justify-between gap-2 pt-1 border-t border-border/60">
        <div className="flex flex-wrap items-center gap-1.5">
          {allTickers.map((t) => (
            <button
              key={t}
              onClick={() => onSelectTicker ? onSelectTicker(t) : router.push(`/stocks/${encodeURIComponent(t)}`)}
              className="text-[10px] font-bold font-mono px-2 py-0.5 rounded bg-surface-subtle border border-border text-content hover:border-primary hover:text-primary transition-colors"
            >
              {t}
            </button>
          ))}
        </div>

        <div className="flex items-center gap-3 text-[11px] font-semibold">
          {allTickers.length > 0 && (
            <button
              onClick={() => router.push(`/stocks/${encodeURIComponent(allTickers[0])}`)}
              className="text-primary hover:underline flex items-center gap-1"
            >
              <TrendingUp className="w-3 h-3" />
              <span>Stock Details</span>
            </button>
          )}
          <button
            onClick={handleResearch}
            className="text-secondary hover:underline flex items-center gap-1"
          >
            <Sparkles className="w-3 h-3 text-secondary" />
            <span>AI Research</span>
          </button>
        </div>
      </div>
    </div>
  );
};
