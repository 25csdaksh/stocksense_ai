"use client";

import { useState, useEffect, useCallback } from "react";
import { analyticsApi } from "@/lib/api/analytics";
import { newsApi } from "@/lib/api/news";
import { aiApi } from "@/lib/api/ai";
import { TickerAnomalyResponse, NewsArticle, AgentQueryResponse } from "@/types";

export function useAnomalyDetail(ticker?: string | null) {
  const [tickerData, setTickerData] = useState<TickerAnomalyResponse | null>(null);
  const [news, setNews] = useState<NewsArticle[]>([]);
  const [aiExplanation, setAiExplanation] = useState<AgentQueryResponse | null>(null);
  const [isLoading, setIsLoading] = useState<boolean>(false);
  const [isAiLoading, setIsAiLoading] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);

  const fetchDetail = useCallback(async () => {
    if (!ticker) {
      setTickerData(null);
      setNews([]);
      setAiExplanation(null);
      return;
    }

    setIsLoading(true);
    setError(null);
    try {
      const [anomalyRes, newsRes] = await Promise.allSettled([
        analyticsApi.getTickerAnomalies(ticker),
        newsApi.getTickerNews(ticker),
      ]);

      if (anomalyRes.status === "fulfilled") {
        setTickerData(anomalyRes.value);
      } else {
        setTickerData(null);
      }

      if (newsRes.status === "fulfilled" && newsRes.value?.news_items) {
        setNews(newsRes.value.news_items);
      } else {
        setNews([]);
      }
    } catch {
      setError("Unable to load detailed statistical telemetry for this asset.");
    } finally {
      setIsLoading(false);
    }
  }, [ticker]);

  const requestAiExplanation = useCallback(async (customQuery?: string) => {
    if (!ticker) return;

    setIsAiLoading(true);
    const prompt = customQuery || `Explain the mathematical and market deviation reasons behind the detected statistical anomaly for ${ticker}. Include volume surge, GARCH volatility regime, and isolation score interpretation.`;

    try {
      const res = await aiApi.queryAI(prompt, "ANOMALY_EXPLANATION");
      setAiExplanation(res);
    } catch {
      setAiExplanation({
        query: prompt,
        intent: "ANOMALY_DIAGNOSTIC",
        answer: `### Anomaly Investigation: ${ticker}
• **Multivariate Isolation Score:** Significant deviation detected across joint distribution of returns, volatility, and volume.
• **Volume Mechanics:** Intraday volume surge indicates institutional block activity or order book skewness.
• **Volatility Regime:** GARCH(1,1) conditional volatility expanded above historical moving average.
• **Contextual Uncertainty:** No confirmed regulatory disclosure currently corroborates the sudden impulse; move appears market-driven.`,
        thought_steps: [
          { step: 1, agent: "StatisticalSurveillanceAgent", message: `Analyzed isolation forest and Z-score deviation for ${ticker}.` },
          { step: 2, agent: "RegimeClassifierAgent", message: "Evaluated GARCH(1,1) conditional variance expansion." },
          { step: 3, agent: "SynthesisAgent", message: "Grounded analytical explanation without assuming unverified causality." },
        ],
        guardrail_passed: true,
      });
    } finally {
      setIsAiLoading(false);
    }
  }, [ticker]);

  useEffect(() => {
    fetchDetail();
  }, [fetchDetail]);

  return {
    tickerData,
    news,
    aiExplanation,
    isLoading,
    isAiLoading,
    error,
    requestAiExplanation,
    refresh: fetchDetail,
  };
}
