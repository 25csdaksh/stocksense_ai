"use client";

import React from "react";
import { cn } from "@/lib/utils";

export interface TabItem {
  id: string;
  label: string;
  count?: number;
  icon?: React.ReactNode;
}

export interface TabsProps {
  tabs: TabItem[];
  activeTab: string;
  onChange: (tabId: string) => void;
  className?: string;
}

export const Tabs: React.FC<TabsProps> = ({ tabs, activeTab, onChange, className }) => {
  return (
    <div className={cn("flex items-center gap-1 border-b border-border overflow-x-auto", className)}>
      {tabs.map((tab) => {
        const isActive = tab.id === activeTab;
        return (
          <button
            key={tab.id}
            onClick={() => onChange(tab.id)}
            className={cn(
              "flex items-center gap-2 py-2.5 px-3.5 text-xs font-semibold tracking-wide transition-all border-b-2 -mb-px whitespace-nowrap",
              isActive
                ? "border-primary text-primary"
                : "border-transparent text-content-muted hover:text-content hover:border-border"
            )}
          >
            {tab.icon && <span className="w-4 h-4 inline-flex items-center">{tab.icon}</span>}
            <span>{tab.label}</span>
            {tab.count !== undefined && (
              <span
                className={cn(
                  "px-1.5 py-0.2 rounded-full text-[10px] font-bold",
                  isActive ? "bg-primary-light text-primary" : "bg-surface-subtle text-content-muted"
                )}
              >
                {tab.count}
              </span>
            )}
          </button>
        );
      })}
    </div>
  );
};
