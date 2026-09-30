"""
Integration Tests for Market Ingestion & Telemetry REST Endpoints (Phase 6.3).
Validates:
- GET /api/v1/market/ingestion/health
- GET /api/v1/market/ingestion/status
- POST /api/v1/market/ingestion/collect
- POST /api/v1/market/ingestion/backfill
- GET /api/v1/market/ingestion/quality/{symbol}
"""
import pytest
from unittest.mock import patch, MagicMock, AsyncMock
from fastapi.testclient import TestClient

from app.main import app

test_client = TestClient(app)


def test_get_ingestion_health_endpoint():
    response = test_client.get("/api/v1/market/ingestion/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "HEALTHY"
    assert data["collector_status"] == "ONLINE"
    assert "scheduler" in data
    assert "redis_connected" in data
    assert "monitored_universe_size" in data


def test_get_ingestion_status_endpoint():
    response = test_client.get("/api/v1/market/ingestion/status")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "RUNNING"
    assert "monitored_universe" in data
    assert "total_symbols" in data["monitored_universe"]


def test_post_manual_collection_endpoint():
    response = test_client.post(
        "/api/v1/market/ingestion/collect",
        params={"symbols": ["RELIANCE.NS", "TCS.NS"]}
    )
    assert response.status_code == 200
    data = response.json()
    assert "cycle_id" in data
    assert "records_requested" in data
    assert data["records_requested"] >= 1


def test_post_historical_backfill_endpoint():
    with patch("app.services.market_backfill_service.market_backfill_service.backfill_symbol_history", new_callable=AsyncMock) as mock_backfill:
        mock_backfill.return_value = MagicMock(
            model_dump=lambda: {
                "symbol": "RELIANCE.NS",
                "status": "SUCCESS",
                "bars_fetched": 10,
                "bars_persisted": 10,
                "is_incremental": True
            }
        )

        response = test_client.post(
            "/api/v1/market/ingestion/backfill",
            params={"symbol": "RELIANCE.NS", "timeframe": "6m", "interval": "1d"}
        )
        assert response.status_code == 200
        data = response.json()
        assert data["symbol"] == "RELIANCE.NS"
        assert data["status"] == "SUCCESS"


def test_get_symbol_quality_report_endpoint():
    response = test_client.get("/api/v1/market/ingestion/quality/RELIANCE.NS")
    assert response.status_code == 200
    data = response.json()
    assert data["symbol"] == "RELIANCE.NS"
    assert "quality_status" in data
    assert "quality_score" in data
    assert "gaps_detected" in data
