"use client";

import React from "react";
import { GlobalSearchResultItem } from "@/types";
import { Badge } from "@/components/common/Badge";
import {
  TrendingUp,
  Newspaper,
  AlertTriangle,
  Briefcase,
  CornerDownLeft,
  LayoutDashboard,
  Brain,
  Activity,
  Bookmark,
  Settings,
  Sparkles,
} from "lucide-react";
import { formatCurrency } from "@/lib/utils";

interface SearchResultItemProps {
  item: GlobalSearchResultItem;
  isActive: boolean;
  onSelect: () => void;
}

export const SearchResultItem: React.FC<SearchResultItemProps> = ({
  item,
  isActive,
  onSelect,
}) => {
  const getActionIcon = (iconName: string) => {
    switch (iconName) {
      case "LayoutDashboard":
        return <LayoutDashboard className="w-4 h-4 text-primary" />;
      case "TrendingUp":
        return <TrendingUp className="w-4 h-4 text-primary" />;
      case "Brain":
        return <Brain className="w-4 h-4 text-primary" />;
      case "AlertTriangle":
        return <AlertTriangle className="w-4 h-4 text-financial-loss" />;
      case "Activity":
        return <Activity className="w-4 h-4 text-secondary" />;
      case "Briefcase":
        return <Briefcase className="w-4 h-4 text-primary" />;
      case "Bookmark":
        return <Bookmark className="w-4 h-4 text-secondary" />;
      case "Newspaper":
        return <Newspaper className="w-4 h-4 text-primary" />;
      default:
        return <Settings className="w-4 h-4 text-content-muted" />;
    }
  };

  return (
    <div
      onClick={onSelect}
      className={`flex items-center justify-between p-3 rounded-xl transition-all cursor-pointer group ${
        isActive
          ? "bg-primary/10 border border-primary/30 shadow-sm"
          : "hover:bg-surface-subtle border border-transparent"
      }`}
    >
      {/* STOCK Item */}
      {item.type === "STOCK" && (
        <div className="flex items-center gap-3 min-w-0 flex-1">
          <div className="w-8 h-8 rounded-lg bg-surface border border-border flex items-center justify-center font-bold text-xs text-primary shrink-0">
            <TrendingUp className="w-4 h-4" />
          </div>
          <div className="min-w-0 flex-1">
            <div className="flex items-center gap-2">
              <span className="text-xs font-bold text-content truncate">{item.ticker}</span>
              {item.is_demo ? (
                <Badge variant="gold" size="sm">
                  DEMO
                </Badge>
              ) : (
                <Badge variant="primary" size="sm">
                  {item.exchange}
                </Badge>
              )}
            </div>
            <p className="text-[11px] text-content-muted truncate">{item.name}</p>
          </div>
        </div>
      )}

      {/* ACTION Item */}
      {item.type === "ACTION" && (
        <div className="flex items-center gap-3 min-w-0 flex-1">
          <div className="w-8 h-8 rounded-lg bg-primary/10 flex items-center justify-center shrink-0">
            {getActionIcon(item.iconName)}
          </div>
          <div className="min-w-0 flex-1">
            <div className="flex items-center gap-2">
              <span className="text-xs font-bold text-content truncate">{item.label}</span>
              <Badge variant="gold" size="sm">
                {item.category}
              </Badge>
            </div>
            <p className="text-[11px] text-content-muted truncate">{item.description}</p>
          </div>
        </div>
      )}

      {/* NEWS Item */}
      {item.type === "NEWS" && (
        <div className="flex items-center gap-3 min-w-0 flex-1">
          <div className="w-8 h-8 rounded-lg bg-surface border border-border flex items-center justify-center shrink-0 text-primary">
            <Newspaper className="w-4 h-4" />
          </div>
          <div className="min-w-0 flex-1">
            <div className="flex items-center gap-2">
              <span className="text-xs font-bold text-content truncate">{item.title}</span>
              <Badge
                variant={
                  item.sentiment === "POSITIVE" || item.sentiment === "BULLISH"
                    ? "gain"
                    : item.sentiment === "NEGATIVE" || item.sentiment === "BEARISH"
                    ? "loss"
                    : "neutral"
                }
                size="sm"
              >
                {item.sentiment}
              </Badge>
            </div>
            <p className="text-[11px] text-content-muted truncate">
              {item.source} • {item.time} {item.ticker && `• ${item.ticker}`}
            </p>
          </div>
        </div>
      )}

      {/* ANOMALY Item */}
      {item.type === "ANOMALY" && (
        <div className="flex items-center gap-3 min-w-0 flex-1">
          <div className="w-8 h-8 rounded-lg bg-financial-loss/10 flex items-center justify-center shrink-0 text-financial-loss">
            <AlertTriangle className="w-4 h-4" />
          </div>
          <div className="min-w-0 flex-1">
            <div className="flex items-center gap-2">
              <span className="text-xs font-bold text-content truncate">{item.ticker}</span>
              <Badge variant="loss" size="sm">
                {item.severity} SEVERITY
              </Badge>
            </div>
            <p className="text-[11px] text-content-muted truncate">
              {item.anomaly_type} • Outlier Detected
            </p>
          </div>
        </div>
      )}

      {/* PORTFOLIO Item */}
      {item.type === "PORTFOLIO" && (
        <div className="flex items-center gap-3 min-w-0 flex-1">
          <div className="w-8 h-8 rounded-lg bg-primary/10 flex items-center justify-center shrink-0 text-primary">
            <Briefcase className="w-4 h-4" />
          </div>
          <div className="min-w-0 flex-1">
            <div className="flex items-center gap-2">
              <span className="text-xs font-bold text-content truncate">{item.ticker}</span>
              <span className={`text-[11px] font-bold font-tabular ${item.pnl_pct >= 0 ? "text-financial-gain" : "text-financial-loss"}`}>
                {item.pnl_pct >= 0 ? `+` : ``}{item.pnl_pct.toFixed(2)}%
              </span>
            </div>
            <p className="text-[11px] text-content-muted truncate">
              Holding: {item.shares} shs • {formatCurrency(item.value, "INR")}
            </p>
          </div>
        </div>
      )}

      <div className="shrink-0 ml-3">
        <CornerDownLeft
          className={`w-4 h-4 transition-opacity ${
            isActive ? "text-primary opacity-100" : "text-content-muted opacity-0 group-hover:opacity-100"
          }`}
        />
      </div>
    </div>
  );
};
