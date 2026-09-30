"""
MarketMind AI — Integration Tests for WebSocket Endpoints (Phase 6.4).
Tests FastAPI WebSocket connection handshake, ping-pong, subscriptions, error envelopes,
and HTTP health telemetry using FastAPI TestClient.
"""
import pytest
import json
from app.core.security import create_access_token
from app.services.mock_market_stream import mock_market_stream
from app.services.websocket_manager import websocket_manager


def test_stream_health_endpoint_http(test_client):
    """Verifies GET /api/v1/market/stream/health returns clean telemetry."""
    response = test_client.get("/api/v1/market/stream/health")
    assert response.status_code == 200
    data = response.json()
    assert data["websocket_enabled"] is True
    assert "active_connections" in data
    assert "events_per_second" in data
    assert "telemetry" in data
    assert "connections_total" in data["telemetry"]


def test_websocket_handshake_and_welcome(test_client):
    """Verifies initial connection welcome handshake payload."""
    with test_client.websocket_connect("/api/v1/ws/market") as ws:
        msg = ws.receive_json()
        assert msg["event"] == "CONNECTED"
        assert "connection_id" in msg
        assert "server_time" in msg
        assert msg["data_status"] == "DEMO"
        assert "quotes" in msg["supported_channels"]


def test_websocket_ping_pong(test_client):
    """Verifies client ping produces server pong envelope."""
    with test_client.websocket_connect("/api/v1/ws/market") as ws:
        _ = ws.receive_json()  # Consume welcome

        ws.send_json({"action": "ping"})
        resp = ws.receive_json()
        assert resp["event"] == "pong"
        assert "timestamp" in resp


def test_websocket_subscription_and_unsubscription_flow(test_client):
    """Verifies subscribe and unsubscribe message actions."""
    with test_client.websocket_connect("/api/v1/ws/market") as ws:
        _ = ws.receive_json()  # Consume welcome

        # Subscribe
        ws.send_json({
            "action": "subscribe",
            "symbols": ["RELIANCE.NS", "TCS.NS"],
            "channels": ["quotes", "anomalies"]
        })
        sub_resp = ws.receive_json()
        assert sub_resp["event"] == "SUBSCRIPTION_SUCCESS"
        assert "RELIANCE.NS" in sub_resp["subscribed_symbols"]
        assert "quotes" in sub_resp["subscribed_channels"]

        # List subscriptions
        ws.send_json({"action": "list_subscriptions"})
        list_resp = ws.receive_json()
        assert list_resp["event"] == "SUBSCRIPTIONS"
        assert "RELIANCE.NS" in list_resp["symbols"]

        # Unsubscribe
        ws.send_json({
            "action": "unsubscribe",
            "symbols": ["TCS.NS"],
            "channels": ["anomalies"]
        })
        unsub_resp = ws.receive_json()
        assert unsub_resp["event"] == "UNSUBSCRIPTION_SUCCESS"
        assert "TCS.NS" not in unsub_resp["subscribed_symbols"]
        assert "anomalies" not in unsub_resp["subscribed_channels"]


def test_websocket_auth_action_flow(test_client):
    """Verifies client can authenticate after connecting via 'auth' action."""
    token = create_access_token({"sub": "trader_user_1", "email": "trader@marketmind.ai"})

    with test_client.websocket_connect("/api/v1/ws/market") as ws:
        _ = ws.receive_json()  # Consume welcome

        # Send auth message
        ws.send_json({"action": "auth", "token": token})
        auth_resp = ws.receive_json()
        assert auth_resp["event"] == "AUTH_SUCCESS"
        assert auth_resp["user_id"] == "trader_user_1"


def test_websocket_invalid_json_handling(test_client):
    """Verifies that sending malformed JSON yields controlled ERROR envelope."""
    with test_client.websocket_connect("/api/v1/ws/market") as ws:
        _ = ws.receive_json()  # Consume welcome

        ws.send_text("NOT_VALID_JSON{:::}")
        err_resp = ws.receive_json()
        assert err_resp["event"] == "ERROR"
        assert err_resp["code"] == "INVALID_JSON"


def test_websocket_unknown_action_handling(test_client):
    """Verifies that unknown actions return a controlled ERROR envelope."""
    with test_client.websocket_connect("/api/v1/ws/market") as ws:
        _ = ws.receive_json()  # Consume welcome

        ws.send_json({"action": "teleport_orders_xyz"})
        err_resp = ws.receive_json()
        assert err_resp["event"] == "ERROR"
        assert err_resp["code"] == "UNKNOWN_ACTION"


def test_websocket_handshake_with_token_query_param(test_client):
    """Verifies query param ?token=... authenticates connection immediately."""
    token = create_access_token({"sub": "query_param_user"})
    with test_client.websocket_connect(f"/api/v1/ws/market?token={token}") as ws:
        msg = ws.receive_json()
        assert msg["event"] == "CONNECTED"
        assert msg["is_authenticated"] is True
        assert msg["user_id"] == "query_param_user"


def test_websocket_anomaly_event_delivery(test_client):
    """Verifies that an ANOMALY_DETECTED event is delivered to clients subscribed to anomalies channel."""
    with test_client.websocket_connect("/api/v1/ws/market") as ws:
        _ = ws.receive_json()  # welcome

        ws.send_json({"action": "subscribe", "channels": ["anomalies"]})
        sub_resp = ws.receive_json()
        assert sub_resp["event"] == "SUBSCRIPTION_SUCCESS"

        # Emit anomaly
        anomaly = mock_market_stream.create_mock_anomaly_event("RELIANCE.NS", score=0.95)
        # Deliver via manager
        import asyncio
        asyncio.run(websocket_manager.on_event_bus_event(anomaly))

        event_msg = ws.receive_json()
        assert event_msg["event"] == "ANOMALY_DETECTED"
        assert event_msg["symbol"] == "RELIANCE.NS"
        assert event_msg["data_status"] == "DEMO"


def test_websocket_session_change_delivery(test_client):
    """Verifies that a SESSION_CHANGE event is delivered to clients subscribed to market_status."""
    with test_client.websocket_connect("/api/v1/ws/market") as ws:
        _ = ws.receive_json()  # welcome

        ws.send_json({"action": "subscribe", "channels": ["market_status"]})
        sub_resp = ws.receive_json()
        assert sub_resp["event"] == "SUBSCRIPTION_SUCCESS"

        session_ev = mock_market_stream.create_mock_session_event("NSE", "OPEN")
        import asyncio
        asyncio.run(websocket_manager.on_event_bus_event(session_ev))

        event_msg = ws.receive_json()
        assert event_msg["event"] == "SESSION_CHANGE"
        assert event_msg["exchange"] == "NSE"
        assert event_msg["data_status"] == "DEMO"

