"use client";

import { useState, useCallback } from "react";
import { aiApi } from "@/lib/api/ai";
import { AgentQueryResponse, NewsArticle } from "@/types";

export function useNewsAI() {
  const [response, setResponse] = useState<AgentQueryResponse | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const askNewsQuestion = useCallback(
    async (question: string, contextArticles?: NewsArticle[], selectedTicker?: string) => {
      setIsLoading(true);
      setError(null);

      try {
        let contextualizedPrompt = question;
        if (contextArticles && contextArticles.length > 0) {
          const newsSnippets = contextArticles
            .slice(0, 5)
            .map(
              (a, idx) =>
                `[Article ${idx + 1}] (${a.source} - ${a.published_at} - Sentiment: ${a.sentiment_label}) ${a.title}: ${a.summary}`
            )
            .join("\n");

          contextualizedPrompt = `${question}\n\n[Recent Verified Financial News Context]:\n${newsSnippets}`;
        }

        const res = await aiApi.queryAI(contextualizedPrompt, "EQUITY_RESEARCH");
        setResponse(res);
      } catch (err: unknown) {
        const msg = err instanceof Error ? err.message : "Unable to retrieve AI news analysis.";
        setError(msg);
      } finally {
        setIsLoading(false);
      }
    },
    []
  );

  const clear = useCallback(() => {
    setResponse(null);
    setError(null);
  }, []);

  return {
    response,
    isLoading,
    error,
    askNewsQuestion,
    clear,
  };
}
