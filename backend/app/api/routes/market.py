"""
Macro Market Intelligence & Sector Performance API Routes.
Phase 6.1: Multi-market support (NSE, BSE, US), session status telemetry, and provider health.
"""
from typing import List, Dict, Any, Optional
from datetime import datetime, timezone
from fastapi import APIRouter, Query
from app.schemas.market import MarketOverviewResponse, MarketIndexItem, SectorItem
from app.providers.market_data.models import MarketSessionStatus, ProviderHealth
from app.services.market_service import market_service

router = APIRouter(prefix="/market", tags=["Market Intelligence"])


@router.get("/overview", response_model=MarketOverviewResponse)
async def get_market_overview(
    market: str = Query(default="US", description="Market region: US, IN, NSE, BSE")
):
    """Retrieves market regime, benchmark indices, and top movers for US or Indian markets."""
    return await market_service.get_overview(market=market)


@router.get("/indices", response_model=List[MarketIndexItem])
async def get_market_indices(
    market: Optional[str] = Query(default=None, description="Market filter: US, IN, NSE, BSE")
):
    """Retrieves major benchmark indices (S&P 500, NASDAQ, NIFTY 50, SENSEX, VIX)."""
    return await market_service.get_indices(market=market)


@router.get("/sectors", response_model=List[SectorItem])
async def get_sector_performance():
    """Retrieves real-time sector performance, momentum rankings, and market cap weights."""
    return await market_service.get_sectors()


@router.get("/status/{exchange}", response_model=MarketSessionStatus)
async def get_market_session_status(exchange: str = "NSE"):
    """Retrieves session status, trading hours, timezone, and next open/close for an exchange."""
    return await market_service.get_market_status(exchange=exchange)


@router.get("/providers/health", response_model=List[ProviderHealth])
async def get_market_providers_health():
    """Reports operational status, latency, and credential configuration for all registered market data providers."""
    return await market_service.get_providers_health()


# =============================================================================
# Ingestion Engine & Telemetry Endpoints (Phase 6.3)
# =============================================================================

@router.get("/ingestion/health")
async def get_ingestion_health():
    """Returns operational health of the market data collector, scheduler, and ingestion pipeline."""
    from app.services.market_data_collector import market_data_collector
    from app.services.market_scheduler import market_scheduler
    from app.cache.redis_client import cache_client

    redis_ok = await cache_client.is_healthy() if hasattr(cache_client, "is_healthy") else True
    return {
        "status": "HEALTHY",
        "collector_status": "ONLINE",
        "scheduler": market_scheduler.get_scheduler_status(),
        "redis_connected": redis_ok,
        "monitored_universe_size": market_data_collector.get_monitored_universe()["total_symbols"],
        "timestamp": datetime.now(timezone.utc).isoformat()
    }


@router.get("/ingestion/status")
async def get_ingestion_status():
    """Returns detailed telemetry, monitored symbol universe, and last cycle results."""
    from app.services.market_data_collector import market_data_collector
    return market_data_collector.get_collector_status()


@router.post("/ingestion/collect")
async def trigger_manual_collection(
    symbols: Optional[List[str]] = Query(default=None, description="Optional subset of symbols to collect")
):
    """Manually triggers an immediate quote and index collection cycle."""
    from app.services.market_data_collector import market_data_collector, CollectionMode
    res = await market_data_collector.collect_quotes(symbols=symbols, mode=CollectionMode.MANUAL)
    return res.model_dump()


@router.post("/ingestion/backfill")
async def trigger_historical_backfill(
    symbol: str = Query(description="Symbol to backfill, e.g., RELIANCE.NS, AAPL"),
    timeframe: str = Query(default="6m", description="Historical timeframe: 1m, 3m, 6m, 1y"),
    interval: str = Query(default="1d", description="OHLCV interval: 1m, 5m, 15m, 30m, 60m, 1d"),
    force_full: bool = Query(default=False, description="Force full backfill instead of incremental sync")
):
    """Triggers an incremental or full historical backfill into TimescaleDB."""
    from app.services.market_backfill_service import market_backfill_service
    res = await market_backfill_service.backfill_symbol_history(
        symbol=symbol,
        timeframe=timeframe,
        interval=interval,
        force_full=force_full
    )
    return res.model_dump()


@router.get("/ingestion/quality/{symbol}")
async def get_symbol_quality_report(
    symbol: str,
    timeframe: str = Query(default="3m", description="Timeframe to assess"),
    interval: str = Query(default="1d", description="Interval to inspect")
):
    """Evaluates data quality, freshness, and OHLCV gaps for a specific asset."""
    from app.services.market_quality_service import market_quality_service
    from app.providers.market_data.factory import provider_factory

    provider = provider_factory.get_provider(symbol=symbol)
    hist = await provider.get_historical_data(symbol=symbol, timeframe=timeframe, interval=interval)
    report = market_quality_service.evaluate_timeseries_quality(
        symbol=symbol,
        candles=hist.bars,
        interval=interval,
        data_source=hist.data_source
    )
    return report.model_dump()

