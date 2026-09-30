"use client";

import { useState, useEffect, useCallback, useMemo, useRef } from "react";
import { useSyncExternalStore } from "react";
import { watchlistApi } from "@/lib/api/watchlist";
import { useMarketWebSocket } from "@/providers/MarketWebSocketProvider";
import { marketStore } from "@/lib/realtime/marketStore";
import { normalizeSymbol } from "@/lib/realtime/symbolNormalizer";

export interface WatchlistDisplayItem {
  ticker: string;
  company_name: string;
  price: number;
  change: number;
  change_pct: number;
  volume: number;
  status: "ACTIVE" | "ALERT" | "NEUTRAL";
}

const FALLBACK_WATCHLIST: WatchlistDisplayItem[] = [
  {
    ticker: "RELIANCE.NS",
    company_name: "Reliance Industries Ltd",
    price: 2984.5,
    change: 32.1,
    change_pct: 1.09,
    volume: 8420000,
    status: "ACTIVE",
  },
  {
    ticker: "TCS.NS",
    company_name: "Tata Consultancy Services",
    price: 4210.8,
    change: 54.3,
    change_pct: 1.31,
    volume: 3120000,
    status: "ACTIVE",
  },
  {
    ticker: "INFY.NS",
    company_name: "Infosys Ltd",
    price: 1845.2,
    change: -12.4,
    change_pct: -0.67,
    volume: 6840000,
    status: "ALERT",
  },
  {
    ticker: "HDFCBANK.NS",
    company_name: "HDFC Bank Ltd",
    price: 1642.0,
    change: 8.5,
    change_pct: 0.52,
    volume: 12400000,
    status: "NEUTRAL",
  },
  {
    ticker: "TATAMOTORS.NS",
    company_name: "Tata Motors Ltd",
    price: 978.4,
    change: 22.8,
    change_pct: 2.39,
    volume: 9150000,
    status: "ACTIVE",
  },
];

export function useWatchlist() {
  const [baseWatchlist, setBaseWatchlist] = useState<WatchlistDisplayItem[]>([]);
  const [isLoading, setIsLoading] = useState<boolean>(true);
  const [isError, setIsError] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);
  const [isDemo, setIsDemo] = useState<boolean>(false);

  const { subscribeSymbol, unsubscribeSymbol } = useMarketWebSocket();
  const subscribedSymbolsRef = useRef<Set<string>>(new Set());

  // Listen to realtime quotes store
  const realtimeQuotes = useSyncExternalStore(
    marketStore.subscribe,
    () => marketStore.getSnapshot().quotes,
    () => marketStore.getSnapshot().quotes
  );

  const fetchWatchlist = useCallback(async () => {
    setIsLoading(true);
    setIsError(false);
    setError(null);
    try {
      const data = await watchlistApi.getWatchlist();
      if (data && data.length > 0) {
        const formatted: WatchlistDisplayItem[] = data.map((item: any) => ({
          ticker: item.ticker || item.symbol,
          company_name: item.company_name || item.name || item.ticker,
          price: item.price || item.current_price || 0,
          change: item.change || 0,
          change_pct: item.change_pct || item.change_percent || 0,
          volume: item.volume || 0,
          status: item.change_pct > 1 ? "ACTIVE" : item.change_pct < -1 ? "ALERT" : "NEUTRAL",
        }));
        setBaseWatchlist(formatted);
        setIsDemo(false);
      } else {
        setBaseWatchlist(FALLBACK_WATCHLIST);
        setIsDemo(true);
      }
    } catch {
      setBaseWatchlist(FALLBACK_WATCHLIST);
      setIsDemo(true);
    } finally {
      setIsLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchWatchlist();
  }, [fetchWatchlist]);

  // Synchronize WebSocket symbol subscriptions with active watchlist items
  useEffect(() => {
    const currentTickers = new Set(
      baseWatchlist.map((item) => normalizeSymbol(item.ticker)).filter(Boolean)
    );

    // Subscribe new tickers
    currentTickers.forEach((sym) => {
      if (!subscribedSymbolsRef.current.has(sym)) {
        subscribeSymbol(sym);
        subscribedSymbolsRef.current.add(sym);
      }
    });

    // Unsubscribe removed tickers
    subscribedSymbolsRef.current.forEach((sym) => {
      if (!currentTickers.has(sym)) {
        unsubscribeSymbol(sym);
        subscribedSymbolsRef.current.delete(sym);
      }
    });
  }, [baseWatchlist, subscribeSymbol, unsubscribeSymbol]);

  // Cleanup all subscriptions on unmount
  useEffect(() => {
    const active = subscribedSymbolsRef.current;
    return () => {
      active.forEach((sym) => {
        unsubscribeSymbol(sym);
      });
      active.clear();
    };
  }, [unsubscribeSymbol]);

  // Merge real-time WebSocket ticks dynamically
  const mergedWatchlist = useMemo(() => {
    const list = baseWatchlist.length > 0 ? baseWatchlist : FALLBACK_WATCHLIST;
    return list.map((item) => {
      const canonical = normalizeSymbol(item.ticker);
      const rt = realtimeQuotes[canonical] || realtimeQuotes[item.ticker];
      if (!rt) return item;

      return {
        ...item,
        price: rt.price,
        change: rt.change,
        change_pct: rt.changePercent,
        volume: rt.volume !== undefined ? rt.volume : item.volume,
        status:
          rt.changePercent > 1
            ? "ACTIVE"
            : rt.changePercent < -1
            ? "ALERT"
            : "NEUTRAL",
      };
    });
  }, [baseWatchlist, realtimeQuotes]);

  const addToWatchlist = async (ticker: string) => {
    try {
      await watchlistApi.addToWatchlist(ticker);
      await fetchWatchlist();
    } catch (err: any) {
      console.error("Failed to add to watchlist:", err);
    }
  };

  const removeFromWatchlist = async (ticker: string) => {
    try {
      await watchlistApi.removeFromWatchlist(ticker);
      setBaseWatchlist((prev) => prev.filter((item) => item.ticker !== ticker));
    } catch (err: any) {
      console.error("Failed to remove from watchlist:", err);
    }
  };

  return {
    watchlist: mergedWatchlist,
    isLoading,
    isError,
    error,
    isDemo,
    addToWatchlist,
    removeFromWatchlist,
    refresh: fetchWatchlist,
  };
}
