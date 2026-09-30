"""
Unit Tests for Rate Limiter and Bounded Retry Policy.
Phase 6.1: Verifies rate quota awareness, transient exception retry with backoff, and non-retryable exception behavior.
"""
import pytest
import asyncio
from app.providers.market_data.rate_limiter import ProviderRateLimiter
from app.providers.market_data.retry import execute_with_retry
from app.providers.market_data.exceptions import (
    RateLimitExceeded,
    InvalidSymbol,
    MarketDataTimeout,
    ProviderUnavailable,
    ProviderNotConfigured
)


def test_rate_limiter_quota_and_throttling():
    limiter = ProviderRateLimiter(provider_name="TestProvider", max_requests_per_minute=3)
    assert limiter.requests_remaining == 3
    assert limiter.rate_limit_status == "NORMAL"

    limiter.record_request()
    limiter.record_request()
    assert limiter.requests_remaining == 1

    limiter.record_request()
    assert limiter.requests_remaining == 0
    assert limiter.rate_limit_status == "THROTTLED"

    with pytest.raises(RateLimitExceeded):
        limiter.check_rate_limit()


@pytest.mark.asyncio
async def test_retry_on_transient_failure():
    call_count = 0

    async def flaky_operation():
        nonlocal call_count
        call_count += 1
        if call_count < 2:
            raise MarketDataTimeout("TestProvider", "AAPL", 1.0)
        return "SUCCESS"

    result = await execute_with_retry(flaky_operation, max_retries=2, base_delay=0.01)
    assert result == "SUCCESS"
    assert call_count == 2


@pytest.mark.asyncio
async def test_no_retry_on_invalid_symbol():
    call_count = 0

    async def bad_symbol_operation():
        nonlocal call_count
        call_count += 1
        raise InvalidSymbol("BAD$$$")

    with pytest.raises(InvalidSymbol):
        await execute_with_retry(bad_symbol_operation, max_retries=3, base_delay=0.01)

    assert call_count == 1  # Fails immediately without retrying


@pytest.mark.asyncio
async def test_no_retry_on_provider_not_configured():
    call_count = 0

    async def unconfigured_operation():
        nonlocal call_count
        call_count += 1
        raise ProviderNotConfigured("ZerodhaMarketProvider")

    with pytest.raises(ProviderNotConfigured):
        await execute_with_retry(unconfigured_operation, max_retries=3, base_delay=0.01)

    assert call_count == 1
