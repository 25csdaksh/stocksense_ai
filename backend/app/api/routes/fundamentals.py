"""
MarketMind AI — Fundamentals, Valuation & Financial Statement API Routes.
Phase 6.6: Endpoints for company profiles, statements, deterministic ratios,
and data quality telemetry health reporting.
"""
from typing import Optional
from fastapi import APIRouter, Query, HTTPException, status
from app.schemas.fundamentals import (
    FundamentalOverviewResponse,
    FinancialStatementsResponse,
    CompanyProfileResponse,
    FundamentalsHealthResponse,
)
from app.services.fundamentals_service import fundamentals_service
from app.services.fundamentals_collector import fundamentals_collector

router = APIRouter(prefix="/fundamentals", tags=["Company Fundamentals"])


@router.get("/health", response_model=FundamentalsHealthResponse)
async def get_fundamentals_health():
    """Retrieves data quality metrics, provider health status, and ingestion telemetry."""
    return fundamentals_collector.get_health_report()


@router.get("/{symbol}", response_model=FundamentalOverviewResponse)
async def get_fundamental_overview(symbol: str):
    """Retrieves valuation multiples, profitability margins, and financial health scores for a ticker."""
    overview = await fundamentals_service.get_overview(symbol)
    return {
        "ticker": overview.symbol,
        "symbol": overview.symbol,
        "name": overview.name,
        "sector": overview.sector,
        "exchange": overview.exchange,
        "currency": overview.currency,
        "valuation": overview.valuation.model_dump(),
        "profitability": overview.profitability.model_dump(),
        "financial_health": overview.financial_health.model_dump(),
        "liquidity": overview.liquidity.model_dump() if overview.liquidity else None,
        "efficiency": overview.efficiency.model_dump() if overview.efficiency else None,
        "data_source": overview.data_source.value,
        "data_status": overview.data_status.value,
        "updated_at": overview.updated_at,
    }


@router.get("/{symbol}/statements", response_model=FinancialStatementsResponse)
async def get_financial_statements(
    symbol: str,
    statement_type: str = Query(default="income", description="Statement type: income, balance_sheet, cash_flow"),
    period_type: str = Query(default="annual", description="Period granularity: annual, quarterly, ttm")
):
    """Retrieves normalized multi-period financial statements (Income, Balance, Cashflow)."""
    statements = await fundamentals_service.get_statements(
        symbol,
        statement_type=statement_type,
        period_type=period_type
    )
    return {
        "ticker": statements.symbol,
        "symbol": statements.symbol,
        "statement_type": statements.statement_type,
        "period_type": statements.period_type.value,
        "currency": statements.currency,
        "periods": statements.periods,
        "data_source": statements.data_source.value,
        "data_status": statements.data_status.value,
        "updated_at": statements.updated_at,
    }


@router.get("/{symbol}/profile", response_model=CompanyProfileResponse)
async def get_fundamental_profile(symbol: str):
    """Retrieves company legal profile, sector, exchange, and business description."""
    profile = await fundamentals_service.get_company_profile(symbol)
    if not profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Company profile for symbol '{symbol}' not found."
        )
    return {
        "ticker": profile.symbol,
        "symbol": profile.symbol,
        "name": profile.name,
        "legal_name": profile.legal_name,
        "exchange": profile.exchange,
        "isin": profile.isin,
        "sector": profile.sector,
        "industry": profile.industry,
        "country": profile.country,
        "currency": profile.currency,
        "market_cap": profile.market_cap,
        "description": profile.description,
        "website": profile.website,
        "employees": profile.employees,
        "cik": profile.cik,
        "data_source": profile.data_source.value,
        "data_status": profile.data_status.value,
        "updated_at": profile.updated_at,
    }


@router.get("/{symbol}/ratios")
async def get_fundamental_ratios(
    symbol: str,
    market_cap: Optional[float] = Query(None, description="Optional override market capitalization")
):
    """Retrieves comprehensive computed financial ratio suite."""
    ratios = await fundamentals_service.get_ratios(symbol, market_cap=market_cap)
    return ratios.model_dump()
