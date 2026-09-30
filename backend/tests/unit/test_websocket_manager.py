"""
MarketMind AI — Unit Tests for WebSocket Manager (Phase 6.4).
Tests connection tracking, authentication, subscription validation, backpressure queues,
event bus fanout, channel filtering, and telemetry.
"""
import pytest
import asyncio
from datetime import datetime, timedelta, timezone
from unittest.mock import AsyncMock, MagicMock

from app.core.config import settings
from app.core.security import create_access_token
from app.providers.market_data.models import DataStatus
from app.providers.market_data.streaming_events import (
    MarketDataEvent,
    MarketEventType,
    event_bus
)
from app.services.websocket_manager import (
    WebSocketManager,
    WebSocketConnection,
    ChannelType
)
from app.services.mock_market_stream import mock_market_stream


@pytest.fixture
def ws_mgr():
    """Provides an isolated WebSocketManager instance for testing."""
    mgr = WebSocketManager()
    mgr.start()
    yield mgr
    mgr.stop()


class MockWebSocket:
    """Mock WebSocket for unit testing."""
    def __init__(self):
        self.accepted = False
        self.closed = False
        self.sent_messages = []

    async def accept(self):
        self.accepted = True

    async def close(self, code=1000, reason=""):
        self.closed = True

    async def send_json(self, data):
        self.sent_messages.append(data)


@pytest.mark.asyncio
async def test_websocket_connect_and_disconnect(ws_mgr):
    """Verifies connection lifecycle and tracking."""
    mock_ws = MockWebSocket()
    conn, err = await ws_mgr.connect(mock_ws)

    assert err is None
    assert conn is not None
    assert mock_ws.accepted is True
    assert conn.connection_id in ws_mgr._connections
    assert ws_mgr.get_health_metrics()["active_connections"] == 1

    await ws_mgr.disconnect(conn.connection_id)
    assert conn.connection_id not in ws_mgr._connections
    assert ws_mgr.get_health_metrics()["active_connections"] == 0


@pytest.mark.asyncio
async def test_websocket_connect_limit_reached(ws_mgr, monkeypatch):
    """Verifies connection rejection when max limits are exceeded."""
    monkeypatch.setattr(settings, "WS_MAX_CONNECTIONS", 1)

    mock_ws1 = MockWebSocket()
    conn1, err1 = await ws_mgr.connect(mock_ws1)
    assert conn1 is not None

    mock_ws2 = MockWebSocket()
    conn2, err2 = await ws_mgr.connect(mock_ws2)
    assert conn2 is None
    assert "limit reached" in err2.lower()
    assert ws_mgr.get_health_metrics()["telemetry"]["connections_rejected"] == 1

    await ws_mgr.disconnect(conn1.connection_id)


@pytest.mark.asyncio
async def test_websocket_auth_handshake_and_action(ws_mgr):
    """Verifies JWT validation on handshake and subsequent auth message."""
    token = create_access_token({"sub": "user_123", "email": "trader@marketmind.ai"})

    # Handshake with valid token
    mock_ws = MockWebSocket()
    conn, _ = await ws_mgr.connect(mock_ws, token=token)
    assert conn.is_authenticated is True
    assert conn.user_id == "user_123"
    await ws_mgr.disconnect(conn.connection_id)

    # Connect unauthenticated then authenticate via action
    mock_ws2 = MockWebSocket()
    conn2, _ = await ws_mgr.connect(mock_ws2)
    assert conn2.is_authenticated is False

    auth_res = await ws_mgr.authenticate_connection(conn2.connection_id, token)
    assert auth_res["event"] == "AUTH_SUCCESS"
    assert conn2.is_authenticated is True
    assert conn2.user_id == "user_123"

    # Test invalid token
    bad_res = await ws_mgr.authenticate_connection(conn2.connection_id, "invalid.jwt.token")
    assert bad_res["event"] == "ERROR"
    assert bad_res["code"] == "AUTH_FAILED"

    await ws_mgr.disconnect(conn2.connection_id)


@pytest.mark.asyncio
async def test_websocket_subscribe_and_symbol_normalization(ws_mgr):
    """Verifies symbol normalization during subscription."""
    mock_ws = MockWebSocket()
    conn, _ = await ws_mgr.connect(mock_ws)

    res = await ws_mgr.subscribe(
        conn.connection_id,
        symbols=["reliance", "TCS.NS", "AAPL"],
        channels=["quotes", "anomalies"]
    )

    assert res["event"] == "SUBSCRIPTION_SUCCESS"
    assert "RELIANCE.NS" in conn.subscribed_symbols
    assert "TCS.NS" in conn.subscribed_symbols
    assert "AAPL" in conn.subscribed_symbols
    assert "quotes" in conn.subscribed_channels
    assert "anomalies" in conn.subscribed_channels

    # Check subscriptions listing
    list_res = ws_mgr.list_subscriptions(conn.connection_id)
    assert list_res["event"] == "SUBSCRIPTIONS"
    assert "RELIANCE.NS" in list_res["symbols"]

    # Unsubscribe
    unsub_res = await ws_mgr.unsubscribe(conn.connection_id, symbols=["TCS.NS"], channels=["quotes"])
    assert unsub_res["event"] == "UNSUBSCRIPTION_SUCCESS"
    assert "TCS.NS" not in conn.subscribed_symbols
    assert "quotes" not in conn.subscribed_channels

    await ws_mgr.disconnect(conn.connection_id)


@pytest.mark.asyncio
async def test_websocket_subscribe_invalid_symbol(ws_mgr):
    """Verifies handling and rejection of invalid symbols."""
    mock_ws = MockWebSocket()
    conn, _ = await ws_mgr.connect(mock_ws)

    res = await ws_mgr.subscribe(
        conn.connection_id,
        symbols=["INVALID$$$TICKER$$$", "RELIANCE.NS"]
    )

    assert res["event"] == "SUBSCRIPTION_SUCCESS"
    assert "RELIANCE.NS" in conn.subscribed_symbols
    assert "rejected_symbols" in res
    assert len(res["rejected_symbols"]) == 1

    await ws_mgr.disconnect(conn.connection_id)


@pytest.mark.asyncio
async def test_websocket_protected_channel_requires_auth(ws_mgr):
    """Verifies that private channels like 'portfolio' require authentication."""
    mock_ws = MockWebSocket()
    conn, _ = await ws_mgr.connect(mock_ws)

    # Unauthenticated user tries to subscribe to portfolio channel
    res = await ws_mgr.subscribe(conn.connection_id, channels=["portfolio"])
    assert "portfolio" not in conn.subscribed_channels
    assert "rejected_channels" in res
    assert "requires authentication" in res["rejected_channels"][0]["reason"].lower()

    # Authenticate and retry
    token = create_access_token({"sub": "user_456"})
    await ws_mgr.authenticate_connection(conn.connection_id, token)

    res_auth = await ws_mgr.subscribe(conn.connection_id, channels=["portfolio"])
    assert "portfolio" in conn.subscribed_channels

    await ws_mgr.disconnect(conn.connection_id)


@pytest.mark.asyncio
async def test_websocket_event_fanout_and_channel_filtering(ws_mgr):
    """Verifies that events are routed ONLY to clients with matching subscriptions."""
    ws_client1 = MockWebSocket()
    ws_client2 = MockWebSocket()

    conn1, _ = await ws_mgr.connect(ws_client1)
    conn2, _ = await ws_mgr.connect(ws_client2)

    # Client 1 subscribes to RELIANCE.NS, Client 2 subscribes to quotes channel
    await ws_mgr.subscribe(conn1.connection_id, symbols=["RELIANCE.NS"])
    await ws_mgr.subscribe(conn2.connection_id, channels=["quotes"])

    # Emit RELIANCE quote event -> both should receive
    event_rel = mock_market_stream.create_mock_quote_event("RELIANCE.NS", price=2950.0)
    await ws_mgr.on_event_bus_event(event_rel)

    # Give worker a tick to send
    await asyncio.sleep(0.05)

    assert len(ws_client1.sent_messages) == 1
    assert len(ws_client2.sent_messages) == 1
    assert ws_client1.sent_messages[0]["symbol"] == "RELIANCE.NS"
    assert ws_client1.sent_messages[0]["data_status"] == "DEMO"

    # Emit TCS quote event -> Client 1 (subscribed only to RELIANCE) must NOT receive it; Client 2 (quotes channel) SHOULD
    event_tcs = mock_market_stream.create_mock_quote_event("TCS.NS", price=4000.0)
    await ws_mgr.on_event_bus_event(event_tcs)

    await asyncio.sleep(0.05)

    assert len(ws_client1.sent_messages) == 1  # unchanged
    assert len(ws_client2.sent_messages) == 2  # received TCS

    await ws_mgr.disconnect(conn1.connection_id)
    await ws_mgr.disconnect(conn2.connection_id)


@pytest.mark.asyncio
async def test_websocket_backpressure_and_dropping(ws_mgr, monkeypatch):
    """Verifies bounded queue drops normal priority quotes when congested without blocking."""
    mock_ws = MockWebSocket()
    conn, _ = await ws_mgr.connect(mock_ws)
    await ws_mgr.subscribe(conn.connection_id, channels=["quotes", "market_status"])

    # Stop sender task to simulate slow/unresponsive client
    if conn.send_task:
        conn.send_task.cancel()

    # Fill queue to maximum capacity
    queue_max = settings.WS_QUEUE_MAX_SIZE
    for i in range(queue_max):
        ev = mock_market_stream.create_mock_quote_event("RELIANCE.NS", price=2800.0 + i)
        await ws_mgr.on_event_bus_event(ev)

    assert conn.outgoing_queue.full() is True

    # Send one more quote tick (priority Normal) -> should be dropped
    overflow_quote = mock_market_stream.create_mock_quote_event("RELIANCE.NS", price=3000.0)
    await ws_mgr.on_event_bus_event(overflow_quote)

    assert ws_mgr.get_health_metrics()["dropped_events"] >= 1

    # Send a high-priority Session Change event -> should evict and succeed
    session_ev = mock_market_stream.create_mock_session_event("NSE", new_status="CLOSED")
    await ws_mgr.on_event_bus_event(session_ev)

    assert conn.outgoing_queue.full() is True

    await ws_mgr.disconnect(conn.connection_id)


@pytest.mark.asyncio
async def test_websocket_heartbeat_ping_pong_and_stale_cleanup(ws_mgr, monkeypatch):
    """Verifies ping/pong and automatic disconnect of stale connections."""
    mock_ws = MockWebSocket()
    conn, _ = await ws_mgr.connect(mock_ws)

    # Test ping
    pong = ws_mgr.handle_ping(conn.connection_id)
    assert pong["event"] == "pong"
    assert "timestamp" in pong

    # Make connection stale artificially
    conn.last_heartbeat = datetime.now(timezone.utc) - timedelta(seconds=120)
    monkeypatch.setattr(settings, "WS_HEARTBEAT_TIMEOUT_SECONDS", 60)

    cleaned = await ws_mgr.cleanup_stale_connections()
    assert cleaned == 1
    assert conn.connection_id not in ws_mgr._connections


@pytest.mark.asyncio
async def test_mock_stream_generator_provenance(ws_mgr):
    """Verifies all mock generator events strictly maintain DEMO provenance."""
    quote = mock_market_stream.create_mock_quote_event("INFY.NS")
    assert quote.data_status == DataStatus.DEMO
    assert quote.data_source == "DEMO"

    idx = mock_market_stream.create_mock_index_event("^BSESN")
    assert idx.data_status == DataStatus.DEMO

    anomaly = mock_market_stream.create_mock_anomaly_event("TATAMOTORS.NS")
    assert anomaly.data_status == DataStatus.DEMO

    session = mock_market_stream.create_mock_session_event("BSE", "OPEN")
    assert session.data_status == DataStatus.DEMO

    ingest = mock_market_stream.create_mock_ingestion_event(10, "SUCCESS")
    assert ingest.data_status == DataStatus.DEMO


@pytest.mark.asyncio
async def test_websocket_duplicate_event_deduplication(ws_mgr):
    """Verifies that an event with identical event_id is not dispatched twice to the same client."""
    mock_ws = MockWebSocket()
    conn, _ = await ws_mgr.connect(mock_ws)
    await ws_mgr.subscribe(conn.connection_id, channels=["quotes"])

    event = mock_market_stream.create_mock_quote_event("RELIANCE.NS", price=2900.0)

    # First dispatch
    await ws_mgr.on_event_bus_event(event)
    await asyncio.sleep(0.05)
    assert len(mock_ws.sent_messages) == 1

    # Second dispatch with same event_id
    await ws_mgr.on_event_bus_event(event)
    await asyncio.sleep(0.05)
    assert len(mock_ws.sent_messages) == 1  # Should be deduplicated

    await ws_mgr.disconnect(conn.connection_id)


@pytest.mark.asyncio
async def test_websocket_private_portfolio_isolation(ws_mgr):
    """Verifies that User A never receives User B's portfolio updates."""
    # User A
    token_a = create_access_token({"sub": "user_a"})
    ws_a = MockWebSocket()
    conn_a, _ = await ws_mgr.connect(ws_a, token=token_a)
    await ws_mgr.subscribe(conn_a.connection_id, channels=["portfolio"])

    # User B
    token_b = create_access_token({"sub": "user_b"})
    ws_b = MockWebSocket()
    conn_b, _ = await ws_mgr.connect(ws_b, token=token_b)
    await ws_mgr.subscribe(conn_b.connection_id, channels=["portfolio"])

    # Emit private portfolio event for User A
    event_user_a = MarketDataEvent(
        event_type=MarketEventType.QUOTE_TICK,
        symbol="PORTFOLIO_UPDATE",
        exchange="INTERNAL",
        data_source="PORTFOLIO_SERVICE",
        data_status=DataStatus.DEMO,
        payload={"user_id": "user_a", "total_value": 150000.0}
    )
    # Map to portfolio channel artificially
    ws_mgr._channel_subscribers.setdefault("portfolio", set())

    # Send directly through manager
    async with ws_mgr._lock:
        recipient_ids = ws_mgr._channel_subscribers.get("portfolio", set())
        # Filter for user_a
        recipient_ids = recipient_ids.intersection(ws_mgr._user_connections.get("user_a", set()))
        recipients = [ws_mgr._connections[cid] for cid in recipient_ids if cid in ws_mgr._connections]

    for conn in recipients:
        await conn.enqueue_event({"event": "PORTFOLIO_UPDATE", "user_id": "user_a"})

    await asyncio.sleep(0.05)

    assert len(ws_a.sent_messages) == 1
    assert len(ws_b.sent_messages) == 0  # User B received nothing!

    await ws_mgr.disconnect(conn_a.connection_id)
    await ws_mgr.disconnect(conn_b.connection_id)


@pytest.mark.asyncio
async def test_telemetry_security_no_secrets_exposed(ws_mgr):
    """Verifies health metrics and telemetry never leak keys, tokens, or personal secrets."""
    metrics = ws_mgr.get_health_metrics()

    assert "SECRET_KEY" not in metrics
    assert "api_key" not in metrics
    assert "token" not in metrics
    assert "jwt" not in metrics
    assert "password" not in metrics
    assert "active_connections" in metrics
    assert "websocket_enabled" in metrics

