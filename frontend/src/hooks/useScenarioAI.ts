"use client";

import { useState, useCallback } from "react";
import { aiApi } from "@/lib/api/ai";
import { AgentQueryResponse } from "@/types";

export interface ScenarioAIContext {
  ticker?: string;
  mode: string;
  currentPrice?: number;
  expectedTerminalPrice?: number;
  var95?: number;
  cvar99?: number;
  crisesDrawdowns?: Record<string, number>;
  macroReturnPct?: number;
  portfolioLossDollars?: number;
}

export function useScenarioAI() {
  const [response, setResponse] = useState<AgentQueryResponse | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const askScenarioQuestion = useCallback(
    async (question: string, context?: ScenarioAIContext) => {
      setIsLoading(true);
      setError(null);

      try {
        let contextualizedPrompt = question;
        if (context) {
          const contextSummary = [
            context.ticker ? `Target Asset: ${context.ticker}` : "Target: Portfolio",
            `Simulation Mode: ${context.mode}`,
            context.currentPrice !== undefined ? `Current Price: ₹${context.currentPrice}` : null,
            context.expectedTerminalPrice !== undefined ? `Simulated P50 Price: ₹${context.expectedTerminalPrice}` : null,
            context.var95 !== undefined ? `95% VaR: ${context.var95}%` : null,
            context.cvar99 !== undefined ? `99% CVaR (Expected Shortfall): ${context.cvar99}%` : null,
            context.macroReturnPct !== undefined ? `Macro Projected Return: ${context.macroReturnPct}%` : null,
            context.crisesDrawdowns ? `Crisis Drawdowns: ${JSON.stringify(context.crisesDrawdowns)}` : null,
          ]
            .filter(Boolean)
            .join(" | ");

          contextualizedPrompt = `${question}\n\n[Context: ${contextSummary}]`;
        }

        const res = await aiApi.queryAI(contextualizedPrompt, "QUANT_SCENARIO");
        setResponse(res);
      } catch (err: unknown) {
        const msg = err instanceof Error ? err.message : "Unable to retrieve AI scenario explanation.";
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
    askScenarioQuestion,
    clear,
  };
}
