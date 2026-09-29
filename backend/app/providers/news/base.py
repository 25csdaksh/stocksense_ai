"""
Financial News Provider Interface.
"""
from abc import ABC, abstractmethod
from typing import Dict, Any, List


class NewsProvider(ABC):

    @abstractmethod
    async def get_news_for_ticker(self, ticker: str, limit: int = 5) -> List[Dict[str, Any]]:
        pass

    @abstractmethod
    async def get_market_news(self, limit: int = 10) -> List[Dict[str, Any]]:
        pass
