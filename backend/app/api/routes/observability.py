"""
MarketMind AI — Observability & Metrics API Routes.
Phase 6.8: Structured JSON metrics endpoint for telemetry scrapers and platform monitoring.
"""
from typing import Dict, Any
from fastapi import APIRouter
from app.observability.infra_monitor import infra_monitor
from app.observability.provider_monitor import provider_monitor
from app.observability.quality_coordinator import quality_coordinator
from app.services.websocket_manager import websocket_manager
from app.services.market_data_collector import market_data_collector

router = APIRouter(prefix="/observability", tags=["Observability & Metrics"])


@router.get("/metrics")
async def get_metrics() -> Dict[str, Any]:
    """Returns structured platform telemetry and performance metrics."""
    sys_health = await infra_monitor.get_system_health()
    ws_metrics = websocket_manager.get_health_metrics()
    ingest_metrics = market_data_collector.get_collector_status()
    providers = provider_monitor.get_all_reports()

    # Aggregate provider latency and error counts
    total_reqs = sum(p.request_count for p in providers)
    total_fails = sum(p.failure_count for p in providers)
    avg_latency = round(sum(p.latency.average_ms for p in providers) / max(1, len(providers)), 2)

    return {
        "marketmind_telemetry_version": "1.0.0",
        "system_status": sys_health.status.value,
        "system_uptime_seconds": sys_health.uptime_seconds,
        "metrics": {
            "market_quote_latency_ms": avg_latency,
            "market_quote_requests_total": total_reqs,
            "market_quote_errors_total": total_fails,
            "ingestion_cycles_completed_total": ingest_metrics.get("cycles_completed", 0),
            "ingestion_cycles_failed_total": ingest_metrics.get("cycles_failed", 0),
            "ingestion_records_processed_total": ingest_metrics.get("records_processed", 0),
            "websocket_connections_active": ws_metrics.get("active_connections", 0),
            "websocket_subscriptions_total": ws_metrics.get("total_subscriptions", 0),
            "websocket_events_published_sec": ws_metrics.get("events_per_second", 0.0),
            "websocket_events_dropped_total": ws_metrics.get("events_dropped", 0),
            "websocket_queue_saturation_pct": ws_metrics.get("queue_saturation_pct", 0.0),
            "redis_status": sys_health.components.get("redis", {}).status.value if sys_health.components.get("redis") else "UNKNOWN",
            "postgresql_status": sys_health.components.get("postgresql", {}).status.value if sys_health.components.get("postgresql") else "UNKNOWN",
            "qdrant_status": sys_health.components.get("qdrant", {}).status.value if sys_health.components.get("qdrant") else "UNKNOWN",
            "ai_queries_total": getattr(infra_monitor, "_ai_queries_total", 0),
            "ai_query_latency_ms": round(sum(getattr(infra_monitor, "_ai_latencies", [])) / max(1, len(getattr(infra_monitor, "_ai_latencies", []))), 2) if getattr(infra_monitor, "_ai_latencies", []) else 0.0,
        },
        "providers": [
            {
                "name": p.provider_name,
                "market": p.market,
                "status": p.status.value,
                "error_rate_pct": p.error_rate_pct,
                "average_latency_ms": p.latency.average_ms,
                "p95_latency_ms": p.latency.p95_ms
            }
            for p in providers
        ]
    }
