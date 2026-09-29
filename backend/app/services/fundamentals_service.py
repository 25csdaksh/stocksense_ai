"""
Company Fundamentals & Normalized Statements Service.
"""
from typing import Dict, Any
from app.providers.fundamentals.factory import get_fundamentals_provider
from app.utils.validators import validate_ticker


class FundamentalsService:

    def __init__(self):
        self.provider = get_fundamentals_provider()

    async def get_overview(self, ticker: str) -> Dict[str, Any]:
        sym = validate_ticker(ticker)
        return await self.provider.get_overview(sym)

    async def get_statements(self, ticker: str, statement_type: str = "income") -> Dict[str, Any]:
        sym = validate_ticker(ticker)
        return await self.provider.get_financial_statements(sym, statement_type=statement_type)


fundamentals_service = FundamentalsService()
