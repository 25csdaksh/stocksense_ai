"""
Company Fundamentals, Valuation Multiples & Financial Statements API Routes.
"""
from fastapi import APIRouter, Query
from app.schemas.fundamentals import FundamentalOverviewResponse, FinancialStatementsResponse
from app.services.fundamentals_service import fundamentals_service

router = APIRouter(prefix="/fundamentals", tags=["Company Fundamentals"])


@router.get("/{symbol}", response_model=FundamentalOverviewResponse)
async def get_fundamental_overview(symbol: str):
    """Retrieves valuation multiples, profitability margins, and financial health scores for a ticker."""
    return await fundamentals_service.get_overview(symbol)


@router.get("/{symbol}/statements", response_model=FinancialStatementsResponse)
async def get_financial_statements(
    symbol: str,
    statement_type: str = Query(default="income", description="Statement type: income, balance_sheet, cash_flow")
):
    """Retrieves normalized multi-period financial statements."""
    return await fundamentals_service.get_statements(symbol, statement_type=statement_type)
