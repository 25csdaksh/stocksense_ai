"use client";

import React, { useState, useRef, useEffect } from "react";
import {
  Sparkles,
  Send,
  Cpu,
  Database,
  Search,
  CheckCircle2,
  FileText,
  AlertCircle,
  BarChart3,
  Loader2,
} from "lucide-react";
import FanChart from "../charts/FanChart";
import StockDNARadar from "../charts/StockDNARadar";

interface Message {
  id: string;
  role: "user" | "assistant";
  content: string;
  thoughts?: string[];
  toolCalls?: { agent: string; tool: string; result?: string }[];
  widgets?: any[];
  citations?: any[];
  badge?: string;
}

export default function AgentChatDrawer() {
  const [messages, setMessages] = useState<Message[]>([
    {
      id: "welcome",
      role: "assistant",
      content:
        "Welcome to the **MARKETMIND AI Multi-Agent Intelligence Console**. You can ask me to run scenario simulations, inspect 5-factor Stock DNA, detect statistical market anomalies, or search SEC 10-K regulatory disclosures.",
      thoughts: ["Initialized supervisor graph and connected to Qdrant vector index."],
      toolCalls: [],
      badge: "LIVE KNOWLEDGE BASE",
    },
  ]);
  const [inputQuery, setInputQuery] = useState("");
  const [isStreaming, setIsStreaming] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages, isStreaming]);

  const handleSend = async (e?: React.FormEvent) => {
    if (e) e.preventDefault();
    if (!inputQuery.trim() || isStreaming) return;

    const userText = inputQuery.trim();
    setInputQuery("");

    const userMsgId = `user_${Date.now()}`;
    const assistantMsgId = `asst_${Date.now()}`;

    setMessages((prev) => [
      ...prev,
      { id: userMsgId, role: "user", content: userText },
      {
        id: assistantMsgId,
        role: "assistant",
        content: "",
        thoughts: [],
        toolCalls: [],
        widgets: [],
        citations: [],
      },
    ]);

    setIsStreaming(true);

    try {
      const apiBase = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";
      const eventSource = new EventSource(
        `${apiBase}/api/v1/agent/stream?query=${encodeURIComponent(userText)}`
      );

      eventSource.addEventListener("thought", (event: any) => {
        const payload = JSON.parse(event.data);
        setMessages((prev) =>
          prev.map((msg) =>
            msg.id === assistantMsgId
              ? {
                  ...msg,
                  thoughts: [...(msg.thoughts || []), `[${payload.agent}] ${payload.message}`],
                }
              : msg
          )
        );
      });

      eventSource.addEventListener("tool_call", (event: any) => {
        const payload = JSON.parse(event.data);
        setMessages((prev) =>
          prev.map((msg) =>
            msg.id === assistantMsgId
              ? {
                  ...msg,
                  toolCalls: [
                    ...(msg.toolCalls || []),
                    { agent: payload.agent, tool: payload.tool },
                  ],
                }
              : msg
          )
        );
      });

      eventSource.addEventListener("tool_result", (event: any) => {
        const payload = JSON.parse(event.data);
        setMessages((prev) =>
          prev.map((msg) =>
            msg.id === assistantMsgId
              ? {
                  ...msg,
                  toolCalls: (msg.toolCalls || []).map((t, idx) =>
                    idx === (msg.toolCalls || []).length - 1
                      ? { ...t, result: payload.result }
                      : t
                  ),
                }
              : msg
          )
        );
      });

      eventSource.addEventListener("widget", (event: any) => {
        const widgetPayload = JSON.parse(event.data);
        setMessages((prev) =>
          prev.map((msg) =>
            msg.id === assistantMsgId
              ? {
                  ...msg,
                  widgets: [...(msg.widgets || []), widgetPayload],
                }
              : msg
          )
        );
      });

      eventSource.addEventListener("token", (event: any) => {
        const tokenPayload = JSON.parse(event.data);
        setMessages((prev) =>
          prev.map((msg) =>
            msg.id === assistantMsgId
              ? { ...msg, content: msg.content + tokenPayload.token }
              : msg
          )
        );
      });

      eventSource.addEventListener("final", (event: any) => {
        const finalPayload = JSON.parse(event.data);
        setMessages((prev) =>
          prev.map((msg) =>
            msg.id === assistantMsgId
              ? {
                  ...msg,
                  content: finalPayload.full_answer,
                  citations: finalPayload.citations || [],
                  badge: finalPayload.data_source_badge,
                }
              : msg
          )
        );
        eventSource.close();
        setIsStreaming(false);
      });

      eventSource.onerror = () => {
        eventSource.close();
        setIsStreaming(false);
      };
    } catch (err) {
      console.error("Stream connection failed:", err);
      setIsStreaming(false);
    }
  };

  const samplePrompts = [
    "Simulate a 90-day Monte Carlo jump diffusion scenario on NVDA",
    "Calculate the 5-factor Stock DNA radar profile for AAPL",
    "Search SEC 10-K disclosures regarding Apple supply chain & silicon risk",
    "What are the latest detected volatility anomalies and market stress levels?",
  ];

  return (
    <div className="flex flex-col h-[780px] bg-white rounded-xl border border-border shadow-sm overflow-hidden">
      {/* Header */}
      <div className="px-6 py-3.5 bg-slate-50 border-b border-border flex items-center justify-between">
        <div className="flex items-center gap-2.5">
          <div className="w-8 h-8 rounded-lg bg-primary text-white flex items-center justify-center font-bold">
            <Sparkles className="w-4 h-4 text-gold" />
          </div>
          <div>
            <h3 className="text-sm font-bold text-slate-900">AI Quantitative Research Co-Pilot</h3>
            <p className="text-[11px] text-slate-500">
              LangGraph StateGraph Agent • Gemini 1.5 • SEC RAG Retrieval
            </p>
          </div>
        </div>
        <div className="flex items-center gap-2 text-xs">
          <span className="inline-flex items-center gap-1 px-2.5 py-1 rounded-full text-[10px] font-semibold bg-emerald-50 text-primary border border-emerald-200">
            ● AGENT READY
          </span>
        </div>
      </div>

      {/* Messages Scroll Area */}
      <div className="flex-1 p-6 overflow-y-auto space-y-6">
        {messages.map((msg) => (
          <div
            key={msg.id}
            className={`flex flex-col ${msg.role === "user" ? "items-end" : "items-start"}`}
          >
            <div className="flex items-center gap-2 mb-1.5 px-1">
              <span className="text-[11px] font-bold text-slate-600 font-mono">
                {msg.role === "user" ? "YOU (ANALYST)" : "MARKETMIND AGENT"}
              </span>
              {msg.badge && (
                <span className="text-[9px] px-1.5 py-0.5 rounded font-mono font-bold bg-slate-100 text-slate-700 border border-slate-200">
                  {msg.badge}
                </span>
              )}
            </div>

            {/* Thought Chain Accordion */}
            {msg.thoughts && msg.thoughts.length > 0 && (
              <div className="mb-2 w-full max-w-2xl bg-slate-50 border border-slate-200 rounded-lg p-2.5 text-xs font-mono space-y-1">
                <div className="text-[10px] font-bold text-slate-400 uppercase tracking-wider flex items-center gap-1.5">
                  <Cpu className="w-3 h-3 text-primary" /> Reasoning Chain & Tool Dispatches
                </div>
                {msg.thoughts.map((th, idx) => (
                  <div key={idx} className="text-slate-600 pl-4 border-l-2 border-primary/30 text-[11px]">
                    {th}
                  </div>
                ))}
              </div>
            )}

            {/* Tool Calls Badges */}
            {msg.toolCalls && msg.toolCalls.length > 0 && (
              <div className="mb-2 flex flex-wrap gap-2 max-w-2xl">
                {msg.toolCalls.map((t, idx) => (
                  <div
                    key={idx}
                    className="flex items-center gap-1.5 px-2.5 py-1 rounded bg-amber-50 border border-amber-200 text-amber-900 text-xs font-mono"
                  >
                    <Database className="w-3 h-3 text-amber-600" />
                    <span className="font-semibold">{t.tool}</span>
                    {t.result && (
                      <span className="text-[10px] text-amber-700 font-medium">({t.result})</span>
                    )}
                  </div>
                ))}
              </div>
            )}

            {/* Message Bubble */}
            <div
              className={`max-w-3xl rounded-xl p-4 text-sm leading-relaxed shadow-sm ${
                msg.role === "user"
                  ? "bg-primary text-white"
                  : "bg-surface-subtle border border-border text-slate-800"
              }`}
            >
              <div className="whitespace-pre-wrap font-sans">{msg.content}</div>

              {/* Render Inline Widgets if attached */}
              {msg.widgets && msg.widgets.length > 0 && (
                <div className="mt-4 space-y-4 pt-3 border-t border-slate-200">
                  {msg.widgets.map((w, idx) => {
                    if (w.widget_type === "FAN_CHART") {
                      return <FanChart key={idx} data={w.data} height={280} />;
                    }
                    if (w.widget_type === "RADAR_DNA") {
                      return <StockDNARadar key={idx} data={w.data} height={280} />;
                    }
                    return null;
                  })}
                </div>
              )}

              {/* Render Citations if attached */}
              {msg.citations && msg.citations.length > 0 && (
                <div className="mt-4 pt-3 border-t border-slate-200 space-y-2">
                  <div className="text-xs font-bold text-slate-700 flex items-center gap-1.5">
                    <FileText className="w-3.5 h-3.5 text-primary" /> Verified Regulatory SEC Citations:
                  </div>
                  <div className="grid grid-cols-1 gap-2">
                    {msg.citations.map((c: any) => (
                      <div
                        key={c.id}
                        className="p-2.5 bg-white border border-slate-200 rounded-lg text-xs space-y-1"
                      >
                        <div className="flex items-center justify-between text-[11px] font-bold text-primary font-mono">
                          <span>
                            {c.ticker} {c.filing_type} (FY{c.fiscal_year})
                          </span>
                          <span>Page {c.page_number}</span>
                        </div>
                        <p className="text-slate-600 italic font-serif">"{c.content_snippet}"</p>
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </div>
          </div>
        ))}

        {isStreaming && (
          <div className="flex items-center gap-2 text-xs font-mono text-primary animate-pulse">
            <Loader2 className="w-4 h-4 animate-spin" />
            <span>Agent synthesizing quantitative analysis...</span>
          </div>
        )}
        <div ref={messagesEndRef} />
      </div>

      {/* Suggested Prompts Marquee */}
      <div className="px-6 py-2 bg-slate-50 border-t border-border flex items-center gap-2 overflow-x-auto no-scrollbar">
        <span className="text-[10px] font-bold text-slate-400 font-mono uppercase shrink-0">PROMPTS:</span>
        {samplePrompts.map((p, idx) => (
          <button
            key={idx}
            onClick={() => {
              setInputQuery(p);
            }}
            className="px-2.5 py-1 rounded bg-white hover:bg-slate-100 border border-slate-200 text-slate-700 text-xs whitespace-nowrap transition"
          >
            {p}
          </button>
        ))}
      </div>

      {/* Input Box */}
      <form onSubmit={handleSend} className="p-4 bg-white border-t border-border flex items-center gap-3">
        <input
          type="text"
          value={inputQuery}
          onChange={(e) => setInputQuery(e.target.value)}
          placeholder="Ask AI: 'Simulate a 90d Monte Carlo on AAPL', 'Factor DNA for NVDA', 'SEC Risk Factors'..."
          disabled={isStreaming}
          className="flex-1 px-4 py-2.5 rounded-lg border border-border focus:outline-none focus:ring-2 focus:ring-primary/40 text-sm font-sans bg-slate-50"
        />
        <button
          type="submit"
          disabled={isStreaming || !inputQuery.trim()}
          className="px-5 py-2.5 rounded-lg bg-primary hover:bg-primary-hover disabled:opacity-50 text-white font-semibold text-xs flex items-center gap-2 shadow-sm transition"
        >
          <span>Run Agent</span>
          <Send className="w-3.5 h-3.5" />
        </button>
      </form>
    </div>
  );
}
