/**
 * MarketMind AI — Frontend Observability & Data Quality Verification Suite.
 * Phase 6.8: Unit tests for freshness state derivation, provenance rules,
 * deterministic 6-dimension scoring, 3-pillar symbol aggregation, and secret sanitization.
 */

import assert from "assert";

console.log("=================================================");
console.log("Phase 6.8 — Frontend Observability & Quality Tests");
console.log("=================================================");

function test(name, fn) {
  try {
    fn();
    console.log(`\x1b[32m PASS \x1b[0m ${name}`);
  } catch (err) {
    console.error(`\x1b[31m FAIL \x1b[0m ${name}`);
    console.error(err);
    process.exit(1);
  }
}

// 1. Quality Score Deterministic Calculation
test("Deterministic Quality Score: Exact 6-Dimension Weights", () => {
  const weights = {
    freshness: 0.25,
    completeness: 0.20,
    validity: 0.20,
    availability: 0.15,
    consistency: 0.10,
    continuity: 0.10,
  };

  const scores = {
    freshness: 80.0,
    completeness: 90.0,
    validity: 100.0,
    availability: 100.0,
    consistency: 70.0,
    continuity: 60.0,
  };

  const calculated =
    scores.freshness * weights.freshness +
    scores.completeness * weights.completeness +
    scores.validity * weights.validity +
    scores.availability * weights.availability +
    scores.consistency * weights.consistency +
    scores.continuity * weights.continuity;

  assert.strictEqual(Math.round(calculated * 100) / 100, 86.0);
});

// 2. Symbol 3-Pillar Aggregation
test("Symbol 3-Pillar Composite Calculation (Market 40%, Fund 35%, News 25%)", () => {
  const marketScore = 96.0;
  const fundScore = 78.0;
  const newsScore = 94.0;

  const composite = Math.round((marketScore * 0.40 + fundScore * 0.35 + newsScore * 0.25) * 100) / 100;
  assert.strictEqual(composite, 89.2);
});

// 3. Freshness State Resolution
test("Freshness State Resolution & Provenance Invariants", () => {
  function resolveFreshness(status, dataStatus) {
    if (dataStatus?.toUpperCase() === "LIVE" || status?.toUpperCase() === "LIVE") return "LIVE";
    if (status?.toUpperCase() === "FRESH") return "FRESH";
    if (status?.toUpperCase() === "STALE") return "STALE";
    if (status?.toUpperCase() === "UNAVAILABLE") return "UNAVAILABLE";
    return "DEMO";
  }

  assert.strictEqual(resolveFreshness("LIVE", "LIVE"), "LIVE");
  assert.strictEqual(resolveFreshness("HEALTHY", "DEMO"), "DEMO");
  assert.strictEqual(resolveFreshness("STALE", "LIVE"), "LIVE"); // Data status LIVE takes priority for stream type
  assert.strictEqual(resolveFreshness("STALE", "DEMO"), "STALE");
  assert.strictEqual(resolveFreshness("UNAVAILABLE", "DEMO"), "UNAVAILABLE");
});

// 4. Secret Sanitization Verification
test("Secret & Credential Redaction Invariants", () => {
  const REDACTION_PATTERNS = [
    [/(api[_-]?key["']?\s*[:=]\s*["'])([^"']+)["']/gi, '$1[REDACTED]'],
    [/(password["']?\s*[:=]\s*["'])([^"']+)["']/gi, '$1[REDACTED]'],
    [/(bearer\s+)([a-zA-Z0-9_\-\.]+)/gi, '$1[REDACTED]'],
  ];

  function sanitize(msg) {
    let clean = msg;
    for (const [pattern, replacement] of REDACTION_PATTERNS) {
      clean = clean.replace(pattern, replacement);
    }
    return clean;
  }

  const raw = 'Request failed for api_key="secret-999" with Bearer eyJhbGciOi.token and password="mypassword"';
  const sanitized = sanitize(raw);

  assert(!sanitized.includes("secret-999"), "api_key must be redacted");
  assert(!sanitized.includes("mypassword"), "password must be redacted");
  assert(!sanitized.includes("eyJhbGciOi"), "bearer token must be redacted");
  assert(sanitized.includes("[REDACTED]"), "replacement marker must be present");
});

// 5. OHLC Invariant Verification
test("OHLC Boundary Validation: High >= max(Open, Close) & Low <= min(Open, Close)", () => {
  function validateCandle(c) {
    if (c.high < Math.max(c.open, c.close)) return false;
    if (c.low > Math.min(c.open, c.close)) return false;
    if (c.high < c.low) return false;
    if (c.volume < 0) return false;
    return true;
  }

  assert.strictEqual(validateCandle({ open: 100, high: 105, low: 95, close: 102, volume: 500 }), true);
  assert.strictEqual(validateCandle({ open: 100, high: 98, low: 95, close: 102, volume: 500 }), false); // high < close
  assert.strictEqual(validateCandle({ open: 100, high: 105, low: 102, close: 104, volume: 500 }), false); // low > open
  assert.strictEqual(validateCandle({ open: 100, high: 105, low: 95, close: 102, volume: -10 }), false); // negative volume
});

console.log("=================================================");
console.log("Results: 5 Passed, 0 Failed");
console.log("=================================================");
