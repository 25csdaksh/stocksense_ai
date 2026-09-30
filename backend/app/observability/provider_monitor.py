"""
MarketMind AI — Provider Health, Availability & Latency Monitoring Service.
Phase 6.8: Tracks per-provider request metrics, failure rates, latency percentiles (p50/p95/p99),
and rate limit hits across Indian, US, and demo market data & news feeds.
"""
import time
import statistics
import collections
from typing import Dict, Any, List, Optional
from datetime import datetime, timezone

from app.observability.models import (
    ProviderHealthReport,
    ProviderHealthStatus,
    LatencyMetrics,
)


class ProviderHealthMonitor:
    """Tracks latency percentiles and operational health metrics for external providers."""

    def __init__(self):
        # provider_name -> { requests, successes, failures, rate_limits, latencies: deque, last_success, last_failure, market, status }
        self._providers: Dict[str, Dict[str, Any]] = {
            "ZerodhaKite": {
                "market": "INDIA",
                "status": ProviderHealthStatus.CONFIGURATION_REQUIRED,
                "auth_status": "CREDENTIALS_REQUIRED",
                "requests": 0, "successes": 0, "failures": 0, "rate_limits": 0,
                "latencies": collections.deque(maxlen=500),
                "last_success": None, "last_failure": None
            },
            "IndianMarketProvider": {
                "market": "INDIA",
                "status": ProviderHealthStatus.DEMO,
                "auth_status": "DEMO_ACTIVE",
                "requests": 0, "successes": 0, "failures": 0, "rate_limits": 0,
                "latencies": collections.deque(maxlen=500),
                "last_success": datetime.now(timezone.utc).isoformat(), "last_failure": None
            },
            "USMarketProvider": {
                "market": "US",
                "status": ProviderHealthStatus.DEMO,
                "auth_status": "DEMO_ACTIVE",
                "requests": 0, "successes": 0, "failures": 0, "rate_limits": 0,
                "latencies": collections.deque(maxlen=500),
                "last_success": datetime.now(timezone.utc).isoformat(), "last_failure": None
            },
            "IndianNewsProvider": {
                "market": "INDIA",
                "status": ProviderHealthStatus.DEMO,
                "auth_status": "DEMO_ACTIVE",
                "requests": 0, "successes": 0, "failures": 0, "rate_limits": 0,
                "latencies": collections.deque(maxlen=500),
                "last_success": datetime.now(timezone.utc).isoformat(), "last_failure": None
            },
            "USNewsProvider": {
                "market": "US",
                "status": ProviderHealthStatus.DEMO,
                "auth_status": "DEMO_ACTIVE",
                "requests": 0, "successes": 0, "failures": 0, "rate_limits": 0,
                "latencies": collections.deque(maxlen=500),
                "last_success": datetime.now(timezone.utc).isoformat(), "last_failure": None
            }
        }

    def record_request(
        self,
        provider_name: str,
        success: bool,
        latency_ms: float,
        is_rate_limited: bool = False,
        error_msg: Optional[str] = None
    ) -> None:
        """Records an external provider call and updates latency distribution."""
        now_iso = datetime.now(timezone.utc).isoformat()
        entry = self._providers.setdefault(
            provider_name,
            {
                "market": "GLOBAL",
                "status": ProviderHealthStatus.DEMO,
                "auth_status": "CONFIGURED",
                "requests": 0, "successes": 0, "failures": 0, "rate_limits": 0,
                "latencies": collections.deque(maxlen=500),
                "last_success": None, "last_failure": None
            }
        )

        entry["requests"] += 1
        entry["latencies"].append(max(0.1, latency_ms))

        if success:
            entry["successes"] += 1
            entry["last_success"] = now_iso
        else:
            entry["failures"] += 1
            entry["last_failure"] = now_iso

        if is_rate_limited:
            entry["rate_limits"] += 1
            entry["status"] = ProviderHealthStatus.RATE_LIMITED
        elif not success and entry["failures"] > 5 and (entry["failures"] / entry["requests"]) > 0.5:
            entry["status"] = ProviderHealthStatus.DEGRADED

    def get_provider_report(self, provider_name: str) -> Optional[ProviderHealthReport]:
        """Returns health and latency summary for a single provider."""
        entry = self._providers.get(provider_name)
        if not entry:
            return None

        lat_list = sorted(list(entry["latencies"]))
        count = len(lat_list)
        if count > 0:
            avg_ms = round(statistics.mean(lat_list), 2)
            p50_ms = round(statistics.median(lat_list), 2)
            p95_idx = int(count * 0.95)
            p99_idx = int(count * 0.99)
            p95_ms = round(lat_list[min(p95_idx, count - 1)], 2)
            p99_ms = round(lat_list[min(p99_idx, count - 1)], 2)
            max_ms = round(max(lat_list), 2)
        else:
            avg_ms = p50_ms = p95_ms = p99_ms = max_ms = 0.0

        reqs = entry["requests"]
        fails = entry["failures"]
        err_rate = round((fails / max(1, reqs)) * 100, 2) if reqs > 0 else 0.0

        return ProviderHealthReport(
            provider_name=provider_name,
            market=entry["market"],
            status=entry["status"],
            last_success=entry["last_success"],
            last_failure=entry["last_failure"],
            request_count=reqs,
            success_count=entry["successes"],
            failure_count=fails,
            error_rate_pct=err_rate,
            latency=LatencyMetrics(
                count=count,
                average_ms=avg_ms,
                p50_ms=p50_ms,
                p95_ms=p95_ms,
                p99_ms=p99_ms,
                max_ms=max_ms
            ),
            rate_limit_hits=entry["rate_limits"],
            authentication_status=entry["auth_status"],
            data_freshness_sec=12.0
        )

    def get_all_reports(self) -> List[ProviderHealthReport]:
        """Returns telemetry reports for all registered providers."""
        reports = []
        for name in self._providers.keys():
            rep = self.get_provider_report(name)
            if rep:
                reports.append(rep)
        return reports


provider_monitor = ProviderHealthMonitor()
