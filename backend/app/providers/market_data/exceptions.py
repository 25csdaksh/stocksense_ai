"""
MarketMind AI — Market Data Domain Exceptions.
Controlled error types preventing raw external exceptions from leaking to API clients.
"""
from typing import Optional, Dict, Any
from fastapi import status
from app.core.exceptions import MarketMindException


class MarketDataException(MarketMindException):
    """Base domain exception for all market data provider operations."""
    def __init__(
        self,
        message: str,
        status_code: int = status.HTTP_500_INTERNAL_SERVER_ERROR,
        details: Optional[Dict[str, Any]] = None
    ):
        super().__init__(message=message, status_code=status_code, details=details)


class ProviderNotConfigured(MarketDataException):
    """Raised when a requested provider lacks valid credentials or environment setup."""
    def __init__(self, provider_name: str, missing_keys: Optional[list] = None):
        msg = f"Market data provider '{provider_name}' is not configured or lacks required API credentials."
        super().__init__(
            message=msg,
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            details={
                "provider": provider_name,
                "missing_keys": missing_keys or [],
                "status": "CONFIGURATION_REQUIRED",
                "resolution": f"Provide required environment credentials in .env for {provider_name}."
            }
        )


class ProviderUnavailable(MarketDataException):
    """Raised when a market data provider is unreachable or experiencing upstream outages."""
    def __init__(self, provider_name: str, reason: str = "Upstream connection failed"):
        super().__init__(
            message=f"Market data provider '{provider_name}' is currently unavailable: {reason}",
            status_code=status.HTTP_502_BAD_GATEWAY,
            details={"provider": provider_name, "reason": reason}
        )


class SymbolNotFound(MarketDataException):
    """Raised when a symbol does not exist on the specified exchange."""
    def __init__(self, symbol: str, exchange: Optional[str] = None):
        exch_str = f" on {exchange}" if exchange else ""
        super().__init__(
            message=f"Financial asset '{symbol}' not found{exch_str}.",
            status_code=status.HTTP_404_NOT_FOUND,
            details={"symbol": symbol, "exchange": exchange}
        )


class InvalidSymbol(MarketDataException):
    """Raised when a symbol string fails syntactic or format validation."""
    def __init__(self, symbol: str, reason: str = "Malformed ticker format"):
        super().__init__(
            message=f"Invalid symbol '{symbol}': {reason}",
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            details={"symbol": symbol, "reason": reason}
        )


class RateLimitExceeded(MarketDataException):
    """Raised when provider rate limits are exceeded."""
    def __init__(self, provider_name: str, retry_after_seconds: Optional[int] = None):
        super().__init__(
            message=f"Rate limit exceeded for provider '{provider_name}'. Please retry later.",
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            details={
                "provider": provider_name,
                "retry_after_seconds": retry_after_seconds or 60
            }
        )


class MarketDataTimeout(MarketDataException):
    """Raised when a market data query exceeds maximum latency SLA."""
    def __init__(self, provider_name: str, symbol: Optional[str] = None, timeout_seconds: float = 5.0):
        sym_str = f" for '{symbol}'" if symbol else ""
        super().__init__(
            message=f"Market data request to '{provider_name}'{sym_str} timed out after {timeout_seconds}s.",
            status_code=status.HTTP_504_GATEWAY_TIMEOUT,
            details={"provider": provider_name, "symbol": symbol, "timeout_seconds": timeout_seconds}
        )


class DataValidationError(MarketDataException):
    """Raised when incoming market feed fails financial sanity checks (e.g. invalid OHLC boundaries)."""
    def __init__(self, message: str, record: Optional[Dict[str, Any]] = None):
        super().__init__(
            message=f"Market data financial validation failed: {message}",
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            details={"validation_error": message, "record": record or {}}
        )


class ProviderAuthenticationFailed(MarketDataException):
    """Raised when broker credentials (API key, access token) are invalid, expired, or rejected."""
    def __init__(self, provider_name: str, reason: str = "Invalid or expired access token"):
        super().__init__(
            message=f"Authentication failed for provider '{provider_name}': {reason}",
            status_code=status.HTTP_401_UNAUTHORIZED,
            details={
                "provider": provider_name,
                "status": "AUTHENTICATION_ERROR",
                "reason": reason
            }
        )

