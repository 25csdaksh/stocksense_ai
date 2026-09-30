"""
MarketMind AI — Provider Rate Limit State & Token Tracker.
Monitors quota limits, remaining requests, and calculates backoff cooldowns without violating broker terms.
"""
import time
from typing import Dict, Any, Optional
from app.providers.market_data.exceptions import RateLimitExceeded


class ProviderRateLimiter:
    """Tracks provider request rates, remaining quota, and enforces client-side limits."""

    def __init__(self, provider_name: str, max_requests_per_minute: int = 60):
        self.provider_name = provider_name
        self.max_requests = max_requests_per_minute
        self.window_seconds = 60.0
        self.timestamps: list = []
        self._custom_retry_after: Optional[float] = None

    def record_request(self) -> None:
        """Records a new outbound request timestamp and prunes expired history."""
        now = time.time()
        self.timestamps = [t for t in self.timestamps if now - t < self.window_seconds]
        self.timestamps.append(now)

    def check_rate_limit(self) -> None:
        """Checks if current request would exceed allowable window quota."""
        now = time.time()
        self.timestamps = [t for t in self.timestamps if now - t < self.window_seconds]

        if len(self.timestamps) >= self.max_requests:
            earliest = self.timestamps[0]
            retry_after = max(1, int(self.window_seconds - (now - earliest)))
            raise RateLimitExceeded(
                provider_name=self.provider_name,
                retry_after_seconds=retry_after
            )

    @property
    def requests_remaining(self) -> int:
        """Calculates current requests remaining in the rolling window."""
        now = time.time()
        active = [t for t in self.timestamps if now - t < self.window_seconds]
        return max(0, self.max_requests - len(active))

    @property
    def rate_limit_status(self) -> str:
        """Returns human-readable rate limit status: NORMAL, WARNING, THROTTLED."""
        remaining = self.requests_remaining
        if remaining == 0:
            return "THROTTLED"
        elif remaining < (self.max_requests * 0.2):
            return "WARNING"
        return "NORMAL"

    def get_telemetry(self) -> Dict[str, Any]:
        return {
            "provider": self.provider_name,
            "requests_remaining": self.requests_remaining,
            "max_requests": self.max_requests,
            "status": self.rate_limit_status
        }
