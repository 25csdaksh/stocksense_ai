"""
MarketMind AI — Production Market Data Collector Service.
Phase 6.3: Continuous & on-demand ingestion service for multi-market quotes, indices, and real-time events.
Supports configurable universes, failure isolation, Redis caching, streaming events, and structured telemetry.
"""
import time
import uuid
from enum import Enum
from typing import List, Dict, Any, Optional, Set
from datetime import datetime, timezone
from pydantic import BaseModel, Field

from app.core.config import settings
from app.core.logging import logger
from app.providers.market_data.models import (
    NormalizedQuote,
    MarketIndexQuote,
    ProviderStatus,
    DataStatus
)
from app.providers.market_data.factory import provider_factory
from app.providers.market_data.validator import MarketDataValidator
from app.providers.market_data.symbol_normalizer import normalize_symbol
from app.providers.market_data.session import market_session_manager
from app.providers.market_data.observability import log_market_data_operation
from app.providers.market_data.streaming_events import (
    MarketDataEvent,
    MarketEventType,
    event_bus
)
from app.cache.market_cache import market_cache
from app.services.market_ingestion_service import market_ingestion_service
from app.db.session import async_session_factory


class CollectionMode(str, Enum):
    """Operational mode for data collection."""
    MANUAL = "MANUAL"
    ON_DEMAND = "ON_DEMAND"
    SCHEDULED = "SCHEDULED"
    STREAMING_READY = "STREAMING_READY"


class CollectorCycleResult(BaseModel):
    """Structured telemetry emitted at the end of each collection cycle."""
    cycle_id: str = Field(default_factory=lambda: str(uuid.uuid4())[:8])
    timestamp: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    mode: CollectionMode = CollectionMode.ON_DEMAND
    records_requested: int = 0
    records_received: int = 0
    records_valid: int = 0
    records_rejected: int = 0
    records_persisted: int = 0
    failed_symbols: List[str] = Field(default_factory=list)
    latency_ms: float = 0.0
    provider_name: str = "MarketDataProviderFactory"
    provider_status: str = "LIVE"
    quotes: List[NormalizedQuote] = Field(default_factory=list)
    indices: List[MarketIndexQuote] = Field(default_factory=list)


# Default Core Market Universes
DEFAULT_INDIAN_EQUITIES = [
    "RELIANCE.NS", "TCS.NS", "INFY.NS", "HDFCBANK.NS",
    "ICICIBANK.NS", "SBIN.NS", "ITC.NS", "TATAMOTORS.NS"
]

DEFAULT_INDIAN_INDICES = [
    "NIFTY 50", "NIFTY BANK", "NIFTY IT", "SENSEX"
]

DEFAULT_US_EQUITIES = [
    "AAPL", "MSFT", "NVDA", "GOOGL", "AMZN", "TSLA"
]

DEFAULT_US_INDICES = [
    "S&P 500", "NASDAQ"
]


class MarketDataCollector:
    """
    Centralized collector service orchestrating market data acquisition, validation,
    cache publishing, and event dispatch.
    """

    def __init__(self):
        self._monitored_equities: Set[str] = set(DEFAULT_INDIAN_EQUITIES + DEFAULT_US_EQUITIES)
        self._monitored_indices: Set[str] = set(DEFAULT_INDIAN_INDICES + DEFAULT_US_INDICES)
        self._last_cycle_result: Optional[CollectorCycleResult] = None
        self._total_records_processed: int = 0
        self._total_cycles_completed: int = 0

    # =========================================================================
    # Universe Management
    # =========================================================================

    def get_monitored_universe(self) -> Dict[str, List[str]]:
        """Returns the currently active configured symbol universe."""
        return {
            "equities": sorted(list(self._monitored_equities)),
            "indices": sorted(list(self._monitored_indices)),
            "total_symbols": len(self._monitored_equities) + len(self._monitored_indices)
        }

    def add_symbol_to_universe(self, symbol: str) -> None:
        """Adds a new equity or index to the monitored universe."""
        norm = normalize_symbol(symbol)
        if norm.is_index:
            self._monitored_indices.add(norm.display_symbol)
        else:
            self._monitored_equities.add(norm.canonical_symbol)
        logger.info(f"MarketDataCollector added '{symbol}' to monitored universe.")

    def remove_symbol_from_universe(self, symbol: str) -> bool:
        """Removes a symbol from the monitored universe."""
        norm = normalize_symbol(symbol)
        removed = False
        if norm.canonical_symbol in self._monitored_equities:
            self._monitored_equities.remove(norm.canonical_symbol)
            removed = True
        if norm.display_symbol in self._monitored_indices:
            self._monitored_indices.remove(norm.display_symbol)
            removed = True
        return removed

    def reset_default_universe(self) -> None:
        """Resets monitored universe to factory defaults."""
        self._monitored_equities = set(DEFAULT_INDIAN_EQUITIES + DEFAULT_US_EQUITIES)
        self._monitored_indices = set(DEFAULT_INDIAN_INDICES + DEFAULT_US_INDICES)

    # =========================================================================
    # Real-Time Quote Collection with Failure Isolation
    # =========================================================================

    async def collect_quotes(
        self,
        symbols: Optional[List[str]] = None,
        mode: CollectionMode = CollectionMode.ON_DEMAND
    ) -> CollectorCycleResult:
        """
        Collects real-time quotes for the given symbols (or full monitored universe).
        Executes normalization, validation, Redis caching, event streaming, and failure isolation.
        """
        start_t = time.time()
        target_symbols = symbols if symbols is not None else list(self._monitored_equities)
        cycle_result = CollectorCycleResult(
            mode=mode,
            records_requested=len(target_symbols)
        )

        valid_quotes: List[NormalizedQuote] = []

        for sym in target_symbols:
            try:
                norm = normalize_symbol(sym)
                provider = provider_factory.get_provider(symbol=norm.canonical_symbol)

                # 1. Fetch quote from resolved provider
                quote = await provider.get_quote(norm.canonical_symbol)
                cycle_result.records_received += 1

                # 2. Enforce Financial Validation
                is_valid, err_reason = MarketDataValidator.validate_quote(quote)
                if not is_valid:
                    cycle_result.records_rejected += 1
                    logger.warning(f"Collector rejected invalid quote for '{sym}': {err_reason}")
                    continue

                cycle_result.records_valid += 1
                valid_quotes.append(quote)

                # 3. Update Redis Cache
                await market_cache.set_quote(norm.canonical_symbol, quote.model_dump())

                # 4. Dispatch Streaming Event
                event = MarketDataEvent(
                    event_type=MarketEventType.QUOTE_TICK,
                    symbol=quote.symbol,
                    exchange=quote.exchange,
                    timestamp=quote.timestamp,
                    price=quote.price,
                    volume=quote.volume,
                    change=quote.change,
                    change_pct=quote.change_percent,
                    data_source=quote.data_source,
                    data_status=quote.data_status,
                    payload={"name": quote.name, "currency": quote.currency}
                )
                await event_bus.publish(event)

            except Exception as exc:
                cycle_result.failed_symbols.append(sym)
                logger.warning(f"Failure isolated: Error collecting quote for '{sym}': {exc}")

        cycle_result.quotes = valid_quotes
        cycle_result.records_persisted = len(valid_quotes)
        elapsed_ms = (time.time() - start_t) * 1000.0
        cycle_result.latency_ms = round(elapsed_ms, 2)

        self._last_cycle_result = cycle_result
        self._total_records_processed += len(valid_quotes)
        self._total_cycles_completed += 1

        log_market_data_operation(
            provider="MarketDataCollector",
            operation=f"collect_quotes[{mode.value}]",
            symbol=f"{len(valid_quotes)}/{len(target_symbols)}",
            latency_ms=elapsed_ms,
            success=(len(cycle_result.failed_symbols) < len(target_symbols))
        )
        return cycle_result

    # =========================================================================
    # Benchmark Indices Collection
    # =========================================================================

    async def collect_indices(
        self,
        mode: CollectionMode = CollectionMode.ON_DEMAND
    ) -> CollectorCycleResult:
        """
        Collects real-time benchmark market indices (NIFTY 50, SENSEX, S&P 500, NASDAQ)
        and persists them into Redis and TimescaleDB.
        """
        start_t = time.time()
        target_indices = list(self._monitored_indices)
        cycle_result = CollectorCycleResult(
            mode=mode,
            records_requested=len(target_indices)
        )

        valid_indices: List[MarketIndexQuote] = []

        # Indian Indices
        indian_provider = provider_factory.get_indian_provider()
        try:
            ind_indices = await indian_provider.get_market_indices()
            valid_indices.extend(ind_indices)
            cycle_result.records_received += len(ind_indices)
            cycle_result.records_valid += len(ind_indices)
        except Exception as exc:
            logger.warning(f"Collector failure fetching Indian indices: {exc}")
            cycle_result.failed_symbols.append("INDIAN_INDICES")

        # US Indices
        us_provider = provider_factory.get_us_provider()
        try:
            us_indices = await us_provider.get_market_indices()
            valid_indices.extend(us_indices)
            cycle_result.records_received += len(us_indices)
            cycle_result.records_valid += len(us_indices)
        except Exception as exc:
            logger.warning(f"Collector failure fetching US indices: {exc}")
            cycle_result.failed_symbols.append("US_INDICES")

        # Cache in Redis
        if valid_indices:
            await market_cache.set_indices("ALL", [idx.model_dump() for idx in valid_indices])

            # Persist to TimescaleDB
            try:
                async with async_session_factory() as session:
                    persisted = await market_ingestion_service.ingest_indices(session, valid_indices)
                    await session.commit()
                    cycle_result.records_persisted = persisted
            except Exception as exc:
                logger.warning(f"TimescaleDB index persistence warning: {exc}")

            # Publish Streaming Events
            for idx in valid_indices:
                await event_bus.publish(MarketDataEvent(
                    event_type=MarketEventType.INDEX_TICK,
                    symbol=idx.symbol,
                    exchange=idx.exchange,
                    timestamp=idx.timestamp,
                    price=idx.price,
                    change=idx.change,
                    change_pct=idx.change_pct,
                    data_source=idx.data_source,
                    data_status=idx.data_status,
                    payload={"name": idx.name, "currency": idx.currency}
                ))

        cycle_result.indices = valid_indices
        elapsed_ms = (time.time() - start_t) * 1000.0
        cycle_result.latency_ms = round(elapsed_ms, 2)
        return cycle_result

    # =========================================================================
    # Coordinated Full Ingestion Cycle
    # =========================================================================

    async def collect_all(
        self,
        mode: CollectionMode = CollectionMode.SCHEDULED
    ) -> CollectorCycleResult:
        """Executes coordinated quote and index collection."""
        quote_res = await self.collect_quotes(mode=mode)
        idx_res = await self.collect_indices(mode=mode)

        combined = CollectorCycleResult(
            mode=mode,
            records_requested=quote_res.records_requested + idx_res.records_requested,
            records_received=quote_res.records_received + idx_res.records_received,
            records_valid=quote_res.records_valid + idx_res.records_valid,
            records_rejected=quote_res.records_rejected + idx_res.records_rejected,
            records_persisted=quote_res.records_persisted + idx_res.records_persisted,
            failed_symbols=quote_res.failed_symbols + idx_res.failed_symbols,
            latency_ms=round(quote_res.latency_ms + idx_res.latency_ms, 2),
            quotes=quote_res.quotes,
            indices=idx_res.indices
        )
        self._last_cycle_result = combined
        return combined

    # =========================================================================
    # Collector Status & Telemetry
    # =========================================================================

    def get_collector_status(self) -> Dict[str, Any]:
        """Returns real-time collector operational status."""
        return {
            "status": "RUNNING",
            "monitored_universe": self.get_monitored_universe(),
            "total_cycles_completed": self._total_cycles_completed,
            "total_records_processed": self._total_records_processed,
            "last_cycle": self._last_cycle_result.model_dump() if self._last_cycle_result else None
        }


market_data_collector = MarketDataCollector()
