"""
Stock Universe, Real-Time Quotes & Historical OHLCV Routes.
Phase 6.6: Extended with multi-period financials, ratios, and company profile routing.
"""
from typing import List, Dict, Any, Optional
from fastapi import APIRouter, Query
from app.schemas.stock import StockQuoteResponse, HistoricalOHLCVResponse
from app.services.stock_service import stock_service
from app.services.fundamentals_service import fundamentals_service

router = APIRouter(prefix="/stocks", tags=["Stocks & OHLCV Data"])


@router.get("", response_model=List[Dict[str, Any]])
async def get_stock_universe():
    """Retrieves all supported US and Indian assets across sectors in the universe."""
    return await stock_service.get_stock_universe()


@router.get("/{symbol}", response_model=StockQuoteResponse)
async def get_stock_quote(symbol: str):
    """Retrieves real-time quote, market cap, and 52-week boundaries for an Indian (NSE/BSE) or US ticker symbol."""
    return await stock_service.get_quote(symbol)


@router.get("/{symbol}/quote", response_model=StockQuoteResponse)
async def get_stock_quote_alias(symbol: str):
    """Alias for retrieving real-time quote snapshot."""
    return await stock_service.get_quote(symbol)


@router.get("/{symbol}/overview", response_model=StockQuoteResponse)
async def get_stock_overview(symbol: str):
    """Retrieves asset overview quote and key market parameters."""
    return await stock_service.get_quote(symbol)


@router.get("/{symbol}/history", response_model=HistoricalOHLCVResponse)
async def get_stock_history(
    symbol: str,
    timeframe: str = Query(default="6m", description="Historical duration: 1m, 3m, 6m, 1y, 2y, 5y"),
    interval: str = Query(default="1d", description="Bar interval: 1d, 1wk, 1mo")
):
    """Retrieves historical OHLCV candlestick time series with computed technical overlays."""
    return await stock_service.get_history(symbol, timeframe=timeframe, interval=interval)


@router.get("/{symbol}/fundamentals")
async def get_stock_fundamentals(symbol: str):
    """Retrieves fundamental financial valuation metrics (PE, PB, Dividend Yield, Beta, Margins)."""
    return await stock_service.get_fundamentals(symbol)


@router.get("/{symbol}/profile")
async def get_stock_profile(symbol: str):
    """Retrieves company legal profile, sector, exchange, and business description."""
    return await fundamentals_service.get_company_profile(symbol)


@router.get("/{symbol}/financials")
async def get_stock_financials(
    symbol: str,
    statement_type: str = Query(default="income", description="Statement type: income, balance_sheet, cash_flow"),
    period_type: str = Query(default="annual", description="Period granularity: annual, quarterly, ttm")
):
    """Retrieves normalized multi-period financial statements."""
    return await fundamentals_service.get_statements(
        symbol,
        statement_type=statement_type,
        period_type=period_type
    )


@router.get("/{symbol}/ratios")
async def get_stock_ratios(
    symbol: str,
    market_cap: Optional[float] = Query(None, description="Optional override market capitalization")
):
    """Retrieves calculated valuation, profitability, leverage, liquidity, and efficiency ratios."""
    return await fundamentals_service.get_ratios(symbol, market_cap=market_cap)
