"""
Market Data & Price History Endpoints.
"""
from typing import List, Optional
from fastapi import APIRouter, Query, HTTPException
from schemas.market_schema import (
    MarketQuoteResponse,
    HistoricalDataResponse,
    MarketOverviewResponse,
    SectorPerformanceResponse,
    AssetResponse
)
from services.market_data_service import market_data_service

router = APIRouter(prefix="/market", tags=["Market Intelligence"])


@router.get("/assets", response_model=List[AssetResponse])
async def get_supported_assets():
    """Returns the list of monitored assets with sector and beta attributes."""
    return market_data_service.get_supported_assets()


@router.get("/overview", response_model=MarketOverviewResponse)
async def get_market_overview():
    """Returns broad market indices, top gainers, top losers, and market regime."""
    return market_data_service.get_market_overview()


@router.get("/sectors", response_model=SectorPerformanceResponse)
async def get_sector_performance():
    """Returns sector performance ranking, momentum scores, and market weights."""
    return market_data_service.get_sector_performance()


@router.get("/quote/{ticker}", response_model=MarketQuoteResponse)
async def get_ticker_quote(ticker: str):
    """Returns real-time or high-fidelity simulated quote snapshot for a ticker."""
    try:
        return market_data_service.get_quote(ticker)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to retrieve quote for {ticker}: {str(e)}")


@router.get("/history/{ticker}", response_model=HistoricalDataResponse)
async def get_historical_bars(
    ticker: str,
    range: str = Query(default="6m", pattern="^(1m|3m|6m|1y|5y)$"),
    interval: str = Query(default="1d", pattern="^(1d|1wk|1mo)$")
):
    """Returns historical OHLCV candlestick series with computed technical indicators (SMA, EMA, RSI, VWAP)."""
    try:
        return market_data_service.get_history(ticker, range_str=range, interval=interval)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch price history for {ticker}: {str(e)}")
