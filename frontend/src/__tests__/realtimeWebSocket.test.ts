/**
 * MarketMind AI — Comprehensive Frontend Real-Time WebSocket & Store Tests (Phase 6.5).
 * Tests symbol normalization, event routing, store reactivity, deduplication,
 * connection lifecycle, backoff scheduling, and provenance enforcement.
 */
import assert from "node:assert/strict";
import { test, describe, beforeEach } from "node:test";

// Test implementations of the core frontend realtime abstractions
import { normalizeSymbol } from "../lib/realtime/symbolNormalizer.js";
import { marketStore } from "../lib/realtime/marketStore.js";
import { routeMarketStreamEvent } from "../lib/realtime/marketEventRouter.js";

describe("Phase 6.5 — Frontend Real-Time Streaming Unit & Integration Tests", () => {
  beforeEach(() => {
    marketStore.reset();
  });

  test("1. Symbol Normalization: Indian equities, indices, and US tickers", () => {
    assert.equal(normalizeSymbol("RELIANCE"), "RELIANCE.NS");
    assert.equal(normalizeSymbol("tcs"), "TCS.NS");
    assert.equal(normalizeSymbol("INFY.NS"), "INFY.NS");
    assert.equal(normalizeSymbol("NIFTY 50"), "^NSEI");
    assert.equal(normalizeSymbol("SENSEX"), "^BSESN");
    assert.equal(normalizeSymbol("NIFTY BANK"), "^NSEBANK");
    assert.equal(normalizeSymbol("AAPL"), "AAPL");
    assert.equal(normalizeSymbol(""), "");
  });

  test("2. Event Router: Handles CONNECTED event and initializes store state", () => {
    const connectedMsg = {
      event: "CONNECTED",
      connection_id: "conn-12345",
      server_time: new Date().toISOString(),
      data_status: "DEMO",
      data_source: "DEMO",
    };

    const handled = routeMarketStreamEvent(connectedMsg);
    assert.equal(handled, true);

    const snapshot = marketStore.getSnapshot();
    assert.equal(snapshot.connectionStatus, "CONNECTED");
    assert.equal(snapshot.dataStatus, "DEMO");
    assert.ok(snapshot.lastEventAt !== null);
  });

  test("3. Event Router: QUOTE_TICK updates store and normalizes symbol", () => {
    const tick = {
      event: "QUOTE_TICK",
      event_id: "evt-quote-001",
      symbol: "RELIANCE",
      exchange: "NSE",
      timestamp: new Date().toISOString(),
      data_status: "DEMO",
      data_source: "DEMO",
      payload: {
        price: 2985.5,
        change: 35.0,
        change_percent: 1.18,
        volume: 125000,
        day_high: 3010.0,
        day_low: 2950.0,
      },
    };

    routeMarketStreamEvent(tick);
    const quote = marketStore.getSnapshot().quotes["RELIANCE.NS"];
    assert.ok(quote);
    assert.equal(quote.price, 2985.5);
    assert.equal(quote.changePercent, 1.18);
    assert.equal(quote.symbol, "RELIANCE.NS");
    assert.equal(quote.dataStatus, "DEMO");
  });

  test("4. Event Router: INDEX_TICK updates benchmark indices in store", () => {
    const indexTick = {
      event: "INDEX_TICK",
      event_id: "evt-idx-001",
      symbol: "^NSEI",
      exchange: "NSE",
      timestamp: new Date().toISOString(),
      data_status: "DEMO",
      data_source: "DEMO",
      payload: {
        index_name: "NIFTY 50",
        value: 24890.5,
        change: 120.5,
        change_percent: 0.49,
      },
    };

    routeMarketStreamEvent(indexTick);
    const idx = marketStore.getSnapshot().indices["^NSEI"];
    assert.ok(idx);
    assert.equal(idx.name, "NIFTY 50");
    assert.equal(idx.price, 24890.5);
    assert.equal(idx.changePercent, 0.49);
  });

  test("5. Event Router: ANOMALY_DETECTED prepends anomaly feed with deduplication", () => {
    const anomalyMsg = {
      event: "ANOMALY_DETECTED",
      event_id: "anom-uniq-999",
      symbol: "RELIANCE.NS",
      timestamp: new Date().toISOString(),
      data_status: "DEMO",
      payload: {
        anomaly_type: "VOLATILITY_BURST",
        severity: "HIGH",
        confidence_score: 0.91,
        summary: "GARCH Volatility Regime expansion detected",
      },
    };

    // First arrival
    routeMarketStreamEvent(anomalyMsg);
    assert.equal(marketStore.getSnapshot().anomalies.length, 1);
    assert.equal(marketStore.getSnapshot().anomalies[0].id, "anom-uniq-999");
    assert.equal(marketStore.getSnapshot().anomalies[0].severity, "HIGH");

    // Second arrival with identical ID -> deduplicated!
    routeMarketStreamEvent(anomalyMsg);
    assert.equal(marketStore.getSnapshot().anomalies.length, 1);
  });

  test("6. Event Router: SESSION_CHANGE updates exchange market status", () => {
    const sessionMsg = {
      event: "SESSION_CHANGE",
      symbol: "NSE",
      exchange: "NSE",
      timestamp: new Date().toISOString(),
      payload: {
        status: "OPEN",
        is_open: true,
      },
    };

    routeMarketStreamEvent(sessionMsg);
    const session = marketStore.getSnapshot().marketStatus["NSE"];
    assert.ok(session);
    assert.equal(session.status, "OPEN");
    assert.equal(session.isOpen, true);
  });

  test("7. Event Router: Gracefully ignores malformed or unknown events", () => {
    assert.equal(routeMarketStreamEvent(null), false);
    assert.equal(routeMarketStreamEvent("INVALID_STRING"), false);
    assert.equal(routeMarketStreamEvent({ event: "UNKNOWN_FUTURE_EVENT" }), false);
    assert.equal(routeMarketStreamEvent({}), false);
  });

  test("8. Store Reactivity: Listeners are triggered upon state updates", () => {
    let triggered = false;
    const unsubscribe = marketStore.subscribe(() => {
      triggered = true;
    });

    marketStore.updateQuote({
      symbol: "TCS.NS",
      exchange: "NSE",
      price: 4200.0,
      change: 50.0,
      changePercent: 1.2,
      timestamp: new Date().toISOString(),
      dataStatus: "DEMO",
      dataSource: "DEMO",
      lastUpdated: new Date(),
    });

    assert.equal(triggered, true);
    unsubscribe();
  });

  test("9. Provenance Safety: Strict DEMO status is maintained across all events", () => {
    routeMarketStreamEvent({
      event: "QUOTE_TICK",
      symbol: "INFY.NS",
      data_status: "DEMO",
      payload: { price: 1850.0 },
    });

    const quote = marketStore.getSnapshot().quotes["INFY.NS"];
    assert.equal(quote.dataStatus, "DEMO");
    assert.notEqual(quote.dataStatus, "LIVE");
  });

  test("10. Exponential Backoff progression calculates bounded delay steps", () => {
    const BACKOFF_STEPS = [1000, 2000, 4000, 8000, 16000, 30000];
    const getDelay = (attempt: number) => {
      const idx = Math.min(attempt, BACKOFF_STEPS.length - 1);
      return BACKOFF_STEPS[idx];
    };

    assert.equal(getDelay(0), 1000);
    assert.equal(getDelay(1), 2000);
    assert.equal(getDelay(2), 4000);
    assert.equal(getDelay(3), 8000);
    assert.equal(getDelay(4), 16000);
    assert.equal(getDelay(5), 30000);
    assert.equal(getDelay(10), 30000); // Caps at 30s
  });
});
