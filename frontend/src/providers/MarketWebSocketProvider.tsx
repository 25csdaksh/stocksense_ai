/**
 * MarketMind AI — Centralized Real-Time Market WebSocket Provider.
 * Maintains a single, shared WebSocket connection for the entire frontend application.
 * Manages reference-counted subscriptions, automatic exponential backoff reconnection,
 * JWT authentication, and incoming event routing into the RealtimeMarketStore.
 */
"use client";

import React, {
  createContext,
  useContext,
  useEffect,
  useRef,
  useState,
  useCallback,
} from "react";
import {
  WebSocketConnectionState,
  MarketDataStatus,
  MarketDataSource,
  MarketStreamChannel,
  MarketWebSocketContextType,
} from "@/types/market_stream";
import { API_BASE_URL } from "@/lib/constants";
import { authStorage } from "@/lib/auth/storage";
import { useAuth } from "@/hooks/useAuth";
import { marketStore } from "@/lib/realtime/marketStore";
import { useRealtimeConnectionState } from "@/hooks/useRealtimeSelectors";
import { routeMarketStreamEvent } from "@/lib/realtime/marketEventRouter";
import { normalizeSymbol } from "@/lib/realtime/symbolNormalizer";

const MarketWebSocketContext = createContext<MarketWebSocketContextType | null>(null);

const BACKOFF_STEPS = [1000, 2000, 4000, 8000, 16000, 30000];
const HEARTBEAT_INTERVAL_MS = 30000;
const STALE_THRESHOLD_MS = 60000;

export function MarketWebSocketProvider({ children }: { children: React.ReactNode }) {
  const { user } = useAuth();
  const socketRef = useRef<WebSocket | null>(null);
  const reconnectTimeoutRef = useRef<NodeJS.Timeout | null>(null);
  const heartbeatIntervalRef = useRef<NodeJS.Timeout | null>(null);
  const staleCheckIntervalRef = useRef<NodeJS.Timeout | null>(null);
  const retryCountRef = useRef<number>(0);
  const isIntentionalCloseRef = useRef<boolean>(false);

  // Reference-counted subscription tracking
  const symbolRefCount = useRef<Map<string, number>>(new Map());
  const channelRefCount = useRef<Map<string, number>>(new Map());

  const [connectionStatus, setConnectionStatus] = useState<WebSocketConnectionState>("DISCONNECTED");
  const connectionState = useRealtimeConnectionState();

  const getWebSocketUrl = useCallback(() => {
    const rawWsUrl = process.env.NEXT_PUBLIC_WS_URL;
    if (rawWsUrl) {
      return rawWsUrl;
    }
    // Derive from API_BASE_URL (http:// -> ws://, https:// -> wss://)
    const baseUrl = API_BASE_URL.replace(/^http/, "ws");
    const token = authStorage.getToken();
    const query = token ? `?token=${encodeURIComponent(token)}` : "";
    return `${baseUrl}/api/v1/ws/market${query}`;
  }, []);

  const sendJson = useCallback((data: Record<string, any>) => {
    if (socketRef.current && socketRef.current.readyState === WebSocket.OPEN) {
      try {
        socketRef.current.send(JSON.stringify(data));
      } catch (err) {
        console.debug("[MarketWS] Error sending payload:", err);
      }
    }
  }, []);

  const resubscribeActive = useCallback(() => {
    // Collect all symbols with refCount > 0
    const activeSymbols = Array.from(symbolRefCount.current.entries())
      .filter(([_, count]) => count > 0)
      .map(([sym]) => sym);

    // Collect all channels with refCount > 0
    const activeChannels = Array.from(channelRefCount.current.entries())
      .filter(([_, count]) => count > 0)
      .map(([ch]) => ch);

    if (activeSymbols.length > 0 || activeChannels.length > 0) {
      sendJson({
        action: "subscribe",
        symbols: activeSymbols,
        channels: activeChannels,
      });
    }
  }, [sendJson]);

  const connect = useCallback(() => {
    if (typeof window === "undefined") return;

    // Prevent duplicate connections if already open/connecting
    if (
      socketRef.current &&
      (socketRef.current.readyState === WebSocket.OPEN ||
        socketRef.current.readyState === WebSocket.CONNECTING)
    ) {
      return;
    }

    if (reconnectTimeoutRef.current) {
      clearTimeout(reconnectTimeoutRef.current);
      reconnectTimeoutRef.current = null;
    }

    isIntentionalCloseRef.current = false;
    const isReconnect = retryCountRef.current > 0;
    const initialStatus: WebSocketConnectionState = isReconnect ? "RECONNECTING" : "CONNECTING";
    setConnectionStatus(initialStatus);
    marketStore.setConnectionStatus(initialStatus);

    try {
      const url = getWebSocketUrl();
      const ws = new WebSocket(url);
      socketRef.current = ws;

      ws.onopen = () => {
        retryCountRef.current = 0;
        setConnectionStatus("CONNECTED");
        marketStore.setConnectionStatus("CONNECTED");

        // Authenticate if token exists and was not already passed via query
        const token = authStorage.getToken();
        if (token) {
          sendJson({ action: "auth", token });
        }

        // Restore active subscriptions
        resubscribeActive();
      };

      ws.onmessage = (event) => {
        try {
          const raw = JSON.parse(event.data);
          routeMarketStreamEvent(raw);
        } catch {
          // Ignore unparseable raw ticks
        }
      };

      ws.onclose = () => {
        socketRef.current = null;
        if (!isIntentionalCloseRef.current) {
          scheduleReconnect();
        } else {
          setConnectionStatus("DISCONNECTED");
          marketStore.setConnectionStatus("DISCONNECTED");
        }
      };

      ws.onerror = () => {
        setConnectionStatus("ERROR");
        marketStore.setConnectionStatus("ERROR");
      };
    } catch (err) {
      console.debug("[MarketWS] Connection initialization error:", err);
      scheduleReconnect();
    }
  }, [getWebSocketUrl, sendJson, resubscribeActive]);

  const scheduleReconnect = useCallback(() => {
    if (isIntentionalCloseRef.current) return;

    setConnectionStatus("RECONNECTING");
    marketStore.setConnectionStatus("RECONNECTING");

    const attempt = retryCountRef.current;
    const delayIndex = Math.min(attempt, BACKOFF_STEPS.length - 1);
    const baseDelay = BACKOFF_STEPS[delayIndex];
    // Add 0-500ms random jitter to avoid thundering herd
    const jitter = Math.floor(Math.random() * 500);
    const delay = baseDelay + jitter;

    retryCountRef.current = attempt + 1;

    if (reconnectTimeoutRef.current) {
      clearTimeout(reconnectTimeoutRef.current);
    }

    reconnectTimeoutRef.current = setTimeout(() => {
      connect();
    }, delay);
  }, [connect]);

  const disconnect = useCallback(() => {
    isIntentionalCloseRef.current = true;
    if (reconnectTimeoutRef.current) {
      clearTimeout(reconnectTimeoutRef.current);
      reconnectTimeoutRef.current = null;
    }
    if (socketRef.current) {
      socketRef.current.close(1000, "Normal Closure");
      socketRef.current = null;
    }
    setConnectionStatus("DISCONNECTED");
    marketStore.setConnectionStatus("DISCONNECTED");
  }, []);

  const manualReconnect = useCallback(() => {
    retryCountRef.current = 0;
    disconnect();
    connect();
  }, [disconnect, connect]);

  // Subscription methods
  const subscribeSymbol = useCallback(
    (rawSymbol: string) => {
      const canonical = normalizeSymbol(rawSymbol);
      if (!canonical) return;

      const currentCount = symbolRefCount.current.get(canonical) || 0;
      symbolRefCount.current.set(canonical, currentCount + 1);

      // Only send WebSocket action on the first reference
      if (currentCount === 0) {
        sendJson({
          action: "subscribe",
          symbols: [canonical],
        });
      }
    },
    [sendJson]
  );

  const unsubscribeSymbol = useCallback(
    (rawSymbol: string) => {
      const canonical = normalizeSymbol(rawSymbol);
      if (!canonical) return;

      const currentCount = symbolRefCount.current.get(canonical) || 0;
      if (currentCount <= 1) {
        symbolRefCount.current.delete(canonical);
        sendJson({
          action: "unsubscribe",
          symbols: [canonical],
        });
      } else {
        symbolRefCount.current.set(canonical, currentCount - 1);
      }
    },
    [sendJson]
  );

  const subscribeChannel = useCallback(
    (channel: MarketStreamChannel) => {
      const ch = channel.toLowerCase();
      const currentCount = channelRefCount.current.get(ch) || 0;
      channelRefCount.current.set(ch, currentCount + 1);

      if (currentCount === 0) {
        sendJson({
          action: "subscribe",
          channels: [ch],
        });
      }
    },
    [sendJson]
  );

  const unsubscribeChannel = useCallback(
    (channel: MarketStreamChannel) => {
      const ch = channel.toLowerCase();
      const currentCount = channelRefCount.current.get(ch) || 0;
      if (currentCount <= 1) {
        channelRefCount.current.delete(ch);
        sendJson({
          action: "unsubscribe",
          channels: [ch],
        });
      } else {
        channelRefCount.current.set(ch, currentCount - 1);
      }
    },
    [sendJson]
  );

  // Initial connection & window event listeners
  useEffect(() => {
    connect();

    // Heartbeat ping timer
    heartbeatIntervalRef.current = setInterval(() => {
      sendJson({ action: "ping" });
    }, HEARTBEAT_INTERVAL_MS);

    // Stale freshness check timer
    staleCheckIntervalRef.current = setInterval(() => {
      const snap = marketStore.getSnapshot();
      if (
        snap.connectionStatus === "CONNECTED" &&
        snap.lastEventAt !== null &&
        Date.now() - snap.lastEventAt.getTime() > STALE_THRESHOLD_MS
      ) {
        // Trigger notification
        marketStore.touchLastEvent();
      }
    }, 10000);

    const handleOnline = () => {
      manualReconnect();
    };

    const handleOffline = () => {
      setConnectionStatus("DISCONNECTED");
      marketStore.setConnectionStatus("DISCONNECTED");
    };

    const handleVisibilityChange = () => {
      if (document.visibilityState === "visible") {
        // Reconnect if socket closed while in background tab
        if (!socketRef.current || socketRef.current.readyState === WebSocket.CLOSED) {
          connect();
        }
      }
    };

    window.addEventListener("online", handleOnline);
    window.addEventListener("offline", handleOffline);
    document.addEventListener("visibilitychange", handleVisibilityChange);

    return () => {
      disconnect();
      if (heartbeatIntervalRef.current) clearInterval(heartbeatIntervalRef.current);
      if (staleCheckIntervalRef.current) clearInterval(staleCheckIntervalRef.current);
      window.removeEventListener("online", handleOnline);
      window.removeEventListener("offline", handleOffline);
      document.removeEventListener("visibilitychange", handleVisibilityChange);
    };
  }, [connect, disconnect, manualReconnect, sendJson]);

  // Handle user logout / auth change
  useEffect(() => {
    if (!user && socketRef.current && socketRef.current.readyState === WebSocket.OPEN) {
      // Send unsubscribe for protected private channels if user logged out
      channelRefCount.current.delete("portfolio");
      sendJson({ action: "unsubscribe", channels: ["portfolio"] });
    }
  }, [user, sendJson]);

  const value: MarketWebSocketContextType = {
    status: connectionStatus,
    dataStatus: connectionState.dataStatus,
    dataSource: connectionState.dataSource,
    connected: connectionStatus === "CONNECTED",
    lastEventAt: connectionState.lastEventAt,
    isStale: connectionState.isStale,
    subscribeSymbol,
    unsubscribeSymbol,
    subscribeChannel,
    unsubscribeChannel,
    reconnect: manualReconnect,
  };

  return (
    <MarketWebSocketContext.Provider value={value}>
      {children}
    </MarketWebSocketContext.Provider>
  );
}

export function useMarketWebSocket(): MarketWebSocketContextType {
  const context = useContext(MarketWebSocketContext);
  if (!context) {
    throw new Error("useMarketWebSocket must be used within a MarketWebSocketProvider");
  }
  return context;
}
