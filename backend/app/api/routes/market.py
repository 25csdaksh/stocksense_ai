"""
Macro Market Intelligence & Sector Performance API Routes.
"""
from typing import List, Dict, Any
from fastapi import APIRouter
from app.schemas.market import MarketOverviewResponse, MarketIndexItem, SectorItem
from app.services.market_service import market_service

router = APIRouter(prefix="/market", tags=["Market Intelligence"])


@router.get("/overview", response_model=MarketOverviewResponse)
async def get_market_overview():
    """Retrieves global market regime, benchmark indices, and top movers."""
    return await market_service.get_overview()


@router.get("/indices", response_model=List[MarketIndexItem])
async def get_market_indices():
    """Retrieves major benchmark indices (S&P 500, Nasdaq 100, Dow Jones, Russell 2000, VIX)."""
    return await market_service.get_indices()


@router.get("/sectors", response_model=List[SectorItem])
async def get_sector_performance():
    """Retrieves real-time sector performance, momentum rankings, and market cap weights."""
    return await market_service.get_sectors()
