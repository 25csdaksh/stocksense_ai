"""
Technical Indicators, Rolling Correlation, Systemic Graph & Stock DNA Routes.
"""
from typing import Dict, Any
from fastapi import APIRouter, Query
from app.schemas.analytics import (
    TechnicalAnalyticsResponse,
    CorrelationMatrixResponse,
    RelationshipGraphResponse,
    StockDNAResponse
)
from app.services.analytics_service import analytics_service

router = APIRouter(prefix="/analytics", tags=["Quantitative Analytics"])


@router.get("/correlations", response_model=CorrelationMatrixResponse)
async def get_correlation_matrix(
    method: str = Query(default="pearson", description="Correlation method: pearson or spearman")
):
    """Computes cross-asset rolling return correlation matrix and highlights top pairs."""
    return await analytics_service.get_correlation_matrix(method=method)


@router.get("/relationship-graph", response_model=RelationshipGraphResponse)
async def get_relationship_graph(
    threshold: float = Query(default=0.45, ge=0.0, le=1.0, description="Minimum correlation threshold for edge creation")
):
    """Computes NetworkX systemic market relationship graph with eigenvector centrality."""
    return await analytics_service.get_relationship_graph(threshold=threshold)


@router.get("/{symbol}/technical", response_model=TechnicalAnalyticsResponse)
async def get_technical_analytics(symbol: str):
    """Computes SMA, EMA, RSI, MACD, Bollinger Bands, ATR, and realized volatility for a ticker."""
    return await analytics_service.get_technical_analysis(symbol)


@router.get("/{symbol}/dna", response_model=StockDNAResponse)
async def get_stock_dna(symbol: str):
    """Computes 5-factor quantitative Stock DNA profile (Value, Growth, Quality, Momentum, Low Volatility)."""
    return await analytics_service.get_stock_dna(symbol)
