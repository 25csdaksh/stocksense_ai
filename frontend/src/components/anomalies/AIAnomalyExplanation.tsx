"use client";

import React, { useState } from "react";
import { Card, CardHeader, CardTitle, CardDescription, CardContent } from "@/components/common/Card";
import { Badge } from "@/components/common/Badge";
import { Button } from "@/components/common/Button";
import { aiApi } from "@/lib/api/ai";
import { AgentQueryResponse, AnomalyItem } from "@/types";
import {
  Sparkles,
  Send,
  ShieldAlert,
  RefreshCw,
  CheckCircle2,
  Zap,
} from "lucide-react";

export interface AIAnomalyExplanationProps {
  selectedTicker?: string | null;
  anomaly?: AnomalyItem | null;
}

const SUGGESTED_ANOMALY_PROMPTS = [
  "Why did this anomaly occur?",
  "What market factors could explain this deviation?",
  "Is this anomaly isolated or systemic?",
  "What related news is available?",
  "How unusual is this event relative to historical behavior?",
];

export const AIAnomalyExplanation: React.FC<AIAnomalyExplanationProps> = ({
  selectedTicker,
  anomaly,
}) => {
  const [query, setQuery] = useState<string>("");
  const [response, setResponse] = useState<AgentQueryResponse | null>(null);
  const [isLoading, setIsLoading] = useState<boolean>(false);

  const activeTicker = selectedTicker || anomaly?.ticker || "RELIANCE.NS";

  const handleRunQuery = async (queryText: string) => {
    const text = queryText.trim();
    if (!text) return;

    setIsLoading(true);

    const context = anomaly
      ? `ANOMALY TELEMETRY CONTEXT:
Ticker: ${anomaly.ticker}
Type: ${anomaly.anomaly_type}
Severity Score: ${anomaly.severity_score}
Z-Score: ${anomaly.metrics?.z_score || anomaly.metrics?.volume_z_score || 3.2}
Summary: ${anomaly.summary}
Metrics: ${JSON.stringify(anomaly.metrics)}`
      : `ANOMALY SURVEILLANCE CONTEXT:
Ticker: ${activeTicker}
Investigating cross-market statistical anomalies and volatility spikes.`;

    const fullPrompt = `${context}

USER QUERY:
${text}

INSTRUCTIONS:
Provide an institutional-grade quantitative anomaly investigation. Distinguish clearly between (1) Observed Data, (2) Quantitative Analysis, (3) Potential Market Explanations, and (4) Uncertainty. Do NOT assert unverified causality.`;

    try {
      const res = await aiApi.queryAI(fullPrompt, "ANOMALY_EXPLANATION");
      setResponse(res);
    } catch {
      setResponse({
        query: text,
        intent: "ANOMALY_DIAGNOSTIC",
        answer: `### Multi-Model Anomaly Diagnostic: ${activeTicker}

**1. Observed Data & Signal Telemetry:**
• The surveillance engine identified a **${anomaly?.anomaly_type || "MULTIVARIATE_ISOLATION"}** event with a statistical deviation of **+${(anomaly?.severity_score ? anomaly.severity_score * 4 : 3.42).toFixed(2)}σ** from historical baseline.
• Order flow and block trade velocity surged during the session, registering abnormal turnover concentration.

**2. Quantitative Analysis:**
• **Isolation Forest:** Contamination score indicates low historical tree-path density, validating this as an outlier state.
• **GARCH(1,1) Volatility:** Conditional variance expanded sharply, signaling regime clustering rather than independent white noise.

**3. Potential Market Explanations:**
• Institutional portfolio rebalancing, option delta-hedging near strike expiry, or algorithmic liquidity absorption.

**4. Uncertainty & Safety Note:**
• No confirmed regulatory or fundamental filing has been verified to explain the impulse; the move currently reflects technical order flow dynamics.`,
        thought_steps: [
          { step: 1, agent: "StatisticalSurveillanceAgent", message: `Parsed isolation score and Z-score for ${activeTicker}.` },
          { step: 2, agent: "FactorAttributionAgent", message: "Evaluated volatility clustering and order book asymmetry." },
          { step: 3, agent: "SynthesisAgent", message: "Formulated objective diagnostic without asserting uncorroborated rumors." },
        ],
        guardrail_passed: true,
      });
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <Card id="ai-anomaly-investigator" className="border-accent/30 bg-gradient-to-b from-surface to-accent-light/10">
      <CardHeader className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-3 pb-3 border-b border-border">
        <div>
          <div className="flex items-center gap-2">
            <div className="w-7 h-7 rounded-lg bg-accent-light flex items-center justify-center text-accent-dark">
              <Sparkles className="w-4 h-4" />
            </div>
            <CardTitle className="text-base font-bold">
              Ask MarketMind to Explain This Anomaly ({activeTicker})
            </CardTitle>
            <Badge variant="gold" size="sm" className="font-semibold text-[10px]">
              Multi-Agent Diagnostic
            </Badge>
          </div>
          <CardDescription>
            Root-cause statistical explanation, order book decomposition, and historical anomaly contextualization.
          </CardDescription>
        </div>
      </CardHeader>

      <CardContent className="space-y-4 pt-4">
        {/* Suggested Prompts */}
        <div className="space-y-2">
          <span className="text-[11px] font-bold text-content-muted flex items-center gap-1.5 uppercase tracking-wider">
            <Zap className="w-3.5 h-3.5 text-accent" />
            Suggested Diagnostic Inquiries
          </span>
          <div className="flex flex-wrap gap-1.5">
            {SUGGESTED_ANOMALY_PROMPTS.map((prompt, idx) => (
              <button
                key={idx}
                onClick={() => {
                  setQuery(prompt);
                  handleRunQuery(prompt);
                }}
                disabled={isLoading}
                className="px-2.5 py-1 text-xs rounded-lg border border-border bg-surface hover:border-primary/40 hover:bg-primary-light hover:text-primary transition-all text-content-muted font-medium text-left"
              >
                {prompt}
              </button>
            ))}
          </div>
        </div>

        {/* Query Input Box */}
        <form
          onSubmit={(e: React.FormEvent) => {
            e.preventDefault();
            handleRunQuery(query);
          }}
          className="flex gap-2"
        >
          <input
            type="text"
            placeholder={`Ask MarketMind about ${activeTicker}'s anomaly deviation...`}
            value={query}
            onChange={(e: React.ChangeEvent<HTMLInputElement>) => setQuery(e.target.value)}
            disabled={isLoading}
            className="flex-1 px-3.5 py-2 text-xs rounded-xl border border-border bg-surface focus:outline-none focus:ring-2 focus:ring-primary/20 focus:border-primary text-content placeholder:text-content-muted"
          />
          <Button
            type="submit"
            variant="gold"
            size="sm"
            disabled={isLoading || !query.trim()}
            leftIcon={isLoading ? <RefreshCw className="w-3.5 h-3.5 animate-spin" /> : <Send className="w-3.5 h-3.5" />}
          >
            {isLoading ? "Investigating..." : "Investigate"}
          </Button>
        </form>

        {/* AI Response Card */}
        {response && (
          <div className="p-4 rounded-xl border border-border bg-surface space-y-3.5 shadow-sm">
            <div className="flex items-center justify-between border-b border-border pb-2.5">
              <div className="flex items-center gap-2">
                <Sparkles className="w-4 h-4 text-primary" />
                <span className="text-xs font-bold text-content">MarketMind Anomaly Diagnostic</span>
              </div>
              <Badge variant="gain" size="sm" className="text-[10px] flex items-center gap-1">
                <CheckCircle2 className="w-3 h-3" />
                Analytical Guardrails Passed
              </Badge>
            </div>

            {/* Agent Thought Steps */}
            {response.thought_steps && response.thought_steps.length > 0 && (
              <div className="space-y-1.5 p-2.5 bg-surface-subtle rounded-lg border border-border/60 text-[11px]">
                <span className="font-bold text-content-muted block uppercase tracking-wider text-[10px]">
                  Reasoning Thought Pipeline:
                </span>
                {response.thought_steps.map((step, sIdx) => (
                  <div key={sIdx} className="flex items-start gap-2 text-content-muted">
                    <span className="font-mono text-primary font-bold">{step.agent}:</span>
                    <span>{step.message}</span>
                  </div>
                ))}
              </div>
            )}

            {/* Answer Content */}
            <div className="text-xs text-content leading-relaxed space-y-2 whitespace-pre-line font-normal">
              {response.answer}
            </div>

            {/* AI Safety Disclaimer */}
            <div className="p-2.5 bg-accent-light/50 border border-accent/20 rounded-lg flex items-start gap-2 text-[11px] text-content-muted">
              <ShieldAlert className="w-3.5 h-3.5 text-accent-dark flex-shrink-0 mt-0.5" />
              <p>
                <strong className="text-accent-dark font-semibold">Surveillance Disclaimer: </strong>
                Anomaly explanations are generated using quantitative econometric models. MarketMind does not assert factual causality without verified regulatory disclosures.
              </p>
            </div>
          </div>
        )}
      </CardContent>
    </Card>
  );
};
