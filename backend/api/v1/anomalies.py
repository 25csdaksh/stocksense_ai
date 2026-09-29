"""
Anomaly Detection & Volatility Regime Endpoints.
"""
from typing import List
from datetime import datetime
from fastapi import APIRouter
import pandas as pd
from schemas.analytics_schema import AnomalyStreamResponse
from services.market_data_service import market_data_service, SUPPORTED_UNIVERSE

import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", "ml-engine")))
from engine import ml_engine

router = APIRouter(prefix="/analytics", tags=["Market Anomalies & Volatility"])


@router.get("/anomalies", response_model=AnomalyStreamResponse)
async def get_detected_anomalies():
    """Scans the active universe for statistical anomalies (Isolation Forest + GARCH + Volume Spikes)."""
    detected_list = []
    
    for ticker in list(SUPPORTED_UNIVERSE.keys())[:6]:
        hist = market_data_service.get_history(ticker, range_str="6m")
        bars = hist["bars"]
        if len(bars) > 20:
            df = pd.DataFrame(bars)
            df.set_index("time", inplace=True)
            res = ml_engine.run_anomaly_pipeline(df, ticker)
            for anom in res["detected_anomalies"][-2:]:  # latest 2
                detected_list.append(anom)

    detected_list.sort(key=lambda x: x["severity_score"], reverse=True)
    
    # Compute systemic market stress score
    avg_severity = sum(a["severity_score"] for a in detected_list) / max(1, len(detected_list))
    stress_idx = round(float(avg_severity * 100), 1)

    return {
        "anomalies": detected_list,
        "total_active": len(detected_list),
        "systemic_stress_index": stress_idx,
        "timestamp": datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC")
    }
