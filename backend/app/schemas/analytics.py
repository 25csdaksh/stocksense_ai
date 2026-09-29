"""
Analytics, Correlation, Systemic Graph & Stock DNA Schemas.
"""
from typing import List, Dict, Any, Optional
from pydantic import BaseModel


class TechnicalAnalyticsResponse(BaseModel):
    ticker: str
    sma_20: float
    sma_50: float
    ema_20: float
    rsi_14: float
    macd: Dict[str, float]
    bollinger_bands: Dict[str, float]
    atr_14: float
    realized_volatility_20d_pct: float
    technical_bias: str  # BULLISH, BEARISH, NEUTRAL


class CorrelationPair(BaseModel):
    asset_a: str
    asset_b: str
    correlation: float


class CorrelationMatrixResponse(BaseModel):
    assets: List[str]
    matrix: List[List[float]]
    method: str
    top_pairs: List[CorrelationPair]
    observations: int


class NetworkNodeSchema(BaseModel):
    id: str
    label: str
    name: str
    sector: str
    degree: int
    eigenvector_centrality: float
    betweenness_centrality: float
    annualized_volatility: float


class NetworkEdgeSchema(BaseModel):
    source: str
    target: str
    weight: float
    correlation: float
    edge_type: str


class RelationshipGraphResponse(BaseModel):
    nodes: List[NetworkNodeSchema]
    edges: List[NetworkEdgeSchema]
    network_metrics: Dict[str, Any]


class StockDNARadarItem(BaseModel):
    factor: str
    score: float
    fullMark: int = 100


class StockDNAResponse(BaseModel):
    ticker: str
    factor_scores: Dict[str, float]
    radar_data: List[StockDNARadarItem]
    dominant_persona: str
    summary: str
