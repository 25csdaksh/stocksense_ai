"""
System Health & Telemetry API Routes.
"""
from datetime import datetime
from typing import Dict, Any
from fastapi import APIRouter
from app.core.config import settings

router = APIRouter(tags=["System Health"])


@router.get("/health")
async def health_check() -> Dict[str, Any]:
    """System health check endpoint for monitoring, kubernetes probes, and uptime telemetry."""
    return {
        "status": "healthy",
        "service": settings.PROJECT_NAME,
        "version": settings.VERSION,
        "environment": settings.ENVIRONMENT,
        "timestamp": datetime.utcnow().isoformat(),
        "components": {
            "api_server": "operational",
            "market_data_engine": "operational",
            "analytics_engine": "operational",
            "rag_retrieval_engine": "operational",
            "multi_agent_framework": "operational",
            "cache_layer": "operational"
        }
    }
