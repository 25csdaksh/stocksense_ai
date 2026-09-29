"use client";

import React, { useState } from "react";
import Link from "next/link";
import { useAuth } from "@/hooks/useAuth";
import { Button } from "@/components/common/Button";
import { Dropdown } from "@/components/common/Dropdown";
import { GlobalSearch } from "@/components/navigation/GlobalSearch";
import { Search, Menu, User as UserIcon, LogOut, ShieldCheck, ChevronDown, Activity } from "lucide-react";

export interface HeaderProps {
  onToggleMobileSidebar: () => void;
}

export const Header: React.FC<HeaderProps> = ({ onToggleMobileSidebar }) => {
  const { user, isAuthenticated, logout } = useAuth();
  const [isSearchOpen, setIsSearchOpen] = useState(false);

  // Fallback indices preview
  const liveIndices = [
    { label: "NIFTY 50", value: "24,836.10", change: "+0.45%", isUp: true },
    { label: "SENSEX", value: "81,332.72", change: "+0.38%", isUp: true },
    { label: "NIFTY BANK", value: "51,215.30", change: "-0.12%", isUp: false },
  ];

  const profileDropdownItems = [
    {
      id: "profile",
      label: user?.username ? `@${user.username}` : "Profile",
      icon: <UserIcon className="w-4 h-4 text-primary" />,
      onClick: () => {},
    },
    {
      id: "admin",
      label: "System Status",
      icon: <ShieldCheck className="w-4 h-4 text-secondary" />,
      onClick: () => {},
    },
    "divider" as const,
    {
      id: "logout",
      label: "Sign Out",
      icon: <LogOut className="w-4 h-4" />,
      variant: "danger" as const,
      onClick: () => logout(),
    },
  ];

  return (
    <>
      <header className="sticky top-0 z-30 bg-surface/90 backdrop-blur-md border-b border-border px-4 lg:px-8 py-3 flex items-center justify-between gap-4">
        {/* Left: Mobile Toggle & Ticker */}
        <div className="flex items-center gap-4">
          <button
            onClick={onToggleMobileSidebar}
            className="p-2 rounded-lg text-content-muted hover:text-content hover:bg-surface-subtle md:hidden"
            aria-label="Toggle Navigation"
          >
            <Menu className="w-5 h-5" />
          </button>

          {/* Real-time Market Status Ticker */}
          <div className="hidden lg:flex items-center gap-4 text-xs font-semibold">
            <div className="flex items-center gap-1.5 px-2.5 py-1 rounded-full bg-financial-gain-bg border border-financial-gain/20 text-financial-gain">
              <Activity className="w-3.5 h-3.5 animate-pulse" />
              <span className="text-[11px] font-bold">NSE / BSE LIVE</span>
            </div>

            <div className="flex items-center gap-3">
              {liveIndices.map((idx) => (
                <div key={idx.label} className="flex items-center gap-1.5 font-tabular">
                  <span className="text-content-muted text-[11px]">{idx.label}</span>
                  <span className="text-content font-bold text-xs">{idx.value}</span>
                  <span
                    className={`text-[10px] font-bold ${
                      idx.isUp ? "text-financial-gain" : "text-financial-loss"
                    }`}
                  >
                    {idx.change}
                  </span>
                </div>
              ))}
            </div>
          </div>
        </div>

        {/* Center: Global Search Trigger Button */}
        <div className="flex-1 max-w-md">
          <button
            onClick={() => setIsSearchOpen(true)}
            className="w-full flex items-center justify-between px-3.5 py-1.5 rounded-xl border border-border bg-surface-subtle/70 text-content-muted hover:bg-surface-subtle hover:border-content-muted/30 transition-all text-xs"
          >
            <div className="flex items-center gap-2">
              <Search className="w-3.5 h-3.5 text-primary" />
              <span>Search stocks (TCS, RELIANCE), AI research...</span>
            </div>
            <kbd className="hidden sm:inline-flex items-center gap-0.5 px-1.5 py-0.5 text-[10px] font-mono font-semibold text-content-muted bg-surface border border-border rounded shadow-xs">
              <span className="text-[9px]">⌘</span>K
            </kbd>
          </button>
        </div>

        {/* Right: Auth / Profile */}
        <div className="flex items-center gap-3">
          {isAuthenticated ? (
            <Dropdown
              trigger={
                <div className="flex items-center gap-2 p-1.5 pr-2.5 rounded-full border border-border bg-surface hover:bg-surface-subtle transition-colors cursor-pointer">
                  <div className="w-7 h-7 rounded-full bg-primary text-accent font-bold text-xs flex items-center justify-center">
                    {user?.username ? user.username.charAt(0).toUpperCase() : "U"}
                  </div>
                  <span className="text-xs font-semibold text-content hidden sm:inline">
                    {user?.username}
                  </span>
                  <ChevronDown className="w-3.5 h-3.5 text-content-muted" />
                </div>
              }
              items={profileDropdownItems}
            />
          ) : (
            <div className="flex items-center gap-2">
              <Link href="/login">
                <Button variant="ghost" size="sm">
                  Sign In
                </Button>
              </Link>
              <Link href="/register">
                <Button variant="gold" size="sm">
                  Get Started
                </Button>
              </Link>
            </div>
          )}
        </div>
      </header>

      {/* Global Search Dialog */}
      <GlobalSearch isOpen={isSearchOpen} onClose={() => setIsSearchOpen(false)} />
    </>
  );
};
