"""
Market Data Provider Interface (Abstract Base Class).
"""
from abc import ABC, abstractmethod
from typing import Dict, Any, List


class MarketDataProvider(ABC):

    @abstractmethod
    async def get_quote(self, ticker: str) -> Dict[str, Any]:
        """Fetches latest quote snapshot."""
        pass

    @abstractmethod
    async def get_history(self, ticker: str, timeframe: str = "6m", interval: str = "1d") -> Dict[str, Any]:
        """Fetches historical OHLCV bars with technical indicators."""
        pass

    @abstractmethod
    async def get_indices(self) -> List[Dict[str, Any]]:
        """Fetches major index benchmarks."""
        pass
