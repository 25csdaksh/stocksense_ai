"""
Market Anomaly Detection & Volatility Regime Routes.
"""
from typing import Dict, Any
from fastapi import APIRouter
from app.schemas.anomaly import AnomalyStreamResponse
from app.services.anomaly_service import anomaly_service

router = APIRouter(prefix="/anomalies", tags=["Anomaly & Volatility Detection"])


@router.get("", response_model=AnomalyStreamResponse)
async def get_market_anomaly_stream():
    """Retrieves cross-universe multivariate anomaly stream and systemic stress index."""
    return await anomaly_service.get_market_anomaly_stream()


@router.get("/{symbol}", response_model=Dict[str, Any])
async def get_ticker_anomalies(symbol: str):
    """Retrieves ticker-level Isolation Forest anomalies, GARCH(1,1) volatility forecasts, and volume spikes."""
    return await anomaly_service.get_ticker_anomalies(symbol)
