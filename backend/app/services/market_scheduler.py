"""
MarketMind AI — Production Market Data Ingestion Scheduler.
Phase 6.3: Pure asyncio background ingestion loop with market-session awareness (NSE/BSE & US trading hours),
quote refresh cycles, index polling, and incremental backfill scheduling.
"""
import asyncio
import time
from typing import Dict, Any, Optional
from datetime import datetime, timezone

from app.core.logging import logger
from app.services.market_data_collector import market_data_collector, CollectionMode
from app.services.market_backfill_service import market_backfill_service
from app.providers.market_data.session import market_session_manager


class MarketDataScheduler:
    """
    Lightweight, resilient async scheduler managing background market data ingestion cycles.
    """

    def __init__(
        self,
        quote_interval_seconds: float = 10.0,
        index_interval_seconds: float = 15.0,
        backfill_interval_seconds: float = 1800.0
    ):
        self.quote_interval = quote_interval_seconds
        self.index_interval = index_interval_seconds
        self.backfill_interval = backfill_interval_seconds
        self._task: Optional[asyncio.Task] = None
        self._is_running: bool = False
        self._started_at: Optional[str] = None
        self._last_quote_run: Optional[str] = None
        self._last_index_run: Optional[str] = None
        self._last_backfill_run: Optional[str] = None
        self._cycle_counter: int = 0
        self._error_counter: int = 0
        self._last_error: Optional[str] = None

    @property
    def is_running(self) -> bool:
        return self._is_running and self._task is not None and not self._task.done()

    async def start(self) -> bool:
        """Starts the background scheduler loop. Returns True if started, False if already running."""
        if self.is_running:
            logger.warning("MarketDataScheduler is already running.")
            return False

        self._is_running = True
        self._started_at = datetime.now(timezone.utc).isoformat()
        self._task = asyncio.create_task(self._scheduler_loop(), name="marketmind_data_scheduler")
        logger.info(
            f"MarketDataScheduler started (quotes={self.quote_interval}s, "
            f"indices={self.index_interval}s, backfill={self.backfill_interval}s)."
        )
        return True

    async def stop(self) -> bool:
        """Gracefully stops the background scheduler loop."""
        if not self._is_running:
            return False

        self._is_running = False
        if self._task and not self._task.done():
            self._task.cancel()
            try:
                await self._task
            except asyncio.CancelledError:
                pass
        self._task = None
        logger.info("MarketDataScheduler stopped gracefully.")
        return True

    async def _scheduler_loop(self) -> None:
        """Core asynchronous background loop with session awareness."""
        last_index_time = 0.0
        last_backfill_time = 0.0

        while self._is_running:
            try:
                now = time.time()
                # 1. Check Session State (NSE & US)
                nse_stat = market_session_manager.get_session_status("NSE")
                us_stat = market_session_manager.get_session_status("US")
                any_market_open = nse_stat.is_open or us_stat.is_open

                # 2. Quote Collection Cycle
                if any_market_open:
                    await market_data_collector.collect_quotes(mode=CollectionMode.SCHEDULED)
                    self._last_quote_run = datetime.now(timezone.utc).isoformat()
                else:
                    # In market closure, poll less aggressively or sleep
                    logger.debug("Market sessions closed; skipping high-frequency quote poll.")

                # 3. Index Collection Cycle
                if now - last_index_time >= self.index_interval:
                    await market_data_collector.collect_indices(mode=CollectionMode.SCHEDULED)
                    self._last_index_run = datetime.now(timezone.utc).isoformat()
                    last_index_time = now

                # 4. Periodic Incremental Backfill Cycle
                if now - last_backfill_time >= self.backfill_interval:
                    # Run incremental backfill in background without blocking quote loop
                    asyncio.create_task(
                        market_backfill_service.backfill_universe_history(timeframe="3m", interval="1d"),
                        name="periodic_incremental_backfill"
                    )
                    self._last_backfill_run = datetime.now(timezone.utc).isoformat()
                    last_backfill_time = now

                self._cycle_counter += 1
                self._last_error = None

            except asyncio.CancelledError:
                break
            except Exception as exc:
                self._error_counter += 1
                self._last_error = str(exc)
                logger.warning(f"MarketDataScheduler cycle error: {exc}")

            # Sleep until next quote interval
            try:
                await asyncio.sleep(self.quote_interval)
            except asyncio.CancelledError:
                break

    def get_scheduler_status(self) -> Dict[str, Any]:
        """Returns structured telemetry on scheduler status, uptime, and cycles."""
        return {
            "is_running": self.is_running,
            "started_at": self._started_at,
            "quote_interval_seconds": self.quote_interval,
            "index_interval_seconds": self.index_interval,
            "backfill_interval_seconds": self.backfill_interval,
            "total_cycles_completed": self._cycle_counter,
            "total_errors": self._error_counter,
            "last_quote_run": self._last_quote_run,
            "last_index_run": self._last_index_run,
            "last_backfill_run": self._last_backfill_run,
            "last_error": self._last_error
        }


market_scheduler = MarketDataScheduler()
