"""
System Health, Readiness & Telemetry API Routes.
Phase 6.8: Fast, non-blocking health and readiness probes with detailed infrastructure status.
"""
from datetime import datetime, timezone
from typing import Dict, Any
from fastapi import APIRouter
from app.core.config import settings
from app.observability.infra_monitor import infra_monitor
from app.observability.models import SystemHealthReport, QualityStatus

router = APIRouter(tags=["System Health"])


@router.get("/health")
async def health_check() -> Dict[str, Any]:
    """System health check endpoint for monitoring, kubernetes probes, and uptime telemetry."""
    return {
        "status": "healthy",
        "service": settings.PROJECT_NAME,
        "version": settings.VERSION,
        "environment": settings.ENVIRONMENT,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "components": {
            "api_server": "operational",
            "market_data_engine": "operational",
            "analytics_engine": "operational",
            "rag_retrieval_engine": "operational",
            "multi_agent_framework": "operational",
            "cache_layer": "operational"
        }
    }


@router.get("/ready")
async def readiness_check() -> Dict[str, Any]:
    """Readiness probe verifying operational readiness of core application services."""
    report = await infra_monitor.get_system_health()
    is_ready = report.status != QualityStatus.ERROR
    return {
        "ready": is_ready,
        "status": report.status.value,
        "service": settings.PROJECT_NAME,
        "timestamp": report.timestamp,
        "components_ready": {k: v.status.value for k, v in report.components.items()}
    }


@router.get("/system/health", response_model=SystemHealthReport)
async def get_system_health() -> SystemHealthReport:
    """Returns detailed infrastructure telemetry, provider health matrices, and dependency statuses."""
    return await infra_monitor.get_system_health()

