"""
MarketMind AI — High-Performance Asynchronous WebSocket Streaming Manager.
Phase 6.4: Real-time market streaming engine consuming MarketDataEventBus,
supporting multi-channel & symbol subscriptions, bounded backpressure queues,
JWT authentication, heartbeat tracking, and structured telemetry.
"""
import asyncio
import collections
import time
import uuid
from datetime import datetime, timezone
from enum import Enum
from typing import Dict, Any, Optional, Set, List, Tuple
from fastapi import WebSocket, WebSocketDisconnect

from app.core.config import settings
from app.core.logging import logger
from app.core.security import decode_access_token
from app.providers.market_data.symbol_normalizer import symbol_normalizer
from app.providers.market_data.exceptions import InvalidSymbol
from app.providers.market_data.streaming_events import (
    MarketDataEvent,
    MarketEventType,
    event_bus
)
from app.providers.market_data.models import DataStatus


class ChannelType(str, Enum):
    """Approved public & authenticated WebSocket channels."""
    QUOTES = "quotes"
    INDICES = "indices"
    ANOMALIES = "anomalies"
    MARKET_STATUS = "market_status"
    INGESTION = "ingestion"
    PORTFOLIO = "portfolio"  # Protected private channel (requires auth)


APPROVED_PUBLIC_CHANNELS: Set[str] = {
    ChannelType.QUOTES.value,
    ChannelType.INDICES.value,
    ChannelType.ANOMALIES.value,
    ChannelType.MARKET_STATUS.value,
    ChannelType.INGESTION.value,
}

PROTECTED_CHANNELS: Set[str] = {
    ChannelType.PORTFOLIO.value,
}

# Event priority definitions
EVENT_PRIORITY = {
    MarketEventType.SESSION_CHANGE: 3,     # Highest: must not drop
    MarketEventType.ANOMALY_DETECTED: 3,   # Highest: alert criticality
    MarketEventType.INDEX_TICK: 2,         # Normal
    MarketEventType.QUOTE_TICK: 2,         # Normal
    MarketEventType.BAR_CLOSED: 2,         # Normal
    MarketEventType.INGESTION_CYCLE_COMPLETED: 1  # Lower: telemetry
}


class WebSocketConnection:
    """Represents a single active client WebSocket session."""

    def __init__(self, websocket: WebSocket, connection_id: Optional[str] = None):
        self.connection_id: str = connection_id or str(uuid.uuid4())
        self.websocket: WebSocket = websocket
        self.user_id: Optional[str] = None
        self.is_authenticated: bool = False
        self.subscribed_symbols: Set[str] = set()
        self.subscribed_channels: Set[str] = set()
        self.connected_at: datetime = datetime.now(timezone.utc)
        self.last_heartbeat: datetime = datetime.now(timezone.utc)
        self.last_activity: datetime = datetime.now(timezone.utc)
        self.outgoing_queue: asyncio.Queue = asyncio.Queue(maxsize=settings.WS_QUEUE_MAX_SIZE)
        self.send_task: Optional[asyncio.Task] = None
        self.is_closed: bool = False
        self._sent_event_ids: collections.deque = collections.deque(maxlen=150)

    def update_heartbeat(self) -> None:
        """Refreshes heartbeat and activity timestamps."""
        now = datetime.now(timezone.utc)
        self.last_heartbeat = now
        self.last_activity = now

    def update_activity(self) -> None:
        """Refreshes client activity timestamp."""
        self.last_activity = datetime.now(timezone.utc)

    def is_duplicate(self, event_id: str) -> bool:
        """Checks whether event has already been sent to this connection."""
        if not event_id:
            return False
        return event_id in self._sent_event_ids

    def mark_sent(self, event_id: str) -> None:
        """Records event id in connection deduplication ring."""
        if event_id:
            self._sent_event_ids.append(event_id)

    async def enqueue_event(self, event_payload: Dict[str, Any], priority: int = 2) -> bool:
        """
        Enqueues an outgoing event applying priority-aware bounded backpressure.
        Returns True if enqueued, False if dropped due to queue congestion.
        """
        if self.is_closed:
            return False

        if not self.outgoing_queue.full():
            self.outgoing_queue.put_nowait(event_payload)
            return True

        # Backpressure condition: Queue is full
        if priority >= 3:
            # High priority (Session changes, Anomalies): evict oldest item to make space
            try:
                _ = self.outgoing_queue.get_nowait()
                self.outgoing_queue.task_done()
            except asyncio.QueueEmpty:
                pass
            self.outgoing_queue.put_nowait(event_payload)
            return True

        # Normal/Low priority dropped when client is congested
        return False


class WebSocketManager:
    """
    Central WebSocket Manager for real-time market data streaming.
    Bridges MarketDataEventBus to connected WebSocket clients with
    subscription filtering, authentication, backpressure, and health metrics.
    """

    def __init__(self):
        self._connections: Dict[str, WebSocketConnection] = {}
        self._symbol_subscribers: Dict[str, Set[str]] = {}
        self._channel_subscribers: Dict[str, Set[str]] = {}
        self._user_connections: Dict[str, Set[str]] = {}

        # Telemetry & Metrics
        self._connections_total: int = 0
        self._connections_rejected: int = 0
        self._subscriptions_total: int = 0
        self._events_sent: int = 0
        self._events_dropped: int = 0
        self._authentication_failures: int = 0
        self._disconnects: int = 0
        self._last_event_timestamp: Optional[str] = None
        self._event_timestamps_window: collections.deque = collections.deque(maxlen=500)

        # Event bus registration flag
        self._subscribed_to_bus: bool = False
        self._cleanup_task: Optional[asyncio.Task] = None
        self._lock = asyncio.Lock()

    def start(self) -> None:
        """Subscribes to MarketDataEventBus and begins periodic tasks."""
        if not self._subscribed_to_bus:
            event_bus.subscribe(self.on_event_bus_event)
            self._subscribed_to_bus = True
            logger.info("WebSocketManager successfully subscribed to MarketDataEventBus.")

    def stop(self) -> None:
        """Unsubscribes from event bus and cleans up background tasks."""
        if self._subscribed_to_bus:
            event_bus.unsubscribe(self.on_event_bus_event)
            self._subscribed_to_bus = False
        if self._cleanup_task and not self._cleanup_task.done():
            self._cleanup_task.cancel()

    async def connect(
        self,
        websocket: WebSocket,
        token: Optional[str] = None
    ) -> Tuple[Optional[WebSocketConnection], Optional[str]]:
        """
        Accepts WebSocket connection, applies connection limits, and optionally authenticates JWT.
        Returns (connection, error_message).
        """
        # Connection capacity check
        if len(self._connections) >= settings.WS_MAX_CONNECTIONS:
            self._connections_rejected += 1
            logger.warning(f"WebSocket rejected: MAX_CONNECTIONS ({settings.WS_MAX_CONNECTIONS}) reached.")
            return None, "Server connection limit reached"

        await websocket.accept()
        conn = WebSocketConnection(websocket=websocket)

        # Authenticate if token provided at handshake
        if token:
            payload = decode_access_token(token)
            if payload:
                user_id = str(payload.get("sub") or payload.get("user_id") or "")
                conn.user_id = user_id
                conn.is_authenticated = True
                async with self._lock:
                    if user_id not in self._user_connections:
                        self._user_connections[user_id] = set()
                    self._user_connections[user_id].add(conn.connection_id)
                logger.info(f"WebSocket client authenticated: user_id={user_id}, conn_id={conn.connection_id}")
            else:
                self._authentication_failures += 1
                logger.warning(f"WebSocket handshake token invalid for conn_id={conn.connection_id}")

        async with self._lock:
            self._connections[conn.connection_id] = conn
            self._connections_total += 1

        # Start dedicated sender worker for this connection
        conn.send_task = asyncio.create_task(self._client_sender_worker(conn))

        # Ensure event bus integration is active
        self.start()

        logger.info(f"WebSocket client connected: id={conn.connection_id}, total_active={len(self._connections)}")
        return conn, None

    async def disconnect(self, connection_id: str) -> None:
        """Gracefully disconnects and cleans up a client session."""
        async with self._lock:
            conn = self._connections.pop(connection_id, None)
            if not conn:
                return

            conn.is_closed = True

            # Cancel send worker
            if conn.send_task and not conn.send_task.done():
                conn.send_task.cancel()

            # Clean up symbol index
            for symbol in conn.subscribed_symbols:
                if symbol in self._symbol_subscribers:
                    self._symbol_subscribers[symbol].discard(connection_id)
                    if not self._symbol_subscribers[symbol]:
                        del self._symbol_subscribers[symbol]

            # Clean up channel index
            for channel in conn.subscribed_channels:
                if channel in self._channel_subscribers:
                    self._channel_subscribers[channel].discard(connection_id)
                    if not self._channel_subscribers[channel]:
                        del self._channel_subscribers[channel]

            # Clean up user index
            if conn.user_id and conn.user_id in self._user_connections:
                self._user_connections[conn.user_id].discard(connection_id)
                if not self._user_connections[conn.user_id]:
                    del self._user_connections[conn.user_id]

            self._disconnects += 1

        logger.info(f"WebSocket client disconnected: id={connection_id}, remaining_active={len(self._connections)}")

    async def authenticate_connection(self, connection_id: str, token: str) -> Dict[str, Any]:
        """Authenticates an existing connection using JWT token."""
        conn = self._connections.get(connection_id)
        if not conn:
            return {"event": "ERROR", "code": "CONNECTION_NOT_FOUND", "message": "Connection not found"}

        payload = decode_access_token(token)
        if not payload:
            self._authentication_failures += 1
            return {"event": "ERROR", "code": "AUTH_FAILED", "message": "Invalid or expired token"}

        user_id = str(payload.get("sub") or payload.get("user_id") or "")
        conn.user_id = user_id
        conn.is_authenticated = True

        async with self._lock:
            if user_id not in self._user_connections:
                self._user_connections[user_id] = set()
            self._user_connections[user_id].add(connection_id)

        conn.update_activity()
        return {
            "event": "AUTH_SUCCESS",
            "connection_id": connection_id,
            "user_id": user_id,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }

    async def subscribe(
        self,
        connection_id: str,
        symbols: Optional[List[str]] = None,
        channels: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Subscribes a client to financial symbols and/or market channels.
        Validates symbols and channel permissions.
        """
        conn = self._connections.get(connection_id)
        if not conn:
            return {"event": "ERROR", "code": "CONNECTION_NOT_FOUND", "message": "Connection not found"}

        conn.update_activity()
        symbols = symbols or []
        channels = channels or []

        if not symbols and not channels:
            return {
                "event": "ERROR",
                "code": "EMPTY_SUBSCRIPTION",
                "message": "Must specify at least one symbol or channel to subscribe."
            }

        added_symbols: List[str] = []
        added_channels: List[str] = []
        rejected_symbols: List[Dict[str, str]] = []
        rejected_channels: List[Dict[str, str]] = []

        async with self._lock:
            # Process Channel Subscriptions
            for ch in channels:
                ch_clean = ch.strip().lower()
                if ch_clean in PROTECTED_CHANNELS and not conn.is_authenticated:
                    rejected_channels.append({
                        "channel": ch,
                        "reason": f"Channel '{ch}' requires authentication."
                    })
                    continue

                if ch_clean not in APPROVED_PUBLIC_CHANNELS and ch_clean not in PROTECTED_CHANNELS:
                    rejected_channels.append({
                        "channel": ch,
                        "reason": f"Channel '{ch}' is not supported. Valid channels: {sorted(list(APPROVED_PUBLIC_CHANNELS | PROTECTED_CHANNELS))}"
                    })
                    continue

                if len(conn.subscribed_channels) >= settings.WS_MAX_CHANNELS_PER_CLIENT:
                    rejected_channels.append({
                        "channel": ch,
                        "reason": f"Exceeded max channels limit ({settings.WS_MAX_CHANNELS_PER_CLIENT})"
                    })
                    continue

                conn.subscribed_channels.add(ch_clean)
                if ch_clean not in self._channel_subscribers:
                    self._channel_subscribers[ch_clean] = set()
                self._channel_subscribers[ch_clean].add(connection_id)
                added_channels.append(ch_clean)
                self._subscriptions_total += 1

            # Process Symbol Subscriptions
            for sym in symbols:
                if len(conn.subscribed_symbols) >= settings.WS_MAX_SYMBOLS_PER_CLIENT:
                    rejected_symbols.append({
                        "symbol": sym,
                        "reason": f"Exceeded max symbols limit ({settings.WS_MAX_SYMBOLS_PER_CLIENT})"
                    })
                    continue

                try:
                    norm = symbol_normalizer.normalize(sym)
                    canonical = norm.canonical_symbol
                    conn.subscribed_symbols.add(canonical)
                    if canonical not in self._symbol_subscribers:
                        self._symbol_subscribers[canonical] = set()
                    self._symbol_subscribers[canonical].add(connection_id)
                    added_symbols.append(canonical)
                    self._subscriptions_total += 1
                except InvalidSymbol as ex:
                    rejected_symbols.append({"symbol": sym, "reason": str(ex)})
                except Exception as ex:
                    rejected_symbols.append({"symbol": sym, "reason": f"Invalid symbol format: {str(ex)}"})

        response: Dict[str, Any] = {
            "event": "SUBSCRIPTION_SUCCESS",
            "connection_id": connection_id,
            "subscribed_symbols": sorted(list(conn.subscribed_symbols)),
            "subscribed_channels": sorted(list(conn.subscribed_channels)),
            "added_symbols": added_symbols,
            "added_channels": added_channels,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }

        if rejected_symbols:
            response["rejected_symbols"] = rejected_symbols
        if rejected_channels:
            response["rejected_channels"] = rejected_channels

        return response

    async def unsubscribe(
        self,
        connection_id: str,
        symbols: Optional[List[str]] = None,
        channels: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """Unsubscribes a client from symbols or channels."""
        conn = self._connections.get(connection_id)
        if not conn:
            return {"event": "ERROR", "code": "CONNECTION_NOT_FOUND", "message": "Connection not found"}

        conn.update_activity()
        symbols = symbols or []
        channels = channels or []

        removed_symbols: List[str] = []
        removed_channels: List[str] = []

        async with self._lock:
            for ch in channels:
                ch_clean = ch.strip().lower()
                if ch_clean in conn.subscribed_channels:
                    conn.subscribed_channels.remove(ch_clean)
                    if ch_clean in self._channel_subscribers:
                        self._channel_subscribers[ch_clean].discard(connection_id)
                    removed_channels.append(ch_clean)

            for sym in symbols:
                # Try raw or normalized matching
                target_sym = sym
                try:
                    target_sym = symbol_normalizer.normalize(sym).canonical_symbol
                except Exception:
                    pass

                if target_sym in conn.subscribed_symbols:
                    conn.subscribed_symbols.remove(target_sym)
                    if target_sym in self._symbol_subscribers:
                        self._symbol_subscribers[target_sym].discard(connection_id)
                    removed_symbols.append(target_sym)
                elif sym in conn.subscribed_symbols:
                    conn.subscribed_symbols.remove(sym)
                    if sym in self._symbol_subscribers:
                        self._symbol_subscribers[sym].discard(connection_id)
                    removed_symbols.append(sym)

        return {
            "event": "UNSUBSCRIPTION_SUCCESS",
            "connection_id": connection_id,
            "removed_symbols": removed_symbols,
            "removed_channels": removed_channels,
            "subscribed_symbols": sorted(list(conn.subscribed_symbols)),
            "subscribed_channels": sorted(list(conn.subscribed_channels)),
            "timestamp": datetime.now(timezone.utc).isoformat()
        }

    def list_subscriptions(self, connection_id: str) -> Dict[str, Any]:
        """Returns current subscriptions for the given connection."""
        conn = self._connections.get(connection_id)
        if not conn:
            return {"event": "ERROR", "code": "CONNECTION_NOT_FOUND", "message": "Connection not found"}

        conn.update_activity()
        return {
            "event": "SUBSCRIPTIONS",
            "connection_id": connection_id,
            "symbols": sorted(list(conn.subscribed_symbols)),
            "channels": sorted(list(conn.subscribed_channels)),
            "is_authenticated": conn.is_authenticated,
            "user_id": conn.user_id,
            "connected_at": conn.connected_at.isoformat(),
            "timestamp": datetime.now(timezone.utc).isoformat()
        }

    def handle_ping(self, connection_id: str) -> Dict[str, Any]:
        """Processes a client heartbeat ping and returns a pong envelope."""
        conn = self._connections.get(connection_id)
        if conn:
            conn.update_heartbeat()
        return {
            "event": "pong",
            "connection_id": connection_id,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }

    async def on_event_bus_event(self, event: MarketDataEvent) -> None:
        """
        Callback triggered whenever MarketDataEventBus publishes an event.
        Dispatches normalized messages to subscribed WebSocket clients.
        """
        now_ts = datetime.now(timezone.utc).isoformat()
        self._last_event_timestamp = now_ts
        self._event_timestamps_window.append(time.time())

        # Map event type to primary channel
        channel = self._map_event_to_channel(event.event_type)
        priority = EVENT_PRIORITY.get(event.event_type, 2)

        # Normalize outgoing payload
        outgoing_msg = self._normalize_outgoing_event(event)

        # Identify recipient connection IDs
        recipient_ids: Set[str] = set()

        async with self._lock:
            # 1. Channel subscribers
            if channel and channel in self._channel_subscribers:
                recipient_ids.update(self._channel_subscribers[channel])

            # 2. Specific symbol subscribers
            canonical_symbol = event.symbol
            if canonical_symbol in self._symbol_subscribers:
                recipient_ids.update(self._symbol_subscribers[canonical_symbol])

            # 3. Private / Portfolio events isolation check
            if channel == ChannelType.PORTFOLIO.value:
                owner_id = event.payload.get("user_id")
                if owner_id and owner_id in self._user_connections:
                    recipient_ids = recipient_ids.intersection(self._user_connections[owner_id])
                else:
                    recipient_ids = set()

            recipients = [self._connections[cid] for cid in recipient_ids if cid in self._connections]

        # Dispatch non-blockingly to all matched client queues
        for conn in recipients:
            if conn.is_duplicate(event.event_id):
                continue
            conn.mark_sent(event.event_id)
            enqueued = await conn.enqueue_event(outgoing_msg, priority=priority)
            if not enqueued:
                self._events_dropped += 1

    def _map_event_to_channel(self, event_type: MarketEventType) -> Optional[str]:
        """Maps MarketEventType to standardized public/private channel."""
        mapping = {
            MarketEventType.QUOTE_TICK: ChannelType.QUOTES.value,
            MarketEventType.BAR_CLOSED: ChannelType.QUOTES.value,
            MarketEventType.INDEX_TICK: ChannelType.INDICES.value,
            MarketEventType.ANOMALY_DETECTED: ChannelType.ANOMALIES.value,
            MarketEventType.SESSION_CHANGE: ChannelType.MARKET_STATUS.value,
            MarketEventType.INGESTION_CYCLE_COMPLETED: ChannelType.INGESTION.value,
        }
        return mapping.get(event_type)

    def _normalize_outgoing_event(self, event: MarketDataEvent) -> Dict[str, Any]:
        """
        Normalizes internal MarketDataEvent into a standard client-safe dictionary.
        Enforces data_status / data_source provenance rules.
        """
        status_val = event.data_status.value if hasattr(event.data_status, "value") else str(event.data_status)

        # High-level clean payload
        payload = dict(event.payload) if event.payload else {}
        if event.price is not None and "price" not in payload:
            payload["price"] = event.price
        if event.volume is not None and "volume" not in payload:
            payload["volume"] = event.volume
        if event.change is not None and "change" not in payload:
            payload["change"] = event.change
        if event.change_pct is not None and "change_percent" not in payload:
            payload["change_percent"] = event.change_pct

        # For Ingestion events, strip sensitive telemetry
        if event.event_type == MarketEventType.INGESTION_CYCLE_COMPLETED:
            clean_payload = {
                "symbols_processed": payload.get("symbols_processed", 0),
                "status": payload.get("status", "SUCCESS"),
                "mode": payload.get("mode", "SCHEDULED"),
            }
            payload = clean_payload

        return {
            "event": event.event_type.value if hasattr(event.event_type, "value") else str(event.event_type),
            "event_id": event.event_id,
            "symbol": event.symbol,
            "exchange": event.exchange,
            "timestamp": event.timestamp,
            "data_status": status_val,
            "data_source": event.data_source,
            "payload": payload
        }

    async def _client_sender_worker(self, conn: WebSocketConnection) -> None:
        """Dedicated background task per connection draining its outgoing queue."""
        try:
            while not conn.is_closed:
                msg = await conn.outgoing_queue.get()
                try:
                    await conn.websocket.send_json(msg)
                    self._events_sent += 1
                except Exception as ex:
                    logger.debug(f"Error sending to WebSocket client {conn.connection_id}: {ex}")
                    break
                finally:
                    conn.outgoing_queue.task_done()
        except asyncio.CancelledError:
            pass
        except Exception as ex:
            logger.debug(f"Sender worker exited for {conn.connection_id}: {ex}")
        finally:
            conn.is_closed = True

    async def cleanup_stale_connections(self) -> int:
        """Disconnects connections that exceeded heartbeat timeout."""
        now = datetime.now(timezone.utc)
        timeout_seconds = settings.WS_HEARTBEAT_TIMEOUT_SECONDS
        stale_ids: List[str] = []

        async with self._lock:
            for cid, conn in self._connections.items():
                elapsed = (now - conn.last_heartbeat).total_seconds()
                if elapsed > timeout_seconds:
                    stale_ids.append(cid)

        for cid in stale_ids:
            logger.info(f"Disconnecting stale WebSocket client {cid} due to heartbeat timeout.")
            await self.disconnect(cid)

        return len(stale_ids)

    def get_health_metrics(self) -> Dict[str, Any]:
        """Returns real-time streaming health and telemetry metrics."""
        now = time.time()
        # Calculate events per second in sliding 60s window
        recent_events = [t for t in self._event_timestamps_window if (now - t) <= 60.0]
        eps = round(len(recent_events) / 60.0, 2) if recent_events else 0.0

        total_subs = sum(len(c.subscribed_symbols) + len(c.subscribed_channels) for c in self._connections.values())

        return {
            "websocket_enabled": True,
            "active_connections": len(self._connections),
            "active_subscriptions": total_subs,
            "events_per_second": eps,
            "dropped_events": self._events_dropped,
            "last_event_timestamp": self._last_event_timestamp,
            "telemetry": {
                "connections_total": self._connections_total,
                "active_connections": len(self._connections),
                "connections_rejected": self._connections_rejected,
                "subscriptions_total": self._subscriptions_total,
                "events_sent": self._events_sent,
                "events_dropped": self._events_dropped,
                "authentication_failures": self._authentication_failures,
                "disconnects": self._disconnects
            }
        }


# Global singleton instance
websocket_manager = WebSocketManager()
