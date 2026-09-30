"""
MarketMind AI — Centralized Bounded Retry Policy for Market Data Providers.
Retries only transient network drops, timeouts, and temporary upstream 502/503/504 errors.
Refuses to retry non-transient validation errors, authentication failures, or invalid symbols.
"""
import asyncio
import random
from typing import Callable, Any, TypeVar, Tuple
from app.providers.market_data.exceptions import (
    MarketDataTimeout,
    ProviderUnavailable,
    InvalidSymbol,
    SymbolNotFound,
    ProviderNotConfigured,
    DataValidationError,
    RateLimitExceeded
)
from app.core.logging import logger

T = TypeVar("T")

# Errors that should NEVER be retried
NON_RETRYABLE_EXCEPTIONS: Tuple[type, ...] = (
    InvalidSymbol,
    SymbolNotFound,
    ProviderNotConfigured,
    DataValidationError,
    RateLimitExceeded,
    ValueError,
    TypeError
)

# Transient errors that qualify for bounded exponential retry
RETRYABLE_EXCEPTIONS: Tuple[type, ...] = (
    MarketDataTimeout,
    ProviderUnavailable,
    asyncio.TimeoutError,
    ConnectionError,
    TimeoutError
)


async def execute_with_retry(
    func: Callable[..., Any],
    *args: Any,
    max_retries: int = 2,
    base_delay: float = 0.1,
    max_delay: float = 1.0,
    provider_name: str = "MarketDataProvider",
    **kwargs: Any
) -> Any:
    """
    Executes an async provider call with bounded exponential backoff & jitter for transient errors.
    """
    attempt = 0
    while True:
        try:
            return await func(*args, **kwargs)
        except NON_RETRYABLE_EXCEPTIONS as exc:
            # Immediate fail without retrying non-transient errors
            logger.debug(f"Non-retryable exception ({type(exc).__name__}) on attempt {attempt+1} for {provider_name}")
            raise
        except Exception as exc:
            attempt += 1
            if attempt > max_retries:
                logger.warning(f"Exhausted {max_retries} retries for {provider_name}. Last error: {exc}")
                raise

            delay = min(max_delay, base_delay * (2 ** (attempt - 1)))
            jitter = random.uniform(0, 0.1 * delay)
            total_sleep = delay + jitter

            logger.info(
                f"Transient error ({type(exc).__name__}) calling {provider_name}. "
                f"Retrying attempt {attempt}/{max_retries} in {total_sleep:.2f}s..."
            )
            await asyncio.sleep(total_sleep)
