"use client";

import React from "react";
import Link from "next/link";
import { usePathname } from "next/navigation";
import { cn } from "@/lib/utils";
import {
  LayoutDashboard,
  TrendingUp,
  Brain,
  AlertTriangle,
  Activity,
  Briefcase,
  Bookmark,
  Newspaper,
  Settings,
  Sparkles,
} from "lucide-react";

const NAV_ITEMS = [
  { label: "Dashboard", href: "/dashboard", icon: LayoutDashboard },
  { label: "Market & Stocks", href: "/stocks", icon: TrendingUp },
  { label: "AI Research", href: "/research", icon: Brain, badge: "LangGraph" },
  { label: "Anomalies", href: "/anomalies", icon: AlertTriangle },
  { label: "Scenarios", href: "/scenarios", icon: Activity },
  { label: "Portfolio", href: "/portfolio", icon: Briefcase },
  { label: "Watchlist", href: "/watchlist", icon: Bookmark },
  { label: "News Feed", href: "/news", icon: Newspaper },
];

const BOTTOM_ITEMS = [
  { label: "Settings", href: "/settings", icon: Settings },
];

export interface SidebarProps {
  className?: string;
  isOpenMobile?: boolean;
  onCloseMobile?: () => void;
}

export const Sidebar: React.FC<SidebarProps> = ({ className, isOpenMobile = false, onCloseMobile }) => {
  const pathname = usePathname();

  return (
    <>
      {/* Mobile Backdrop */}
      {isOpenMobile && (
        <div
          className="fixed inset-0 z-40 bg-primary-dark/40 backdrop-blur-sm md:hidden"
          onClick={onCloseMobile}
        />
      )}

      <aside
        className={cn(
          "w-64 bg-surface border-r border-border flex flex-col justify-between h-screen fixed top-0 left-0 z-40 transition-transform duration-200 ease-in-out md:translate-x-0 md:sticky",
          isOpenMobile ? "translate-x-0" : "-translate-x-full",
          className
        )}
      >
        {/* Brand Header */}
        <div className="p-5 border-b border-border flex items-center justify-between">
          <Link href="/dashboard" className="flex items-center gap-2.5">
            <div className="w-9 h-9 rounded-xl bg-primary flex items-center justify-center text-accent shadow-sm">
              <Sparkles className="w-5 h-5 fill-accent" />
            </div>
            <div>
              <div className="flex items-center gap-1.5">
                <span className="font-extrabold text-sm tracking-tight text-primary">MARKETMIND</span>
                <span className="text-[10px] font-bold px-1.5 py-0.2 rounded bg-accent-light text-accent-dark border border-accent/30">
                  AI
                </span>
              </div>
              <p className="text-[10px] text-content-muted font-medium">Financial Intelligence</p>
            </div>
          </Link>
        </div>

        {/* Navigation Items */}
        <div className="flex-1 overflow-y-auto px-3 py-4 space-y-1">
          <div className="px-3 pb-2 text-[10px] font-bold uppercase tracking-wider text-content-muted">
            Intelligence Suite
          </div>

          {NAV_ITEMS.map((item) => {
            const Icon = item.icon;
            const isActive = pathname === item.href || (item.href !== "/" && pathname.startsWith(item.href));

            return (
              <Link
                key={item.href}
                href={item.href}
                onClick={onCloseMobile}
                className={cn(
                  "flex items-center justify-between px-3 py-2.5 rounded-xl text-xs font-semibold transition-all group",
                  isActive
                    ? "bg-primary text-white shadow-sm"
                    : "text-content hover:bg-surface-subtle hover:text-primary"
                )}
              >
                <div className="flex items-center gap-3">
                  <Icon
                    className={cn(
                      "w-4 h-4 transition-colors",
                      isActive ? "text-accent" : "text-content-muted group-hover:text-primary"
                    )}
                  />
                  <span>{item.label}</span>
                </div>
                {item.badge && (
                  <span
                    className={cn(
                      "text-[9px] font-bold px-1.5 py-0.5 rounded uppercase tracking-wider",
                      isActive
                        ? "bg-primary-hover text-accent border border-accent/20"
                        : "bg-surface-subtle text-content-muted border border-border"
                    )}
                  >
                    {item.badge}
                  </span>
                )}
              </Link>
            );
          })}
        </div>

        {/* Bottom Section */}
        <div className="p-3 border-t border-border space-y-1">
          {BOTTOM_ITEMS.map((item) => {
            const Icon = item.icon;
            const isActive = pathname === item.href;

            return (
              <Link
                key={item.href}
                href={item.href}
                onClick={onCloseMobile}
                className={cn(
                  "flex items-center gap-3 px-3 py-2.5 rounded-xl text-xs font-semibold transition-all",
                  isActive
                    ? "bg-primary text-white"
                    : "text-content hover:bg-surface-subtle hover:text-primary"
                )}
              >
                <Icon className="w-4 h-4 text-content-muted" />
                <span>{item.label}</span>
              </Link>
            );
          })}

          <div className="mt-3 p-3 rounded-xl bg-surface-subtle/70 border border-border flex items-center justify-between">
            <div className="flex items-center gap-2">
              <div className="w-2 h-2 rounded-full bg-financial-gain animate-pulse" />
              <span className="text-[11px] font-semibold text-content">Market Engine</span>
            </div>
            <span className="text-[10px] font-mono font-medium text-content-muted">v4.0.0</span>
          </div>
        </div>
      </aside>
    </>
  );
};
