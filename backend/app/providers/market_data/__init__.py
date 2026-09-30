"""
MarketMind AI — Market Data Provider Architecture Module.
Phase 6.1: Live market data abstraction supporting Indian (NSE/BSE) and US markets, session telemetry, rate limiting, and caching.
"""
from app.providers.market_data.models import (
    DataStatus,
    ProviderStatus,
    MarketSessionState,
    MarketType,
    NormalizedQuote,
    HistoricalCandle,
    HistoricalDataResponse,
    MarketIndexQuote,
    CompanyFundamentals,
    CompanyProfile,
    MarketNewsItem,
    MarketSessionStatus,
    ProviderHealth
)
from app.providers.market_data.exceptions import (
    MarketDataException,
    ProviderNotConfigured,
    ProviderUnavailable,
    ProviderAuthenticationFailed,
    SymbolNotFound,
    RateLimitExceeded,
    MarketDataTimeout,
    InvalidSymbol,
    DataValidationError
)
from app.providers.market_data.base import MarketDataProvider, BaseMarketDataProvider
from app.providers.market_data.symbol_normalizer import (
    SymbolNormalizer,
    NormalizedSymbolInfo,
    normalize_symbol,
    is_indian_symbol,
    is_us_symbol
)
from app.providers.market_data.session import MarketSessionManager, market_session_manager
from app.providers.market_data.validator import MarketDataValidator, validator
from app.providers.market_data.rate_limiter import ProviderRateLimiter
from app.providers.market_data.retry import execute_with_retry
from app.providers.market_data.observability import log_market_data_operation, sanitize_sensitive_data
from app.providers.market_data.indian_market_provider import IndianMarketDataProvider, indian_market_provider
from app.providers.market_data.us_market_provider import USMarketProvider, us_market_provider
from app.providers.market_data.demo_provider import DemoMarketProvider, demo_market_provider
from app.providers.market_data.zerodha_provider import ZerodhaMarketProvider, zerodha_market_provider
from app.providers.market_data.broker_stubs import (
    UpstoxMarketProvider,
    AngelOneMarketProvider
)
from app.providers.market_data.factory import (
    MarketDataProviderFactory,
    provider_factory,
    get_market_data_provider
)

__all__ = [
    # Models & Enums
    "DataStatus",
    "ProviderStatus",
    "MarketSessionState",
    "MarketType",
    "NormalizedQuote",
    "HistoricalCandle",
    "HistoricalDataResponse",
    "MarketIndexQuote",
    "CompanyFundamentals",
    "CompanyProfile",
    "MarketNewsItem",
    "MarketSessionStatus",
    "ProviderHealth",
    # Exceptions
    "MarketDataException",
    "ProviderNotConfigured",
    "ProviderUnavailable",
    "ProviderAuthenticationFailed",
    "SymbolNotFound",
    "RateLimitExceeded",
    "MarketDataTimeout",
    "InvalidSymbol",
    "DataValidationError",
    # Base
    "MarketDataProvider",
    "BaseMarketDataProvider",
    # Normalizer
    "SymbolNormalizer",
    "NormalizedSymbolInfo",
    "normalize_symbol",
    "is_indian_symbol",
    "is_us_symbol",
    # Session
    "MarketSessionManager",
    "market_session_manager",
    # Validator
    "MarketDataValidator",
    "validator",
    # Rate Limiter & Retry
    "ProviderRateLimiter",
    "execute_with_retry",
    # Observability
    "log_market_data_operation",
    "sanitize_sensitive_data",
    # Concrete Providers
    "IndianMarketDataProvider",
    "indian_market_provider",
    "USMarketProvider",
    "us_market_provider",
    "DemoMarketProvider",
    "demo_market_provider",
    "ZerodhaMarketProvider",
    "zerodha_market_provider",
    "UpstoxMarketProvider",
    "AngelOneMarketProvider",
    # Factory
    "MarketDataProviderFactory",
    "provider_factory",
    "get_market_data_provider",
]
