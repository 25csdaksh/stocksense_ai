"""
Macro Market Intelligence & Sector Performance API Routes.
Phase 6.1: Multi-market support (NSE, BSE, US), session status telemetry, and provider health.
"""
from typing import List, Dict, Any, Optional
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
