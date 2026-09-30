/**
 * MarketMind AI — Global Real-Time Connection & Data Provenance Status Indicator.
 * Renders connection status (Connected, Reconnecting, Offline) and strict data provenance (LIVE vs DEMO vs STALE).
 */
"use client";

import React, { useState, useEffect } from "react";
import { useRealtimeConnectionState } from "@/hooks/useRealtimeSelectors";
import { Activity, RefreshCw, AlertCircle, WifiOff } from "lucide-react";

export interface RealtimeStatusIndicatorProps {
  compact?: boolean;
  showTime?: boolean;
  className?: string;
}

export const RealtimeStatusIndicator: React.FC<RealtimeStatusIndicatorProps> = ({
  compact = false,
  showTime = true,
  className = "",
}) => {
  const { status, dataStatus, lastEventAt, isStale } = useRealtimeConnectionState();
  const [timeAgo, setTimeAgo] = useState<string>("");

  useEffect(() => {
    const update = () => {
      if (!lastEventAt) {
        setTimeAgo("");
        return;
      }
      const diffSec = Math.floor((Date.now() - lastEventAt.getTime()) / 1000);
      if (diffSec < 5) {
        setTimeAgo("just now");
      } else if (diffSec < 60) {
        setTimeAgo(`${diffSec}s ago`);
      } else {
        const mins = Math.floor(diffSec / 60);
        setTimeAgo(`${mins}m ago`);
      }
    };

    update();
    const interval = setInterval(update, 3000);
    return () => clearInterval(interval);
  }, [lastEventAt]);

  // Determine Badge Styling & Label
  let badgeStyle = "bg-surface-subtle text-content-muted border-border";
  let dotStyle = "bg-content-muted";
  let label = "Offline";
  let icon = <WifiOff className="w-3 h-3" />;

  if (status === "CONNECTED") {
    if (isStale) {
      badgeStyle = "bg-amber-500/10 text-amber-600 border-amber-500/20";
      dotStyle = "bg-amber-500";
      label = "STALE FEED";
      icon = <AlertCircle className="w-3 h-3 text-amber-500" />;
    } else if (dataStatus === "LIVE") {
      badgeStyle = "bg-financial-gain-bg text-financial-gain border-financial-gain/20";
      dotStyle = "bg-financial-gain animate-pulse";
      label = "LIVE STREAM";
      icon = <Activity className="w-3 h-3 text-financial-gain animate-pulse" />;
    } else {
      // DEMO mode
      badgeStyle = "bg-accent/10 text-accent-dark border-accent/20";
      dotStyle = "bg-accent animate-pulse";
      label = "DEMO DATA";
      icon = <Activity className="w-3 h-3 text-accent" />;
    }
  } else if (status === "RECONNECTING") {
    badgeStyle = "bg-amber-500/10 text-amber-600 border-amber-500/20";
    dotStyle = "bg-amber-500";
    label = "RECONNECTING";
    icon = <RefreshCw className="w-3 h-3 text-amber-500 animate-spin" />;
  } else if (status === "CONNECTING") {
    badgeStyle = "bg-surface-subtle text-content-muted border-border";
    dotStyle = "bg-content-muted animate-pulse";
    label = "CONNECTING...";
    icon = <Activity className="w-3 h-3 text-content-muted animate-pulse" />;
  }

  if (compact) {
    return (
      <div
        className={`inline-flex items-center gap-1.5 px-2 py-0.5 rounded-full text-[11px] font-bold font-mono border ${badgeStyle} ${className}`}
        title={`Status: ${status} • Data: ${dataStatus} • ${timeAgo ? `Last event ${timeAgo}` : "No events"}`}
      >
        <span className={`w-1.5 h-1.5 rounded-full ${dotStyle}`} />
        <span>{label}</span>
      </div>
    );
  }

  return (
    <div
      className={`inline-flex items-center gap-2 px-2.5 py-1 rounded-full text-xs font-semibold border ${badgeStyle} ${className}`}
    >
      <div className="flex items-center gap-1.5">
        {icon}
        <span className="text-[11px] font-bold font-mono tracking-tight">{label}</span>
      </div>
      {showTime && timeAgo && status === "CONNECTED" && (
        <span className="text-[10px] text-content-muted font-normal font-sans border-l border-border/60 pl-1.5">
          {timeAgo}
        </span>
      )}
    </div>
  );
};
