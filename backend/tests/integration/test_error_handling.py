"""
Error Handling, Edge Cases & System Resilience Integration Tests.
Verifies graceful error responses, HTTP status codes, validation failures, and unauthorized request rejections.
"""
import pytest
from fastapi.testclient import TestClient


def test_invalid_stock_symbol_validation(test_client: TestClient):
    """Querying an invalid ticker format (e.g. spaces or special chars) returns a 400 Validation error."""
    resp = test_client.get("/api/v1/stocks/INVALID$$$123")
    assert resp.status_code in [400, 422]
    err = resp.json()
    assert "detail" in err or "message" in err or "error" in err


def test_invalid_stock_history_timeframe(test_client: TestClient):
    """Querying history with an invalid timeframe returns 400 Validation error."""
    resp = test_client.get("/api/v1/stocks/AAPL/history?timeframe=invalid_100y")
    assert resp.status_code in [400, 422]


def test_unauthenticated_protected_routes(test_client: TestClient):
    """Accessing protected routes without Bearer token returns 401 Unauthorized."""
    # /auth/me
    resp_me = test_client.get("/api/v1/auth/me")
    assert resp_me.status_code == 401

    # Bad token
    bad_headers = {"Authorization": "Bearer invalid_garbage_token"}
    resp_bad = test_client.get("/api/v1/auth/me", headers=bad_headers)
    assert resp_bad.status_code == 401


def test_scenario_validation_errors(test_client: TestClient):
    """Testing invalid payload schema on scenario endpoints."""
    # Days < 5 or iterations < 100 triggers 422
    bad_payload = {
        "ticker": "AAPL",
        "days": 1,
        "iterations": 10
    }
    resp = test_client.post("/api/v1/scenarios/monte-carlo", json=bad_payload)
    assert resp.status_code == 422


def test_malformed_ai_request_validation(test_client: TestClient):
    """Empty query string fails Pydantic schema validation with 422."""
    resp = test_client.post("/api/v1/ai/analyze", json={"query": ""})
    assert resp.status_code == 422
