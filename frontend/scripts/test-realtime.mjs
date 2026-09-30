/**
 * MarketMind AI — Frontend Realtime Test Runner Script.
 */
import assert from "node:assert/strict";

// 1. Symbol Normalizer Tests
import { normalizeSymbol } from "../src/lib/realtime/symbolNormalizer.ts";
import { marketStore } from "../src/lib/realtime/marketStore.ts";
import { routeMarketStreamEvent } from "../src/lib/realtime/marketEventRouter.ts";

console.log("=================================================");
console.log("Phase 6.5 — Frontend Real-Time WebSocket Tests");
console.log("=================================================");

let passed = 0;
let failed = 0;

function runTest(name, fn) {
  try {
    marketStore.reset();
    fn();
    console.log(` PASS  ${name}`);
    passed++;
  } catch (err) {
    console.error(` FAIL  ${name}`);
    console.error(err);
    failed++;
  }
}

// Test 1
runTest("Symbol Normalization (RELIANCE, TCS, INFY, NIFTY 50, SENSEX, AAPL)", () => {
  assert.equal(normalizeSymbol("RELIANCE"), "RELIANCE.NS");
  assert.equal(normalizeSymbol("tcs"), "TCS.NS");
  assert.equal(normalizeSymbol("INFY.NS"), "INFY.NS");
  assert.equal(normalizeSymbol("NIFTY 50"), "^NSEI");
  assert.equal(normalizeSymbol("SENSEX"), "^BSESN");
  assert.equal(normalizeSymbol("NIFTY BANK"), "^NSEBANK");
  assert.equal(normalizeSymbol("AAPL"), "AAPL");
});

// Test 2
runTest("Event Router: CONNECTED event handling & store initialization", () => {
  const connectedMsg = {
    event: "CONNECTED",
    connection_id: "conn-9988",
    server_time: new Date().toISOString(),
    data_status: "DEMO",
    data_source: "DEMO",
  };
  const handled = routeMarketStreamEvent(connectedMsg);
  assert.equal(handled, true);
  const snap = marketStore.getSnapshot();
  assert.equal(snap.connectionStatus, "CONNECTED");
  assert.equal(snap.dataStatus, "DEMO");
});

// Test 3
runTest("Event Router: QUOTE_TICK updates store and normalizes symbol", () => {
  const tick = {
    event: "QUOTE_TICK",
    symbol: "RELIANCE",
    payload: { price: 2990.0, change: 40.0, change_percent: 1.35, volume: 50000 },
  };
  routeMarketStreamEvent(tick);
  const q = marketStore.getSnapshot().quotes["RELIANCE.NS"];
  assert.ok(q);
  assert.equal(q.price, 2990.0);
  assert.equal(q.changePercent, 1.35);
});

// Test 4
runTest("Event Router: INDEX_TICK updates benchmark indices", () => {
  const idxTick = {
    event: "INDEX_TICK",
    symbol: "^NSEI",
    payload: { index_name: "NIFTY 50", value: 24950.0, change_percent: 0.65 },
  };
  routeMarketStreamEvent(idxTick);
  const idx = marketStore.getSnapshot().indices["^NSEI"];
  assert.ok(idx);
  assert.equal(idx.name, "NIFTY 50");
  assert.equal(idx.price, 24950.0);
});

// Test 5
runTest("Event Router: ANOMALY_DETECTED with deduplication", () => {
  const anomaly = {
    event: "ANOMALY_DETECTED",
    event_id: "anom-test-1",
    symbol: "TCS.NS",
    payload: {
      anomaly_type: "VOLUME_SURGE",
      severity: "HIGH",
      confidence_score: 0.89,
    },
  };
  routeMarketStreamEvent(anomaly);
  assert.equal(marketStore.getSnapshot().anomalies.length, 1);
  // Re-route duplicate
  routeMarketStreamEvent(anomaly);
  assert.equal(marketStore.getSnapshot().anomalies.length, 1);
});

// Test 6
runTest("Event Router: SESSION_CHANGE updates exchange market status", () => {
  const session = {
    event: "SESSION_CHANGE",
    symbol: "NSE",
    payload: { status: "OPEN", is_open: true },
  };
  routeMarketStreamEvent(session);
  const st = marketStore.getSnapshot().marketStatus["NSE"];
  assert.ok(st);
  assert.equal(st.status, "OPEN");
  assert.equal(st.isOpen, true);
});

// Test 7
runTest("Event Router: Malformed event protection", () => {
  assert.equal(routeMarketStreamEvent(null), false);
  assert.equal(routeMarketStreamEvent(undefined), false);
  assert.equal(routeMarketStreamEvent({}), false);
  assert.equal(routeMarketStreamEvent({ event: "INVALID_UNKNOWN" }), false);
});

// Test 8
runTest("Store Reactivity & Listener Dispatches", () => {
  let count = 0;
  const unsub = marketStore.subscribe(() => {
    count++;
  });
  marketStore.setConnectionStatus("CONNECTED");
  marketStore.setDataStatus("DEMO");
  assert.equal(count, 2);
  unsub();
});

// Test 9
runTest("Strict DEMO Provenance Preservation", () => {
  routeMarketStreamEvent({
    event: "QUOTE_TICK",
    symbol: "INFY.NS",
    data_status: "DEMO",
    payload: { price: 1850.0 },
  });
  const q = marketStore.getSnapshot().quotes["INFY.NS"];
  assert.equal(q.dataStatus, "DEMO");
  assert.notEqual(q.dataStatus, "LIVE");
});

// Test 10
runTest("Exponential Backoff Calculation Steps (1s, 2s, 4s, 8s, 16s, 30s max)", () => {
  const BACKOFF_STEPS = [1000, 2000, 4000, 8000, 16000, 30000];
  const calc = (attempt) => BACKOFF_STEPS[Math.min(attempt, BACKOFF_STEPS.length - 1)];
  assert.equal(calc(0), 1000);
  assert.equal(calc(1), 2000);
  assert.equal(calc(2), 4000);
  assert.equal(calc(3), 8000);
  assert.equal(calc(4), 16000);
  assert.equal(calc(5), 30000);
  assert.equal(calc(10), 30000);
});

console.log("=================================================");
console.log(`Results: ${passed} Passed, ${failed} Failed`);
console.log("=================================================");

if (failed > 0) {
  process.exit(1);
} else {
  process.exit(0);
}
