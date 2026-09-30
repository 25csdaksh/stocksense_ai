"""
MarketMind AI — Real-Time Market Streaming WebSocket Endpoints.
Phase 6.4: WebSocket endpoint at /api/v1/ws/market supporting subscription,
heartbeat, authentication, backpressure, and streaming telemetry health.
"""
import json
from datetime import datetime, timezone
from typing import Optional
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Query, status
from app.core.config import settings
from app.core.logging import logger
from app.services.websocket_manager import websocket_manager

router = APIRouter(tags=["Market Streaming"])


@router.websocket("/ws/market")
async def market_websocket_endpoint(
    websocket: WebSocket,
    token: Optional[str] = Query(default=None, description="Optional JWT for authenticated sessions")
):
    """
    Bidirectional WebSocket connection for real-time market data streaming.
    Supports subscriptions to symbols ('RELIANCE.NS') and channels ('quotes', 'indices', 'anomalies', 'market_status', 'ingestion').
    """
    conn, reject_reason = await websocket_manager.connect(websocket, token=token)
    if not conn:
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION, reason=reject_reason or "Connection rejected")
        return

    # Send initial connection handshake confirmation
    welcome_payload = {
        "event": "CONNECTED",
        "connection_id": conn.connection_id,
        "server_time": datetime.now(timezone.utc).isoformat(),
        "is_authenticated": conn.is_authenticated,
        "user_id": conn.user_id,
        "data_status": "DEMO",
        "supported_channels": ["quotes", "indices", "anomalies", "market_status", "ingestion"]
    }
    await websocket.send_json(welcome_payload)

    try:
        while True:
            # Receive raw message text to guard against oversized payloads
            raw_text = await websocket.receive_text()

            if len(raw_text.encode("utf-8")) > settings.WS_MAX_MESSAGE_SIZE:
                await websocket.send_json({
                    "event": "ERROR",
                    "code": "MESSAGE_TOO_LARGE",
                    "message": f"Payload exceeds maximum allowed size of {settings.WS_MAX_MESSAGE_SIZE} bytes."
                })
                continue

            try:
                msg = json.loads(raw_text)
            except Exception:
                await websocket.send_json({
                    "event": "ERROR",
                    "code": "INVALID_JSON",
                    "message": "Malformed JSON payload received."
                })
                continue

            if not isinstance(msg, dict):
                await websocket.send_json({
                    "event": "ERROR",
                    "code": "INVALID_FORMAT",
                    "message": "Message must be a JSON object."
                })
                continue

            action = msg.get("action", "").strip().lower()

            if action == "ping":
                resp = websocket_manager.handle_ping(conn.connection_id)
                await websocket.send_json(resp)

            elif action == "subscribe":
                symbols = msg.get("symbols", [])
                channels = msg.get("channels", [])
                if isinstance(symbols, str):
                    symbols = [symbols]
                if isinstance(channels, str):
                    channels = [channels]

                resp = await websocket_manager.subscribe(
                    connection_id=conn.connection_id,
                    symbols=symbols,
                    channels=channels
                )
                await websocket.send_json(resp)

            elif action == "unsubscribe":
                symbols = msg.get("symbols", [])
                channels = msg.get("channels", [])
                if isinstance(symbols, str):
                    symbols = [symbols]
                if isinstance(channels, str):
                    channels = [channels]

                resp = await websocket_manager.unsubscribe(
                    connection_id=conn.connection_id,
                    symbols=symbols,
                    channels=channels
                )
                await websocket.send_json(resp)

            elif action == "list_subscriptions":
                resp = websocket_manager.list_subscriptions(conn.connection_id)
                await websocket.send_json(resp)

            elif action == "auth":
                auth_token = msg.get("token")
                if not auth_token:
                    await websocket.send_json({
                        "event": "ERROR",
                        "code": "MISSING_TOKEN",
                        "message": "No token provided in auth action."
                    })
                else:
                    resp = await websocket_manager.authenticate_connection(conn.connection_id, auth_token)
                    await websocket.send_json(resp)

            else:
                await websocket.send_json({
                    "event": "ERROR",
                    "code": "UNKNOWN_ACTION",
                    "message": f"Action '{action}' is not supported. Supported actions: subscribe, unsubscribe, list_subscriptions, ping, auth."
                })

    except WebSocketDisconnect:
        await websocket_manager.disconnect(conn.connection_id)
    except Exception as ex:
        logger.debug(f"WebSocket exception for {conn.connection_id}: {ex}")
        await websocket_manager.disconnect(conn.connection_id)


@router.get("/market/stream/health")
async def get_stream_health():
    """Returns streaming infrastructure health, active connections, and subscription metrics."""
    return websocket_manager.get_health_metrics()
