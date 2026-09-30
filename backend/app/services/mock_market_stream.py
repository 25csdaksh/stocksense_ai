"""
MarketMind AI — Mock Market Stream Event Generator (Dev & Testing Mode).
Phase 6.4: Explicit mock/test event source when real Zerodha credentials are unconfigured.
CRITICAL: All generated events are strictly marked data_status = DEMO and data_source = DEMO.
Never label simulated mock data as LIVE.
"""
import random
import uuid
from datetime import datetime, timezone
from typing import Optional, Dict, Any, List

from app.providers.market_data.models import DataStatus
from app.providers.market_data.streaming_events import (
    MarketDataEvent,
    MarketEventType,
    event_bus
)


class MockMarketStreamService:
    """
    Simulated real-time market stream generator for testing and offline development.
    Guarantees strict provenance labeling (DEMO status).
    """

    @staticmethod
    def create_mock_quote_event(
        symbol: str = "RELIANCE.NS",
        price: Optional[float] = None,
        change_pct: Optional[float] = None,
        exchange: str = "NSE"
    ) -> MarketDataEvent:
        """Creates a mock tick event marked data_status=DEMO."""
        base_price = price if price is not None else round(random.uniform(100.0, 3500.0), 2)
        pct = change_pct if change_pct is not None else round(random.uniform(-3.5, 3.5), 2)
        chg = round(base_price * (pct / 100.0), 2)
        vol = round(random.uniform(500, 25000), 0)

        return MarketDataEvent(
            event_id=f"demo-quote-{uuid.uuid4().hex[:8]}",
            event_type=MarketEventType.QUOTE_TICK,
            symbol=symbol,
            exchange=exchange,
            timestamp=datetime.now(timezone.utc).isoformat(),
            price=base_price,
            volume=vol,
            change=chg,
            change_pct=pct,
            data_source="DEMO",
            data_status=DataStatus.DEMO,
            payload={
                "price": base_price,
                "volume": vol,
                "change": chg,
                "change_percent": pct,
                "day_high": round(base_price * 1.02, 2),
                "day_low": round(base_price * 0.98, 2),
                "is_simulated": True
            }
        )

    @staticmethod
    def create_mock_index_event(
        symbol: str = "^NSEI",
        price: Optional[float] = None,
        exchange: str = "NSE"
    ) -> MarketDataEvent:
        """Creates a mock benchmark index tick event marked data_status=DEMO."""
        idx_price = price if price is not None else 24850.75
        pct = round(random.uniform(-1.2, 1.2), 2)
        return MarketDataEvent(
            event_id=f"demo-idx-{uuid.uuid4().hex[:8]}",
            event_type=MarketEventType.INDEX_TICK,
            symbol=symbol,
            exchange=exchange,
            timestamp=datetime.now(timezone.utc).isoformat(),
            price=idx_price,
            change_pct=pct,
            data_source="DEMO",
            data_status=DataStatus.DEMO,
            payload={
                "index_name": "NIFTY 50" if symbol == "^NSEI" else symbol,
                "value": idx_price,
                "change_percent": pct,
                "is_simulated": True
            }
        )

    @staticmethod
    def create_mock_anomaly_event(
        symbol: str = "RELIANCE.NS",
        anomaly_type: str = "VOLATILITY_SPIKE",
        severity: str = "HIGH",
        score: float = 0.88,
        exchange: str = "NSE"
    ) -> MarketDataEvent:
        """Creates a mock anomaly event marked data_status=DEMO."""
        return MarketDataEvent(
            event_id=f"demo-anomaly-{uuid.uuid4().hex[:8]}",
            event_type=MarketEventType.ANOMALY_DETECTED,
            symbol=symbol,
            exchange=exchange,
            timestamp=datetime.now(timezone.utc).isoformat(),
            data_source="DEMO",
            data_status=DataStatus.DEMO,
            payload={
                "anomaly_type": anomaly_type,
                "severity": severity,
                "confidence_score": score,
                "detection_model": "GARCH_MOCK_VOLATILITY",
                "is_simulated": True
            }
        )

    @staticmethod
    def create_mock_session_event(
        exchange: str = "NSE",
        new_status: str = "OPEN"
    ) -> MarketDataEvent:
        """Creates a mock market session transition event marked data_status=DEMO."""
        return MarketDataEvent(
            event_id=f"demo-session-{uuid.uuid4().hex[:8]}",
            event_type=MarketEventType.SESSION_CHANGE,
            symbol=exchange,
            exchange=exchange,
            timestamp=datetime.now(timezone.utc).isoformat(),
            data_source="DEMO",
            data_status=DataStatus.DEMO,
            payload={
                "exchange": exchange,
                "status": new_status,
                "is_open": new_status.upper() == "OPEN",
                "is_simulated": True
            }
        )

    @staticmethod
    def create_mock_ingestion_event(
        symbols_processed: int = 12,
        status: str = "SUCCESS"
    ) -> MarketDataEvent:
        """Creates a mock ingestion cycle completion event marked data_status=DEMO."""
        return MarketDataEvent(
            event_id=f"demo-ingest-{uuid.uuid4().hex[:8]}",
            event_type=MarketEventType.INGESTION_CYCLE_COMPLETED,
            symbol="MARKET_UNIVERSE",
            exchange="ALL",
            timestamp=datetime.now(timezone.utc).isoformat(),
            data_source="DEMO",
            data_status=DataStatus.DEMO,
            payload={
                "symbols_processed": symbols_processed,
                "status": status,
                "mode": "SCHEDULED",
                "is_simulated": True
            }
        )

    async def emit_event(self, event: MarketDataEvent) -> None:
        """Publishes a mock event to the MarketDataEventBus."""
        await event_bus.publish(event)

    async def emit_sample_cycle(self) -> List[MarketDataEvent]:
        """Emits a diverse batch of demo events across multiple channels for testing."""
        events = [
            self.create_mock_quote_event("RELIANCE.NS", price=2980.50, change_pct=1.45),
            self.create_mock_quote_event("TCS.NS", price=3950.00, change_pct=-0.65),
            self.create_mock_quote_event("AAPL", price=232.10, change_pct=0.85, exchange="NASDAQ"),
            self.create_mock_index_event("^NSEI", price=24900.25),
            self.create_mock_anomaly_event("RELIANCE.NS", score=0.92),
            self.create_mock_session_event("NSE", new_status="OPEN"),
            self.create_mock_ingestion_event(symbols_processed=15, status="SUCCESS")
        ]
        for ev in events:
            await self.emit_event(ev)
        return events


mock_market_stream = MockMarketStreamService()
