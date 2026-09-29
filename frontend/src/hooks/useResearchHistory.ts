"use client";

import { useState, useEffect, useCallback } from "react";
import { ResearchSession, ResearchMessage } from "@/types";

const HISTORY_STORAGE_KEY = "marketmind_research_history_v1";

const SEED_SESSIONS: ResearchSession[] = [
  {
    id: "session-tcs-infy",
    title: "TCS vs INFY Fundamental & Regulatory Risk Comparison",
    ticker: "TCS.NS",
    createdAt: new Date(Date.now() - 3600000 * 2).toISOString(),
    updatedAt: new Date(Date.now() - 3600000 * 2).toISOString(),
    lastQuery: "Compare TCS and INFY using available data and 10-K regulatory risk factors",
    messages: [
      {
        id: "msg-1-u",
        role: "user",
        content: "Compare TCS and INFY using available data and 10-K regulatory risk factors",
        timestamp: new Date(Date.now() - 3600000 * 2).toISOString(),
        ticker: "TCS.NS",
      },
      {
        id: "msg-1-a",
        role: "assistant",
        content: `### Executive Comparison Summary: TCS.NS vs INFY.NS

**1. Valuation & Financial Quality:**
- **TCS.NS**: Operates with superior Return on Equity (ROE ~48.2%) and near-zero debt leverage (D/E 0.02x). Forward P/E multiple sits at ~27.5x with consistent operating cash flow generation.
- **INFY.NS**: Trades at a slight relative valuation discount (~23.4x Forward P/E) with operating margins hovering around 21.8% and healthy Free Cash Flow yield of ~4.5%.

**2. Quantitative Momentum & Volatility:**
- Rolling 90-day correlation between both IT leaders is high ($\\rho = 0.84$).
- TCS exhibits lower historical annualized volatility (16.8% vs 19.2% for INFY), providing higher drawdown resilience during broad IT index selloffs.

**3. Regulatory & SEC 10-K Risk Disclosures:**
- **Visa & Talent Localization**: Both firms highlight reliance on H-1B/L-1 visa policies and rising onshore subcontracting wage costs as ongoing margin risks.
- **Enterprise Client IT Spend**: Slowdowns in discretionary BFSI transformation in North America represent the primary near-term revenue headwind.`,
        timestamp: new Date(Date.now() - 3600000 * 2).toISOString(),
        ticker: "TCS.NS",
        thoughtSteps: [
          { step: 1, agent: "SupervisorAgent", message: "Decomposed multi-ticker comparative equity query" },
          { step: 2, agent: "DataFetcherAgent", message: "Extracted comparative quotes and fundamentals for TCS and INFY" },
          { step: 3, agent: "QuantAgent", message: "Computed cross-asset correlation (rho=0.84) and volatility profiles" },
          { step: 4, agent: "RAGAgent", message: "Retrieved Item 1A Risk Factors from regulatory filing database" },
          { step: 5, agent: "SynthesisAgent", message: "Formulated objective institutional research briefing" },
        ],
        citations: [
          {
            id: "cite-tcs-1",
            ticker: "TCS.NS",
            title: "TCS Annual Report & Disclosures",
            filing_type: "Annual Filing",
            fiscal_year: 2025,
            section: "Item 1A — Risk Factors: Macroeconomic Client Spend",
            content_snippet: "Fluctuations in IT capital budgets across North American enterprise clients impact contract renewal velocity.",
            relevance_score: 0.94,
          },
          {
            id: "cite-infy-1",
            ticker: "INFY.NS",
            title: "Infosys SEC Form 20-F",
            filing_type: "Regulatory Filing",
            fiscal_year: 2025,
            section: "Item 3D — Risk Factors: Wage Inflation & Immigration Regulations",
            content_snippet: "Immigration reforms and onshore wage escalations may induce incremental operating cost pressures.",
            relevance_score: 0.91,
          },
        ],
      },
    ],
  },
  {
    id: "session-reliance-risk",
    title: "RELIANCE.NS Solvency & Downside Risk Profile",
    ticker: "RELIANCE.NS",
    createdAt: new Date(Date.now() - 3600000 * 24).toISOString(),
    updatedAt: new Date(Date.now() - 3600000 * 24).toISOString(),
    lastQuery: "Analyze RELIANCE.NS fundamentals, GARCH volatility regime, and recent risks",
    messages: [
      {
        id: "msg-2-u",
        role: "user",
        content: "Analyze RELIANCE.NS fundamentals, GARCH volatility regime, and recent risks",
        timestamp: new Date(Date.now() - 3600000 * 24).toISOString(),
        ticker: "RELIANCE.NS",
      },
      {
        id: "msg-2-a",
        role: "assistant",
        content: `### Institutional Research Brief: Reliance Industries Limited (RELIANCE.NS)

**1. Market & Capitalization Overview:**
Spot trading level exhibits consolidation with 52-week boundary support. Market cap remains well-capitalized at ~₹20.18 Lakh Cr ($240B+).

**2. Solvency & Cash Generation:**
- Net debt to EBITDA is well-contained (~0.42x D/E).
- Altman Z-Score of 3.45 places the balance sheet securely in the investment-grade safe zone.
- Interest coverage ratio of 6.8x ensures high solvency stability.

**3. Econometric Volatility & Risk Modeling:**
- **GARCH(1,1) Conditional Volatility**: Current process estimates 18.2% annualized volatility with stable persistence factor ($\\alpha + \\beta = 0.96$).
- **Parametric 1-Day VaR (95%)**: Downside parametric exposure is estimated at -1.89%.`,
        timestamp: new Date(Date.now() - 3600000 * 24).toISOString(),
        ticker: "RELIANCE.NS",
        thoughtSteps: [
          { step: 1, agent: "SupervisorAgent", message: "Classified single-stock risk & solvency research intent" },
          { step: 2, agent: "DataFetcherAgent", message: "Fetched spot quote, 52W range, and balance sheet ratios" },
          { step: 3, agent: "QuantAgent", message: "Executed GARCH(1,1) conditional volatility process" },
          { step: 4, agent: "SynthesisAgent", message: "Constructed structured institutional solvency brief" },
        ],
        citations: [
          {
            id: "cite-rel-1",
            ticker: "RELIANCE.NS",
            title: "Reliance Industries Annual Financial Statements",
            filing_type: "Annual Filing",
            fiscal_year: 2025,
            section: "Notes to Consolidated Financial Statements: Capital Structure",
            content_snippet: "Consolidated leverage metrics remain aligned with disciplined investment thresholds and long-term liquidity plans.",
            relevance_score: 0.95,
          },
        ],
      },
    ],
  },
];

export function useResearchHistory() {
  const [sessions, setSessions] = useState<ResearchSession[]>([]);
  const [activeSessionId, setActiveSessionId] = useState<string | null>(null);

  // Load from localStorage on mount
  useEffect(() => {
    if (typeof window === "undefined") return;
    try {
      const stored = localStorage.getItem(HISTORY_STORAGE_KEY);
      if (stored) {
        const parsed = JSON.parse(stored);
        if (Array.isArray(parsed) && parsed.length > 0) {
          setSessions(parsed);
          setActiveSessionId(parsed[0].id);
          return;
        }
      }
      setSessions(SEED_SESSIONS);
      setActiveSessionId(SEED_SESSIONS[0].id);
      localStorage.setItem(HISTORY_STORAGE_KEY, JSON.stringify(SEED_SESSIONS));
    } catch {
      setSessions(SEED_SESSIONS);
      setActiveSessionId(SEED_SESSIONS[0].id);
    }
  }, []);

  const saveSession = useCallback((session: ResearchSession) => {
    setSessions((prev) => {
      const existingIdx = prev.findIndex((s) => s.id === session.id);
      let updated: ResearchSession[];
      if (existingIdx >= 0) {
        updated = [...prev];
        updated[existingIdx] = session;
      } else {
        updated = [session, ...prev];
      }
      if (typeof window !== "undefined") {
        try {
          localStorage.setItem(HISTORY_STORAGE_KEY, JSON.stringify(updated));
        } catch (e) {
          console.warn("Could not persist research history:", e);
        }
      }
      return updated;
    });
  }, []);

  const deleteSession = useCallback((id: string) => {
    setSessions((prev) => {
      const updated = prev.filter((s) => s.id !== id);
      if (typeof window !== "undefined") {
        localStorage.setItem(HISTORY_STORAGE_KEY, JSON.stringify(updated));
      }
      return updated;
    });
    setActiveSessionId((prev) => (prev === id ? null : prev));
  }, []);

  const clearHistory = useCallback(() => {
    setSessions([]);
    setActiveSessionId(null);
    if (typeof window !== "undefined") {
      localStorage.removeItem(HISTORY_STORAGE_KEY);
    }
  }, []);

  const activeSession = sessions.find((s) => s.id === activeSessionId) || null;

  return {
    sessions,
    activeSessionId,
    activeSession,
    setActiveSessionId,
    saveSession,
    deleteSession,
    clearHistory,
  };
}
