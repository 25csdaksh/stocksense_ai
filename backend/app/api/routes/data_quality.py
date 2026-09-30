"""
MarketMind AI — Data Quality API Routes.
Phase 6.8: Global platform data quality summary and per-symbol 3-pillar quality assessments.
"""
from typing import Optional, List, Dict, Any
from fastapi import APIRouter, Query, Path

from app.observability.models import (
    GlobalDataQualityReport,
    SymbolDataQualityReport,
    DataQualityReport,
    OperationalFailureRecord,
)
from app.observability.quality_coordinator import quality_coordinator
from app.observability.failure_log import failure_logger
from app.utils.validators import validate_ticker

router = APIRouter(prefix="/data-quality", tags=["Data Quality & Observability"])


@router.get("", response_model=GlobalDataQualityReport)
async def get_global_data_quality(
    market: Optional[str] = Query(None, description="Filter by market region (e.g. INDIA, US)"),
    provider: Optional[str] = Query(None, description="Filter by provider name"),
    dataset: Optional[str] = Query(None, description="Filter by dataset (market_data, fundamentals, news)"),
    status: Optional[str] = Query(None, description="Filter by health status")
) -> GlobalDataQualityReport:
    """Returns top-level data quality scores, market averages, dataset ratings, and recent failure logs."""
    return await quality_coordinator.get_global_quality_report(
        market=market,
        provider=provider,
        dataset=dataset,
        status=status
    )


@router.get("/failures", response_model=List[OperationalFailureRecord])
async def get_recent_failures(
    limit: int = Query(50, ge=1, le=200, description="Max failure records to return"),
    component: Optional[str] = Query(None, description="Filter by component name"),
    symbol: Optional[str] = Query(None, description="Filter by symbol")
) -> List[OperationalFailureRecord]:
    """Returns sanitized recent operational failure and SLA breach records."""
    return failure_logger.get_recent_failures(limit=limit, component=component, symbol=symbol)


@router.get("/{symbol}", response_model=SymbolDataQualityReport)
async def get_symbol_data_quality(
    symbol: str = Path(..., description="Stock ticker symbol (e.g. RELIANCE.NS, AAPL, TCS.NS)")
) -> SymbolDataQualityReport:
    """Returns deterministic 3-pillar data quality report (Market Data, Fundamentals, News) for a symbol."""
    sym = validate_ticker(symbol)
    return await quality_coordinator.assess_symbol_quality(sym)
