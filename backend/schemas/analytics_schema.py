"""
ML Analytics, Anomaly, Correlation, and Stock DNA Schemas.
"""
from typing import List, Dict, Any, Optional
from pydantic import BaseModel


class AnomalyItem(BaseModel):
    ticker: str
    timestamp: str
    anomaly_type: str  # 'VOLUME_SPIKE', 'PRICE_GAP', 'VOLATILITY_BURST', 'CORRELATION_BREAK'
    severity_score: float
    isolation_score: Optional[float] = None
    summary: str
    metrics: Dict[str, Any]


class AnomalyStreamResponse(BaseModel):
    anomalies: List[AnomalyItem]
    total_active: int
    systemic_stress_index: float  # 0.0 to 100.0
    timestamp: str


class TopCorrelatedPair(BaseModel):
    asset_a: str
    asset_b: str
    correlation: float


class CorrelationMatrixResponse(BaseModel):
    assets: List[str]
    matrix: List[List[float]]
    method: str
    top_pairs: List[TopCorrelatedPair]
    observations: int


class NetworkNode(BaseModel):
    id: str
    label: str
    name: str
    sector: str
    degree: int
    eigenvector_centrality: float
    betweenness_centrality: float
    annualized_volatility: float


class NetworkEdge(BaseModel):
    source: str
    target: str
    weight: float
    correlation: float
    edge_type: str


class RelationshipGraphResponse(BaseModel):
    nodes: List[NetworkNode]
    edges: List[NetworkEdge]
    network_metrics: Dict[str, Any]


class FactorScoreItem(BaseModel):
    factor: str
    score: float
    fullMark: int = 100


class StockDNAResponse(BaseModel):
    ticker: str
    factor_scores: Dict[str, float]
    radar_data: List[FactorScoreItem]
    dominant_persona: str
    summary: str
    peer_comparisons: Optional[List[Dict[str, Any]]] = None
