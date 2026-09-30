/**
 * MarketMind AI — Market Session & Exchange Status Indicator.
 * Displays session state (Open, Pre-Market, Closed) for NSE/BSE/US exchanges with real-time updates.
 */
"use client";

import React from "react";
import { useRealtimeMarketStatus } from "@/hooks/useRealtimeSelectors";

export interface MarketStatusIndicatorProps {
  exchange?: string;
  fallbackIsOpen?: boolean;
  className?: string;
}

export const MarketStatusIndicator: React.FC<MarketStatusIndicatorProps> = ({
  exchange = "NSE",
  fallbackIsOpen = true,
  className = "",
}) => {
  const realtimeStatus = useRealtimeMarketStatus(exchange);

  const status = realtimeStatus?.status || (fallbackIsOpen ? "OPEN" : "CLOSED");
  const isOpen = realtimeStatus ? realtimeStatus.isOpen : fallbackIsOpen;

  let badgeStyle = "bg-gain/10 text-gain border-gain/20";
  let dotStyle = "bg-gain animate-pulse";
  let label = `${exchange} Open`;

  if (status === "PRE_MARKET") {
    badgeStyle = "bg-amber-500/10 text-amber-600 border-amber-500/20";
    dotStyle = "bg-amber-500 animate-pulse";
    label = `${exchange} Pre-Market`;
  } else if (!isOpen || status === "CLOSED" || status === "POST_MARKET") {
    badgeStyle = "bg-surface-subtle text-content-muted border-border";
    dotStyle = "bg-content-muted";
    label = `${exchange} Closed`;
  }

  return (
    <span
      className={`inline-flex items-center gap-1.5 text-xs font-semibold px-2 py-0.5 rounded-full border ${badgeStyle} ${className}`}
    >
      <span className={`w-1.5 h-1.5 rounded-full ${dotStyle}`} />
      <span>{label}</span>
    </span>
  );
};
