"""
Correlation Matrix & Network Relationship Graph Endpoints.
"""
from typing import List, Optional
from fastapi import APIRouter, Query
import pandas as pd
from schemas.analytics_schema import CorrelationMatrixResponse, RelationshipGraphResponse
from services.market_data_service import market_data_service, SUPPORTED_UNIVERSE

import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", "ml-engine")))
from engine import ml_engine

router = APIRouter(prefix="/correlations", tags=["Correlation & Systemic Graph"])


def _build_returns_dataframe() -> pd.DataFrame:
    tickers = list(SUPPORTED_UNIVERSE.keys())
    data = {}
    for t in tickers:
        hist = market_data_service.get_history(t, range_str="6m")
        bars = hist["bars"]
        if bars:
            closes = [b["close"] for b in bars]
            df = pd.Series(closes)
            returns = df.pct_change().dropna()
            data[t] = returns.values[-90:]  # align last 90 trading days
    return pd.DataFrame(data)


@router.get("/matrix", response_model=CorrelationMatrixResponse)
async def get_correlation_matrix(method: str = Query(default="pearson", pattern="^(pearson|spearman)$")):
    """Computes dynamic pairwise correlation matrix across core equities and ETFs."""
    returns_df = _build_returns_dataframe()
    return ml_engine.correlation_engine.compute_correlation_matrix(returns_df, method=method)


@router.get("/graph", response_model=RelationshipGraphResponse)
async def get_relationship_graph(threshold: float = Query(default=0.45, ge=0.1, le=0.9)):
    """Builds interactive systemic contagion network graph with PageRank & centrality metrics."""
    returns_df = _build_returns_dataframe()
    metadata_map = {t: {"name": v["name"], "sector": v["sector"], "market_cap": v.get("market_cap", 1e11)} for t, v in SUPPORTED_UNIVERSE.items()}
    return ml_engine.build_relationship_graph(returns_df, metadata_map, threshold=threshold)
