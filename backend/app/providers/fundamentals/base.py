"""
Fundamentals Provider Base Interface.
"""
from abc import ABC, abstractmethod
from typing import Dict, Any


class FundamentalsProvider(ABC):

    @abstractmethod
    async def get_overview(self, ticker: str) -> Dict[str, Any]:
        pass

    @abstractmethod
    async def get_financial_statements(self, ticker: str, statement_type: str = "income") -> Dict[str, Any]:
        pass
