"use client";

import { useState, useEffect, useCallback, useMemo } from "react";
import { analyticsApi } from "@/lib/api/analytics";
import { AnomalyItem, AnomalySeverity } from "@/types";
import { useMarketWebSocket } from "@/providers/MarketWebSocketProvider";
import { useRealtimeAnomalies } from "./useRealtimeSelectors";

export interface EnrichedAnomalyItem extends AnomalyItem {
  id: string;
  company_name?: string;
  observed_value?: string | number;
  expected_value?: string | number;
  z_score?: number;
  model_name?: string;
  status?: "ACTIVE" | "RESOLVED" | "INVESTIGATING";
  severity: AnomalySeverity;
  formatted_time: string;
}

const TICKER_NAMES: Record<string, string> = {
  "RELIANCE.NS": "Reliance Industries Ltd",
  "TCS.NS": "Tata Consultancy Services",
  "HDFCBANK.NS": "HDFC Bank Ltd",
  "INFY.NS": "Infosys Ltd",
  "ICICIBANK.NS": "ICICI Bank Ltd",
  "BHARTIARTL.NS": "Bharti Airtel Ltd",
  "SBIN.NS": "State Bank of India",
  "TATAMOTORS.NS": "Tata Motors Ltd",
  "ITC.NS": "ITC Ltd",
  "LT.NS": "Larsen & Toubro Ltd",
  "AAPL": "Apple Inc.",
  "NVDA": "NVIDIA Corporation",
  "MSFT": "Microsoft Corporation",
  "JPM": "JPMorgan Chase & Co.",
};

const FALLBACK_STREAM: EnrichedAnomalyItem[] = [
  {
    id: "anom-001",
    ticker: "RELIANCE.NS",
    company_name: "Reliance Industries Ltd",
    timestamp: new Date(Date.now() - 12 * 60 * 1000).toISOString(),
    formatted_time: "12m ago",
    anomaly_type: "VOLUME_SURGE",
    severity: "HIGH",
    severity_score: 0.88,
    isolation_score: -0.42,
    z_score: 3.42,
    observed_value: "14.2M Vol",
    expected_value: "4.1M Avg",
    model_name: "Volume Surge + Isolation Forest",
    status: "ACTIVE",
    summary: "Intraday block volume exceeded 3.42 standard deviations above the 30-day moving average.",
    metrics: { volume_z_score: 3.42, current_volume: 14200000, avg_volume: 4150000, price_impact_bps: 48 },
  },
  {
    id: "anom-002",
    ticker: "TCS.NS",
    company_name: "Tata Consultancy Services",
    timestamp: new Date(Date.now() - 28 * 60 * 1000).toISOString(),
    formatted_time: "28m ago",
    anomaly_type: "VOLATILITY_BURST",
    severity: "CRITICAL",
    severity_score: 0.94,
    isolation_score: -0.58,
    z_score: 4.15,
    observed_value: "38.4% Vol",
    expected_value: "13.2% Baseline",
    model_name: "GARCH(1,1) Volatility Regime",
    status: "ACTIVE",
    summary: "GARCH conditional variance exploded following sudden derivative skew expansion near 52-week high.",
    metrics: { garch_volatility_pct: 38.4, baseline_vol_pct: 13.2, atr_14: 64.2, realized_vol_20d: 31.8 },
  },
  {
    id: "anom-003",
    ticker: "INFY.NS",
    company_name: "Infosys Ltd",
    timestamp: new Date(Date.now() - 55 * 60 * 1000).toISOString(),
    formatted_time: "55m ago",
    anomaly_type: "CORRELATION_BREAK",
    severity: "MEDIUM",
    severity_score: 0.72,
    isolation_score: -0.31,
    z_score: 2.65,
    observed_value: "-0.68 Corr",
    expected_value: "+0.84 Historical",
    model_name: "Rolling Correlation Engine",
    status: "ACTIVE",
    summary: "Pairwise co-movement with NIFTY IT de-linked by 1.52 points during sector-wide rotation.",
    metrics: { rolling_correlation: -0.68, historical_correlation: 0.84, sector_beta_shift: 1.85 },
  },
  {
    id: "anom-004",
    ticker: "HDFCBANK.NS",
    company_name: "HDFC Bank Ltd",
    timestamp: new Date(Date.now() - 110 * 60 * 1000).toISOString(),
    formatted_time: "1h 50m ago",
    anomaly_type: "PRICE_SPIKE",
    severity: "LOW",
    severity_score: 0.45,
    isolation_score: -0.19,
    z_score: 1.85,
    observed_value: "+1.92% 5m Candle",
    expected_value: "±0.25% Normal",
    model_name: "Z-Score Impulse Filter",
    status: "RESOLVED",
    summary: "Order-book imbalance caused brief upward price deviation which normalized over 15 minutes.",
    metrics: { impulse_pct: 1.92, bid_ask_spread_bps: 14, z_score: 1.85 },
  },
  {
    id: "anom-005",
    ticker: "TATAMOTORS.NS",
    company_name: "Tata Motors Ltd",
    timestamp: new Date(Date.now() - 190 * 60 * 1000).toISOString(),
    formatted_time: "3h ago",
    anomaly_type: "VOLUME_SURGE",
    severity: "HIGH",
    severity_score: 0.86,
    isolation_score: -0.44,
    z_score: 3.18,
    observed_value: "9.1M Vol",
    expected_value: "3.2M Avg",
    model_name: "Volume Surge Detector",
    status: "ACTIVE",
    summary: "Automotive segment institutional volume concentration accompanying breakout momentum.",
    metrics: { volume_z_score: 3.18, current_volume: 9150000, avg_volume: 3200000, volume_ratio: 2.86 },
  },
];

export function useAnomalyFeed() {
  const [baseAnomalies, setBaseAnomalies] = useState<EnrichedAnomalyItem[]>(FALLBACK_STREAM);
  const [systemicStressIndex, setSystemicStressIndex] = useState<number>(24.8);
  const [totalActiveCount, setTotalActiveCount] = useState<number>(5);
  const [isLoading, setIsLoading] = useState<boolean>(true);
  const [isError, setIsError] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);
  const [isDemo, setIsDemo] = useState<boolean>(false);
  const [lastUpdated, setLastUpdated] = useState<Date>(new Date());

  const { subscribeChannel, unsubscribeChannel } = useMarketWebSocket();
  const realtimeAnomalies = useRealtimeAnomalies(30);

  // Subscribe to 'anomalies' channel
  useEffect(() => {
    subscribeChannel("anomalies");
    return () => {
      unsubscribeChannel("anomalies");
    };
  }, [subscribeChannel, unsubscribeChannel]);

  // Filter States
  const [severityFilter, setSeverityFilter] = useState<string>("ALL");
  const [typeFilter, setTypeFilter] = useState<string>("ALL");
  const [searchQuery, setSearchQuery] = useState<string>("");
  const [timeWindow, setTimeWindow] = useState<string>("1D");

  const fetchAnomalyStream = useCallback(async () => {
    setIsLoading(true);
    setIsError(false);
    setError(null);
    try {
      const data = await analyticsApi.getMarketAnomalyStream();
      if (data && data.anomalies && data.anomalies.length > 0) {
        const enriched: EnrichedAnomalyItem[] = data.anomalies.map((item, idx) => {
          const sevScore = item.severity_score ?? 0.5;
          const sev: AnomalySeverity =
            sevScore >= 0.9 ? "CRITICAL" :
            sevScore >= 0.75 ? "HIGH" :
            sevScore >= 0.5 ? "MEDIUM" : "LOW";

          const zVal = item.metrics?.z_score ?? item.metrics?.volume_z_score ?? (sevScore * 4);

          return {
            id: item.id || `anom-${idx}-${item.ticker}`,
            ticker: item.ticker,
            company_name: TICKER_NAMES[item.ticker] || item.ticker,
            timestamp: item.timestamp || new Date().toISOString(),
            formatted_time: formatTimeAgo(item.timestamp),
            anomaly_type: item.anomaly_type || "STATISTICAL",
            severity: sev,
            severity_score: sevScore,
            isolation_score: item.isolation_score ?? -0.3,
            z_score: Number(zVal.toFixed(2)),
            observed_value: item.metrics?.observed_value || `${(sevScore * 100).toFixed(0)}% Intensity`,
            expected_value: item.metrics?.expected_value || "Normal Regime",
            model_name: item.metrics?.model || "Isolation Forest + GARCH",
            status: "ACTIVE",
            summary: item.summary || `Multivariate anomaly detected for ${item.ticker}`,
            metrics: item.metrics || {},
          };
        });

        setBaseAnomalies(enriched);
        setTotalActiveCount(data.total_active || enriched.length);
        setSystemicStressIndex(data.systemic_stress_index || 22.4);
        setIsDemo(false);
      } else {
        setBaseAnomalies(FALLBACK_STREAM);
        setTotalActiveCount(FALLBACK_STREAM.length);
        setSystemicStressIndex(24.8);
        setIsDemo(true);
      }
      setLastUpdated(new Date());
    } catch {
      setBaseAnomalies(FALLBACK_STREAM);
      setTotalActiveCount(FALLBACK_STREAM.length);
      setSystemicStressIndex(24.8);
      setIsDemo(true);
      setLastUpdated(new Date());
    } finally {
      setIsLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchAnomalyStream();
  }, [fetchAnomalyStream]);

  // Merge real-time WebSocket anomalies dynamically onto base list
  const mergedAnomalies = useMemo(() => {
    if (!realtimeAnomalies || realtimeAnomalies.length === 0) {
      return baseAnomalies;
    }

    const seenIds = new Set<string>();
    const result: EnrichedAnomalyItem[] = [];

    // 1. Add fresh real-time anomalies first
    realtimeAnomalies.forEach((rt) => {
      if (!seenIds.has(rt.id)) {
        seenIds.add(rt.id);
        result.push({
          id: rt.id,
          ticker: rt.ticker,
          company_name: TICKER_NAMES[rt.ticker] || rt.ticker,
          timestamp: rt.timestamp,
          formatted_time: formatTimeAgo(rt.timestamp),
          anomaly_type: rt.anomaly_type,
          severity: rt.severity,
          severity_score: rt.severity_score,
          isolation_score: -0.45,
          z_score: Number((rt.severity_score * 4).toFixed(2)),
          observed_value: `${(rt.severity_score * 100).toFixed(0)}% Intensity`,
          expected_value: "Baseline Regime",
          model_name: "GARCH + Isolation Engine",
          status: "ACTIVE",
          summary: rt.summary,
          metrics: rt.metrics || {},
        });
      }
    });

    // 2. Append existing base anomalies
    baseAnomalies.forEach((b) => {
      if (!seenIds.has(b.id)) {
        seenIds.add(b.id);
        result.push(b);
      }
    });

    return result;
  }, [baseAnomalies, realtimeAnomalies]);

  // Filtered Anomalies
  const filteredAnomalies = useMemo(() => {
    return mergedAnomalies.filter((a) => {
      if (severityFilter !== "ALL" && a.severity !== severityFilter) {
        return false;
      }
      if (typeFilter !== "ALL") {
        const typeStr = a.anomaly_type.toUpperCase();
        if (!typeStr.includes(typeFilter.toUpperCase())) {
          return false;
        }
      }
      if (searchQuery.trim()) {
        const q = searchQuery.toLowerCase();
        const matchesTicker = a.ticker.toLowerCase().includes(q);
        const matchesName = a.company_name?.toLowerCase().includes(q);
        const matchesSummary = a.summary.toLowerCase().includes(q);
        if (!matchesTicker && !matchesName && !matchesSummary) {
          return false;
        }
      }
      return true;
    });
  }, [mergedAnomalies, severityFilter, typeFilter, searchQuery]);

  // Severity Distribution Breakdown
  const severityDistribution = useMemo(() => {
    const counts = { LOW: 0, MEDIUM: 0, HIGH: 0, CRITICAL: 0 };
    mergedAnomalies.forEach((a) => {
      if (counts[a.severity] !== undefined) {
        counts[a.severity]++;
      }
    });
    return counts;
  }, [mergedAnomalies]);

  return {
    anomalies: filteredAnomalies,
    allAnomalies: mergedAnomalies,
    totalActiveCount: mergedAnomalies.length,
    criticalCount: severityDistribution.CRITICAL,
    highCount: severityDistribution.HIGH,
    systemicStressIndex,
    severityDistribution,
    isLoading,
    isError,
    error,
    isDemo,
    lastUpdated,
    severityFilter,
    setSeverityFilter,
    typeFilter,
    setTypeFilter,
    searchQuery,
    setSearchQuery,
    timeWindow,
    setTimeWindow,
    refresh: fetchAnomalyStream,
  };
}

function formatTimeAgo(timestampStr?: string): string {
  if (!timestampStr) return "Just now";
  const date = new Date(timestampStr);
  if (isNaN(date.getTime())) return timestampStr;

  const diffMs = Date.now() - date.getTime();
  const diffMins = Math.floor(diffMs / 60000);
  if (diffMins < 1) return "Just now";
  if (diffMins < 60) return `${diffMins}m ago`;
  const diffHours = Math.floor(diffMins / 60);
  if (diffHours < 24) return `${diffHours}h ago`;
  return `${Math.floor(diffHours / 24)}d ago`;
}
