"""
Unit Tests for MarketDataScheduler (Phase 6.3).
Validates:
- Lifecycle management (startup, shutdown, idempotent start)
- Market session awareness
- Scheduler status telemetry
"""
import pytest
import asyncio
from unittest.mock import AsyncMock, patch

from app.services.market_scheduler import MarketDataScheduler
from app.providers.market_data.models import MarketSessionStatus, MarketSessionState


@pytest.mark.asyncio
async def test_scheduler_lifecycle():
    scheduler = MarketDataScheduler(quote_interval_seconds=0.05, index_interval_seconds=0.05)
    assert scheduler.is_running is False

    # Start
    started = await scheduler.start()
    assert started is True
    assert scheduler.is_running is True

    # Duplicate start attempt should be rejected
    duplicate_start = await scheduler.start()
    assert duplicate_start is False

    # Allow one loop iteration
    await asyncio.sleep(0.1)

    # Stop
    stopped = await scheduler.stop()
    assert stopped is True
    assert scheduler.is_running is False


def test_scheduler_status_telemetry():
    scheduler = MarketDataScheduler(quote_interval_seconds=10.0, index_interval_seconds=15.0)
    status = scheduler.get_scheduler_status()

    assert "is_running" in status
    assert "quote_interval_seconds" in status
    assert "total_cycles_completed" in status
    assert status["quote_interval_seconds"] == 10.0
    assert status["index_interval_seconds"] == 15.0


@pytest.mark.asyncio
async def test_scheduler_session_awareness_closed_market():
    scheduler = MarketDataScheduler(quote_interval_seconds=0.05)

    closed_session = MarketSessionStatus(
        market="IN",
        exchange="NSE",
        is_open=False,
        session_state=MarketSessionState.CLOSED,
        session_start="09:15",
        session_end="15:30",
        timezone="Asia/Kolkata",
        current_time_local="2026-09-30 22:00:00",
        next_open="2026-10-01T03:45:00Z",
        next_close="2026-10-01T10:00:00Z"
    )

    with patch("app.providers.market_data.session.market_session_manager.get_session_status", return_value=closed_session), \
         patch("app.services.market_data_collector.market_data_collector.collect_quotes", new_callable=AsyncMock) as mock_collect:

        await scheduler.start()
        await asyncio.sleep(0.1)
        await scheduler.stop()

        # In closed session, quote polling must be skipped
        mock_collect.assert_not_called()
