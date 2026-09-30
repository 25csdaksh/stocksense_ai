"use client";

import React from "react";
import { cn } from "@/lib/utils";
import { Clock, CheckCircle2, AlertTriangle, Radio, ShieldAlert } from "lucide-react";

export type FreshnessState = "LIVE" | "FRESH" | "STALE" | "DEMO" | "UNAVAILABLE";

interface DataFreshnessBadgeProps {
  status?: FreshnessState | string;
  dataSource?: string;
  dataStatus?: string;
  lastUpdated?: string;
  ageSeconds?: number;
  className?: string;
  showAge?: boolean;
}

export const DataFreshnessBadge: React.FC<DataFreshnessBadgeProps> = ({
  status = "DEMO",
  dataSource,
  dataStatus,
  lastUpdated,
  ageSeconds,
  className,
  showAge = true,
}) => {
  // Normalize state from data provenance
  let effectiveStatus: FreshnessState = "DEMO";
  const upperStatus = status.toUpperCase();

  if (upperStatus === "LIVE" || (dataStatus && dataStatus.toUpperCase() === "LIVE")) {
    effectiveStatus = "LIVE";
  } else if (upperStatus === "FRESH") {
    effectiveStatus = "FRESH";
  } else if (upperStatus === "STALE") {
    effectiveStatus = "STALE";
  } else if (upperStatus === "UNAVAILABLE") {
    effectiveStatus = "UNAVAILABLE";
  } else {
    effectiveStatus = "DEMO";
  }

  // Formatting Age string
  const formatAge = (sec?: number, ts?: string) => {
    if (sec !== undefined && sec !== null) {
      if (sec < 60) return `${Math.round(sec)}s ago`;
      if (sec < 3600) return `${Math.round(sec / 60)}m ago`;
      if (sec < 86400) return `${Math.round(sec / 3600)}h ago`;
      return `${Math.round(sec / 86400)}d ago`;
    }
    if (ts) {
      try {
        const diff = Math.max(0, (Date.now() - new Date(ts).getTime()) / 1000);
        if (diff < 60) return `${Math.round(diff)}s ago`;
        if (diff < 3600) return `${Math.round(diff / 60)}m ago`;
        if (diff < 86400) return `${Math.round(diff / 3600)}h ago`;
        return `${Math.round(diff / 86400)}d ago`;
      } catch {
        return "Unknown";
      }
    }
    return "Real-time";
  };

  const getStyle = () => {
    switch (effectiveStatus) {
      case "LIVE":
        return {
          bg: "bg-emerald-500/10 text-emerald-700 border-emerald-500/30 dark:text-emerald-400",
          dot: "bg-emerald-500 animate-pulse",
          icon: Radio,
          label: "LIVE STREAM",
        };
      case "FRESH":
        return {
          bg: "bg-teal-500/10 text-teal-700 border-teal-500/30 dark:text-teal-400",
          dot: "bg-teal-500",
          icon: CheckCircle2,
          label: "FRESH DATA",
        };
      case "STALE":
        return {
          bg: "bg-amber-500/10 text-amber-700 border-amber-500/30 dark:text-amber-400",
          dot: "bg-amber-500 animate-ping",
          icon: AlertTriangle,
          label: "STALE DATA",
        };
      case "UNAVAILABLE":
        return {
          bg: "bg-rose-500/10 text-rose-700 border-rose-500/30 dark:text-rose-400",
          dot: "bg-rose-500",
          icon: ShieldAlert,
          label: "UNAVAILABLE",
        };
      case "DEMO":
      default:
        return {
          bg: "bg-primary-light/40 text-primary-dark border-primary/20",
          dot: "bg-accent",
          icon: Clock,
          label: "DEMO SIMULATED",
        };
    }
  };

  const config = getStyle();
  const Icon = config.icon;

  return (
    <div
      className={cn(
        "inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-[11px] font-semibold tracking-wide border shadow-2xs backdrop-blur-xs transition-colors",
        config.bg,
        className
      )}
      title={`Data Source: ${dataSource || "Internal"} | Data Status: ${effectiveStatus}`}
    >
      <span className={cn("w-1.5 h-1.5 rounded-full shrink-0", config.dot)} />
      <span className="font-mono text-[10px] tracking-wider uppercase">{config.label}</span>
      {showAge && (
        <>
          <span className="text-content-muted/50 font-sans">•</span>
          <span className="text-[10px] font-mono text-content-muted">
            {formatAge(ageSeconds, lastUpdated)}
          </span>
        </>
      )}
    </div>
  );
};
