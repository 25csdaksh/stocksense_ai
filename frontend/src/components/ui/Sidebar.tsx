"use client";

import React from "react";
import Link from "next/link";
import { usePathname } from "next/navigation";
import {
  LayoutDashboard,
  CandlestickChart,
  FlaskConical,
  Network,
  Bot,
  ShieldCheck,
  FileText,
  HelpCircle,
} from "lucide-react";

export default function Sidebar() {
  const pathname = usePathname();

  const navItems = [
    { label: "Market Pulse", href: "/", icon: LayoutDashboard },
    { label: "Stock Workspace", href: "/workspace/NVDA", icon: CandlestickChart },
    { label: "Scenario Simulator", href: "/simulator", icon: FlaskConical },
    { label: "Relationship Graph", href: "/relationships", icon: Network },
    { label: "AI Multi-Agent RAG", href: "/research", icon: Bot },
    { label: "Portfolio Risk & Stress", href: "/portfolio", icon: ShieldCheck },
  ];

  return (
    <aside className="w-64 bg-white border-r border-border flex flex-col justify-between shrink-0 min-h-[calc(100vh-5rem)]">
      <div className="p-4 space-y-6">
        <div>
          <div className="px-3 mb-2 text-[11px] font-bold text-slate-400 uppercase tracking-wider font-mono">
            ANALYTICS SUITE
          </div>
          <nav className="space-y-1">
            {navItems.map((item) => {
              const Icon = item.icon;
              const isActive =
                item.href === "/"
                  ? pathname === "/"
                  : pathname?.startsWith(item.href.split("/")[1]);

              return (
                <Link
                  key={item.href}
                  href={item.href}
                  className={`flex items-center gap-3 px-3 py-2.5 rounded-lg text-xs font-semibold transition ${
                    isActive
                      ? "bg-primary text-white shadow-sm"
                      : "text-slate-600 hover:text-slate-900 hover:bg-surface"
                  }`}
                >
                  <Icon className={`w-4 h-4 ${isActive ? "text-gold" : "text-slate-400"}`} />
                  <span>{item.label}</span>
                </Link>
              );
            })}
          </nav>
        </div>

        <div>
          <div className="px-3 mb-2 text-[11px] font-bold text-slate-400 uppercase tracking-wider font-mono">
            MONITORED UNIVERSE
          </div>
          <div className="grid grid-cols-3 gap-1.5 px-2">
            {["AAPL", "MSFT", "NVDA", "GOOGL", "AMZN", "TSLA", "JPM", "SPY", "QQQ"].map((sym) => (
              <Link
                key={sym}
                href={`/workspace/${sym}`}
                className="px-2 py-1.5 text-center text-xs font-mono font-bold rounded bg-surface-subtle hover:bg-emerald-50 hover:text-primary hover:border-emerald-200 border border-border text-slate-700 transition"
              >
                {sym}
              </Link>
            ))}
          </div>
        </div>
      </div>

      {/* Footer Info */}
      <div className="p-4 border-t border-border bg-slate-50/50 text-[11px] text-slate-500 space-y-2">
        <div className="flex items-center justify-between">
          <span className="font-semibold text-slate-700">Model Engine:</span>
          <span className="font-mono text-[10px] bg-slate-200 text-slate-800 px-1.5 py-0.5 rounded">
            Gemini 1.5 + LangGraph
          </span>
        </div>
        <div className="flex items-center justify-between">
          <span className="font-semibold text-slate-700">Quant Vector:</span>
          <span className="font-mono text-[10px] bg-slate-200 text-slate-800 px-1.5 py-0.5 rounded">
            Qdrant + GARCH
          </span>
        </div>
      </div>
    </aside>
  );
}
