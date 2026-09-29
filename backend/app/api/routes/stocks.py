"""
Stock Universe, Real-Time Quotes & Historical OHLCV Routes.
"""
from typing import List, Dict, Any
from fastapi import APIRouter, Query
from app.schemas.stock import StockQuoteResponse, HistoricalOHLCVResponse
from app.services.stock_service import stock_service

router = APIRouter(prefix="/stocks", tags=["Stocks & OHLCV Data"])


@router.get("", response_model=List[Dict[str, Any]])
async def get_stock_universe():
    """Retrieves all supported assets across sectors in the universe."""
    return await stock_service.get_stock_universe()


@router.get("/{symbol}", response_model=StockQuoteResponse)
async def get_stock_quote(symbol: str):
    """Retrieves real-time quote, market cap, and 52-week boundaries for a ticker symbol."""
    return await stock_service.get_quote(symbol)


@router.get("/{symbol}/history", response_model=HistoricalOHLCVResponse)
async def get_stock_history(
    symbol: str,
    timeframe: str = Query(default="6m", description="Historical duration: 1m, 3m, 6m, 1y, 2y, 5y"),
    interval: str = Query(default="1d", description="Bar interval: 1d, 1wk, 1mo")
):
    """Retrieves historical OHLCV candlestick time series."""
    return await stock_service.get_history(symbol, timeframe=timeframe, interval=interval)
