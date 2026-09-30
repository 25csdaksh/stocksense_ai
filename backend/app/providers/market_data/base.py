"""
MarketMind AI — Live Market Data Provider Interface (Abstract Base Class).
Phase 6.1: Decoupled, production-ready contract defining all standard market data capabilities.
"""
from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional
from datetime import datetime
from app.providers.market_data.models import (
    NormalizedQuote,
    HistoricalDataResponse,
    MarketIndexQuote,
    CompanyFundamentals,
    CompanyProfile,
    MarketNewsItem,
    MarketSessionStatus,
    ProviderHealth
)


class MarketDataProvider(ABC):
    """
    Abstract Base Class for all concrete Market Data Providers (Indian, US, Demo, Broker Stubs).
    """

    @abstractmethod
    async def get_quote(self, symbol: str) -> NormalizedQuote:
        """Fetches latest real-time/normalized quote snapshot for a symbol."""
        pass

    @abstractmethod
    async def get_quotes(self, symbols: List[str]) -> List[NormalizedQuote]:
        """Batch fetches normalized quote snapshots for multiple symbols."""
        pass

    @abstractmethod
    async def get_historical_data(
        self,
        symbol: str,
        start: Optional[datetime] = None,
        end: Optional[datetime] = None,
        interval: str = "1d",
        timeframe: Optional[str] = "6m"
    ) -> HistoricalDataResponse:
        """Fetches standardized historical OHLCV candlestick bars with indicators."""
        pass

    @abstractmethod
    async def get_fundamentals(self, symbol: str) -> CompanyFundamentals:
        """Fetches fundamental valuation metrics (PE, PB, Market Cap, Beta, Div Yield)."""
        pass

    @abstractmethod
    async def get_company_profile(self, symbol: str) -> CompanyProfile:
        """Fetches company legal name, sector, exchange, and business description."""
        pass

    @abstractmethod
    async def get_market_indices(self) -> List[MarketIndexQuote]:
        """Fetches benchmark indices for the provider's active market."""
        pass

    @abstractmethod
    async def get_news(self, symbol: Optional[str] = None, limit: int = 10) -> List[MarketNewsItem]:
        """Fetches real-time financial headlines for a specific symbol or the broad market."""
        pass

    @abstractmethod
    async def get_market_status(self) -> MarketSessionStatus:
        """Fetches current exchange session state, timezone, next open/close."""
        pass

    @abstractmethod
    async def get_health(self) -> ProviderHealth:
        """Reports provider operational status, latency, and credentials configuration."""
        pass

    # =========================================================================
    # Backward Compatibility Adapter Methods for Phase 1-5 Services
    # =========================================================================
    async def get_history(self, ticker: str, timeframe: str = "6m", interval: str = "1d") -> Dict[str, Any]:
        """Legacy compatibility wrapper returning dictionary structure matching Phase 1-5."""
        hist = await self.get_historical_data(symbol=ticker, timeframe=timeframe, interval=interval)
        return {
            "ticker": hist.ticker,
            "timeframe": hist.timeframe,
            "interval": hist.interval,
            "currency": hist.currency,
            "bars": [b.model_dump() for b in hist.bars],
            "is_synthetic": hist.is_synthetic,
            "total_bars": hist.total_bars,
            "data_source": hist.data_source,
            "data_status": hist.data_status.value
        }

    async def get_indices(self) -> List[Dict[str, Any]]:
        """Legacy compatibility wrapper returning dictionary structure for indices."""
        indices = await self.get_market_indices()
        return [
            {
                "symbol": idx.symbol,
                "name": idx.name,
                "exchange": idx.exchange,
                "price": idx.price,
                "change": idx.change,
                "change_pct": idx.change_pct,
                "currency": idx.currency
            }
            for idx in indices
        ]


BaseMarketDataProvider = MarketDataProvider
