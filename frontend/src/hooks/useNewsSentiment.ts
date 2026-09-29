"use client";

import { useMemo } from "react";
import { NewsArticle, SectorNewsSentiment } from "@/types";

export interface AggregateSentimentStats {
  totalCount: number;
  positiveCount: number;
  neutralCount: number;
  negativeCount: number;
  positivePct: number;
  neutralPct: number;
  negativePct: number;
  averageScore: number;
  overallRegime: "BULLISH" | "BEARISH" | "NEUTRAL";
  sectorBreakdown: SectorNewsSentiment[];
}

export function useNewsSentiment(articles: NewsArticle[]): AggregateSentimentStats {
  return useMemo(() => {
    const total = articles.length;
    if (total === 0) {
      return {
        totalCount: 0,
        positiveCount: 0,
        neutralCount: 0,
        negativeCount: 0,
        positivePct: 0,
        neutralPct: 0,
        negativePct: 0,
        averageScore: 0,
        overallRegime: "NEUTRAL",
        sectorBreakdown: [],
      };
    }

    let pos = 0;
    let neu = 0;
    let neg = 0;
    let scoreSum = 0;

    const sectorMap: Record<string, { count: number; pos: number; neu: number; neg: number; scoreSum: number }> = {};

    articles.forEach((art) => {
      const label = art.sentiment_label?.toUpperCase();
      const score = typeof art.sentiment_score === "number" ? art.sentiment_score : 0;
      scoreSum += score;

      let category: "pos" | "neu" | "neg" = "neu";
      if (label === "POSITIVE" || label === "BULLISH" || score > 0.15) {
        pos++;
        category = "pos";
      } else if (label === "NEGATIVE" || label === "BEARISH" || score < -0.15) {
        neg++;
        category = "neg";
      } else {
        neu++;
        category = "neu";
      }

      // Sector mapping
      const sec = art.sector || (art.ticker?.includes("TCS") || art.ticker?.includes("INFY") ? "Information Technology" : art.ticker?.includes("BANK") ? "Banking & Financials" : art.ticker?.includes("RELIANCE") ? "Energy & Petrochemicals" : "Broad Market");
      if (!sectorMap[sec]) {
        sectorMap[sec] = { count: 0, pos: 0, neu: 0, neg: 0, scoreSum: 0 };
      }
      sectorMap[sec].count++;
      sectorMap[sec].scoreSum += score;
      if (category === "pos") sectorMap[sec].pos++;
      if (category === "neu") sectorMap[sec].neu++;
      if (category === "neg") sectorMap[sec].neg++;
    });

    const avgScore = Number((scoreSum / total).toFixed(3));
    const regime: "BULLISH" | "BEARISH" | "NEUTRAL" =
      avgScore > 0.15 ? "BULLISH" : avgScore < -0.15 ? "BEARISH" : "NEUTRAL";

    const sectorBreakdown: SectorNewsSentiment[] = Object.entries(sectorMap).map(([sector, data]) => ({
      sector,
      article_count: data.count,
      positive_pct: Math.round((data.pos / data.count) * 100),
      neutral_pct: Math.round((data.neu / data.count) * 100),
      negative_pct: Math.round((data.neg / data.count) * 100),
      average_sentiment_score: Number((data.scoreSum / data.count).toFixed(2)),
    }));

    return {
      totalCount: total,
      positiveCount: pos,
      neutralCount: neu,
      negativeCount: neg,
      positivePct: Math.round((pos / total) * 100),
      neutralPct: Math.round((neu / total) * 100),
      negativePct: Math.round((neg / total) * 100),
      averageScore: avgScore,
      overallRegime: regime,
      sectorBreakdown,
    };
  }, [articles]);
}
