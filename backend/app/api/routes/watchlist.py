"""
Watchlist Management API Routes with Database Persistence.
"""
from typing import List, Dict, Any, Optional
from fastapi import APIRouter, Body, HTTPException, status, Depends
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from app.services.portfolio_service import portfolio_service
from app.db.session import get_db_session

router = APIRouter(prefix="/watchlist", tags=["Watchlist"])


class WatchlistAddRequest(BaseModel):
    ticker: str
    target_price: Optional[float] = None
    notes: Optional[str] = None


@router.get("", response_model=List[Dict[str, Any]])
async def get_watchlist(db: AsyncSession = Depends(get_db_session)):
    """Retrieves all assets on the user watchlist enriched with live price and change percentages."""
    return await portfolio_service.get_watchlist(db=db)


@router.post("", status_code=status.HTTP_201_CREATED)
async def add_to_watchlist(
    req: WatchlistAddRequest,
    db: AsyncSession = Depends(get_db_session)
):
    """Adds a ticker symbol to the user watchlist."""
    return await portfolio_service.add_to_watchlist(
        ticker=req.ticker,
        target_price=req.target_price,
        notes=req.notes,
        db=db
    )


@router.delete("/{symbol}")
async def remove_from_watchlist(
    symbol: str,
    db: AsyncSession = Depends(get_db_session)
):
    """Removes a ticker symbol from the user watchlist."""
    removed = await portfolio_service.remove_from_watchlist(symbol, db=db)
    if not removed:
        raise HTTPException(status_code=404, detail=f"Ticker '{symbol}' not found in watchlist.")
    return {"status": "SUCCESS", "message": f"Ticker '{symbol.upper()}' removed from watchlist."}
