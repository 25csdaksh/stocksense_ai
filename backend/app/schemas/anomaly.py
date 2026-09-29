"""
Market Anomaly & Volatility Stream Schemas.
"""
from typing import List, Dict, Any, Optional
from pydantic import BaseModel


class AnomalyItem(BaseModel):
    ticker: str
    timestamp: str
    anomaly_type: str
    severity_score: float
    isolation_score: Optional[float] = None
    summary: str
    metrics: Dict[str, Any]


class AnomalyStreamResponse(BaseModel):
    anomalies: List[AnomalyItem]
    total_active: int
    systemic_stress_index: float
    timestamp: str
