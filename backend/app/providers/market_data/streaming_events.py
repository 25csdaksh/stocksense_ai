"""
MarketMind AI — Market Data Ingestion & Real-Time Streaming Event Contract.
Phase 6.3: Streaming-ready data event abstraction for live quote ticks, candlestick closures,
indices, and anomaly events.
"""
import uuid
from enum import Enum
from typing import Dict, Any, Optional, List, Callable, Awaitable
from datetime import datetime, timezone
from pydantic import BaseModel, Field

from app.providers.market_data.models import DataStatus


class MarketEventType(str, Enum):
    """Types of real-time market data ingestion events."""
    QUOTE_TICK = "QUOTE_TICK"
    BAR_CLOSED = "BAR_CLOSED"
    INDEX_TICK = "INDEX_TICK"
    ANOMALY_DETECTED = "ANOMALY_DETECTED"
    SESSION_CHANGE = "SESSION_CHANGE"
    INGESTION_CYCLE_COMPLETED = "INGESTION_CYCLE_COMPLETED"


class MarketDataEvent(BaseModel):
    """
    Standardized market data streaming event contract.
    Ready for WebSocket broadcasting and downstream agent/analytics consumers.
    """
    event_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    event_type: MarketEventType = Field(description="Event classification")
    symbol: str = Field(description="Canonical asset or index symbol")
    exchange: str = Field(description="Originating exchange (e.g. NSE, BSE, NASDAQ)")
    timestamp: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    price: Optional[float] = Field(default=None, description="Event price or LTP")
    volume: Optional[float] = Field(default=None, description="Event volume or delta")
    change: Optional[float] = Field(default=None, description="Net price change")
    change_pct: Optional[float] = Field(default=None, description="Percentage change")
    data_source: str = Field(default="COLLECTOR", description="Origin feed provider")
    data_status: DataStatus = Field(default=DataStatus.DEMO, description="Provenance status")
    payload: Dict[str, Any] = Field(default_factory=dict, description="Detailed event attributes")


class MarketDataEventBus:
    """
    Lightweight in-process event bus with support for async subscribers.
    Dispatches ingestion events to registered callbacks and prepares for Redis PubSub.
    """

    def __init__(self):
        self._subscribers: List[Callable[[MarketDataEvent], Awaitable[None]]] = []
        self._event_history: List[MarketDataEvent] = []
        self._max_history = 100

    def subscribe(self, callback: Callable[[MarketDataEvent], Awaitable[None]]) -> None:
        """Registers an async listener callback for streaming events."""
        if callback not in self._subscribers:
            self._subscribers.append(callback)

    def unsubscribe(self, callback: Callable[[MarketDataEvent], Awaitable[None]]) -> None:
        """Removes a registered listener callback."""
        if callback in self._subscribers:
            self._subscribers.remove(callback)

    async def publish(self, event: MarketDataEvent) -> None:
        """Publishes an event to all registered async subscribers."""
        self._event_history.append(event)
        if len(self._event_history) > self._max_history:
            self._event_history.pop(0)

        for callback in list(self._subscribers):
            try:
                await callback(event)
            except Exception:
                pass

    def get_recent_events(self, limit: int = 20) -> List[MarketDataEvent]:
        """Returns recent in-memory streaming events."""
        return self._event_history[-limit:]


event_bus = MarketDataEventBus()
