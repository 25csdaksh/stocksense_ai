"""
MarketMind AI — Provider Health API Routes.
Phase 6.8: Telemetry, latency distributions, and authentication state for external data providers.
"""
from typing import List
from fastapi import APIRouter

from app.observability.models import ProviderHealthReport
from app.observability.provider_monitor import provider_monitor

router = APIRouter(prefix="/providers", tags=["Provider Observability"])


@router.get("/health", response_model=List[ProviderHealthReport])
async def get_providers_health() -> List[ProviderHealthReport]:
    """Returns operational health, error rates, p50/p95/p99 latency percentiles across all external providers."""
    return provider_monitor.get_all_reports()
