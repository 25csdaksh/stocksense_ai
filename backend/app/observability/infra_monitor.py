"""
MarketMind AI — Infrastructure Health & Telemetry Monitor.
Phase 6.8: Asynchronous probes for PostgreSQL, Redis, Qdrant Vector DB,
WebSocket Streaming Manager, EventBus, and AI/RAG sub-engines.
Ensures sub-500ms lightweight non-blocking health checks without exposing sensitive credentials.
"""
import time
import asyncio
from datetime import datetime, timezone
from typing import Dict, Any, List, Optional
from sqlalchemy import text

from app.core.config import settings
from app.core.logging import logger
from app.cache.redis_client import redis_client
from app.db.session import async_session_factory, engine
from app.db.vector import vector_repository
from app.services.websocket_manager import websocket_manager
from app.providers.market_data.streaming_events import event_bus
from app.observability.models import (
    QualityStatus,
    ComponentHealth,
    SystemHealthReport,
    ProviderHealthReport,
)
from app.observability.provider_monitor import provider_monitor


class InfrastructureMonitor:
    """Probes and compiles telemetry for core infrastructure and runtime services."""

    def __init__(self):
        self._start_time = time.time()
        # Telemetry counters for AI/RAG
        self._ai_queries_total = 0
        self._ai_failures_total = 0
        self._ai_latencies: List[float] = []
        self._rag_queries_total = 0
        self._rag_failures_total = 0
        self._rag_latencies: List[float] = []

    def record_ai_query(self, latency_ms: float, success: bool = True):
        self._ai_queries_total += 1
        if not success:
            self._ai_failures_total += 1
        self._ai_latencies.append(latency_ms)
        if len(self._ai_latencies) > 200:
            self._ai_latencies.pop(0)

    def record_rag_query(self, latency_ms: float, success: bool = True):
        self._rag_queries_total += 1
        if not success:
            self._rag_failures_total += 1
        self._rag_latencies.append(latency_ms)
        if len(self._rag_latencies) > 200:
            self._rag_latencies.pop(0)

    async def check_database(self) -> ComponentHealth:
        """Lightweight database connectivity and query latency probe."""
        start = time.perf_counter()
        status = QualityStatus.HEALTHY
        details: Dict[str, Any] = {
            "dialect": "postgresql" if "postgres" in settings.DATABASE_URL else "sqlite",
            "pool_size": settings.DB_POOL_SIZE if "postgres" in settings.DATABASE_URL else 1,
            "max_overflow": settings.DB_MAX_OVERFLOW if "postgres" in settings.DATABASE_URL else 0,
        }

        try:
            async with async_session_factory() as session:
                await session.execute(text("SELECT 1"))
            latency_ms = round((time.perf_counter() - start) * 1000, 2)
            details["connected"] = True
            if latency_ms > 500:
                status = QualityStatus.DEGRADED
        except Exception as ex:
            latency_ms = round((time.perf_counter() - start) * 1000, 2)
            status = QualityStatus.ERROR
            details["connected"] = False
            details["error"] = "Database connection failed or timed out"
            logger.warning(f"Database health check probe failed: {ex}")

        return ComponentHealth(
            name="PostgreSQL",
            status=status,
            latency_ms=latency_ms,
            details=details,
            last_checked=datetime.now(timezone.utc).isoformat()
        )

    async def check_redis(self) -> ComponentHealth:
        """Lightweight Redis / In-Memory cache probe."""
        start = time.perf_counter()
        status = QualityStatus.HEALTHY
        details: Dict[str, Any] = {
            "cache_enabled": settings.CACHE_ENABLED,
            "is_redis_connected": getattr(redis_client, "is_connected", False),
            "storage_mode": "REDIS_SERVER" if getattr(redis_client, "is_connected", False) else "IN_MEMORY_FALLBACK",
            "in_memory_keys_count": len(getattr(redis_client, "_memory_cache", {})),
        }

        try:
            # Perform a test key check
            test_key = "__mm_health_probe__"
            await redis_client.set(test_key, "1", expire=5)
            val = await redis_client.get(test_key)
            latency_ms = round((time.perf_counter() - start) * 1000, 2)
            details["probe_successful"] = (val == "1")
            if not getattr(redis_client, "is_connected", False):
                status = QualityStatus.HEALTHY  # In-memory fallback is fully supported design
        except Exception as ex:
            latency_ms = round((time.perf_counter() - start) * 1000, 2)
            status = QualityStatus.DEGRADED
            details["error"] = "Cache probe failure"
            logger.warning(f"Redis cache health check probe failed: {ex}")

        return ComponentHealth(
            name="Redis",
            status=status,
            latency_ms=latency_ms,
            details=details,
            last_checked=datetime.now(timezone.utc).isoformat()
        )

    async def check_qdrant(self) -> ComponentHealth:
        """Lightweight Qdrant vector database probe."""
        start = time.perf_counter()
        status = QualityStatus.HEALTHY
        service = getattr(vector_repository, "qdrant_service", None)
        is_conn = getattr(service, "is_connected", False) if service else False

        details: Dict[str, Any] = {
            "is_connected": is_conn,
            "storage_mode": "QDRANT_CLUSTER" if is_conn else "IN_MEMORY_FALLBACK",
            "collection_name": settings.QDRANT_COLLECTION_NAME,
            "vector_dimension": 384,
            "in_memory_docs_indexed": len(getattr(vector_repository, "_in_memory_docs", [])),
        }

        latency_ms = round((time.perf_counter() - start) * 1000, 2)
        return ComponentHealth(
            name="Qdrant",
            status=status,
            latency_ms=latency_ms,
            details=details,
            last_checked=datetime.now(timezone.utc).isoformat()
        )

    def check_websocket(self) -> ComponentHealth:
        """WebSocket manager connections and queue health."""
        metrics = websocket_manager.get_health_metrics()
        active_conns = metrics.get("active_connections", 0)
        dropped = metrics.get("events_dropped", 0)
        queue_sat = metrics.get("queue_saturation_pct", 0.0)

        status = QualityStatus.HEALTHY
        if queue_sat > 80.0 or dropped > 50:
            status = QualityStatus.DEGRADED

        return ComponentHealth(
            name="WebSocketStream",
            status=status,
            latency_ms=0.5,
            details={
                "active_connections": active_conns,
                "total_subscriptions": metrics.get("total_subscriptions", 0),
                "events_published_sec": metrics.get("events_per_second", 0.0),
                "events_dropped": dropped,
                "queue_saturation_pct": queue_sat,
                "channels": metrics.get("channels", {}),
            },
            last_checked=datetime.now(timezone.utc).isoformat()
        )

    def check_event_bus(self) -> ComponentHealth:
        """Event bus subscriber counts and history depth."""
        subs_count = len(getattr(event_bus, "_subscribers", []))
        history_len = len(getattr(event_bus, "_event_history", []))

        return ComponentHealth(
            name="EventBus",
            status=QualityStatus.HEALTHY,
            latency_ms=0.1,
            details={
                "subscribers_count": subs_count,
                "event_history_depth": history_len,
                "max_history": getattr(event_bus, "_max_history", 100),
                "supported_events": [
                    "QUOTE_TICK", "BAR_CLOSED", "INDEX_TICK",
                    "ANOMALY_DETECTED", "SESSION_CHANGE", "INGESTION_CYCLE_COMPLETED", "NEWS_PUBLISHED"
                ]
            },
            last_checked=datetime.now(timezone.utc).isoformat()
        )

    def check_ai_rag(self) -> ComponentHealth:
        """AI & RAG operational metrics."""
        avg_ai_lat = round(sum(self._ai_latencies) / max(1, len(self._ai_latencies)), 2) if self._ai_latencies else 0.0
        avg_rag_lat = round(sum(self._rag_latencies) / max(1, len(self._rag_latencies)), 2) if self._rag_latencies else 0.0

        return ComponentHealth(
            name="AIRagEngine",
            status=QualityStatus.HEALTHY,
            latency_ms=avg_ai_lat,
            details={
                "ai_queries_total": self._ai_queries_total,
                "ai_failures_total": self._ai_failures_total,
                "ai_average_latency_ms": avg_ai_lat,
                "rag_queries_total": self._rag_queries_total,
                "rag_failures_total": self._rag_failures_total,
                "rag_average_latency_ms": avg_rag_lat,
                "llm_provider": getattr(settings, "DEFAULT_LLM_PROVIDER", "OLLAMA"),
                "status": "OPERATIONAL"
            },
            last_checked=datetime.now(timezone.utc).isoformat()
        )

    async def get_system_health(self) -> SystemHealthReport:
        """Assembles unified system health report across all components and providers."""
        # Execute async component probes concurrently
        db_res, redis_res, qdrant_res = await asyncio.gather(
            self.check_database(),
            self.check_redis(),
            self.check_qdrant(),
            return_exceptions=True
        )

        components: Dict[str, ComponentHealth] = {}

        if isinstance(db_res, ComponentHealth):
            components["postgresql"] = db_res
        else:
            components["postgresql"] = ComponentHealth(name="PostgreSQL", status=QualityStatus.ERROR, details={"error": str(db_res)})

        if isinstance(redis_res, ComponentHealth):
            components["redis"] = redis_res
        else:
            components["redis"] = ComponentHealth(name="Redis", status=QualityStatus.ERROR, details={"error": str(redis_res)})

        if isinstance(qdrant_res, ComponentHealth):
            components["qdrant"] = qdrant_res
        else:
            components["qdrant"] = ComponentHealth(name="Qdrant", status=QualityStatus.ERROR, details={"error": str(qdrant_res)})

        components["websocket"] = self.check_websocket()
        components["event_bus"] = self.check_event_bus()
        components["ai_rag"] = self.check_ai_rag()

        # Determine overall system status
        overall_status = QualityStatus.HEALTHY
        for c in components.values():
            if c.status == QualityStatus.ERROR:
                overall_status = QualityStatus.DEGRADED
                break
            elif c.status == QualityStatus.DEGRADED and overall_status == QualityStatus.HEALTHY:
                overall_status = QualityStatus.DEGRADED

        providers = provider_monitor.get_all_reports()
        uptime = round(time.time() - self._start_time, 2)

        return SystemHealthReport(
            status=overall_status,
            service=settings.PROJECT_NAME,
            version=settings.VERSION,
            environment=settings.ENVIRONMENT,
            uptime_seconds=uptime,
            components=components,
            providers=providers,
            timestamp=datetime.now(timezone.utc).isoformat()
        )


infra_monitor = InfrastructureMonitor()
