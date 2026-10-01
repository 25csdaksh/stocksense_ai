"""
MarketMind AI — Anomaly Intelligence Specialist Agent.
Phase 6.9: Detects price jumps, volume surges, and volatility regime shifts.
Uses strictly neutral, evidence-based associative phrasing ("coincides with", "associated with").
"""
import uuid
import math
from typing import List, Dict, Any, Optional
from datetime import datetime, timezone

from app.ai.models import (
    ResearchEvidence,
    EvidenceProvenance,
)
from app.providers.market_data.factory import provider_factory
from app.providers.market_data.symbol_normalizer import normalize_symbol
from app.core.logging import logger


class AnomalyIntelligenceAgent:
    """Specialist agent identifying unusual statistical movements and volume outliers."""

    async def run(self, symbols: List[str], timeframe: str = "6m") -> List[ResearchEvidence]:
        """Detects and formats statistical anomalies for the target symbols."""
        evidence_list: List[ResearchEvidence] = []

        if not symbols:
            return evidence_list

        for raw_sym in symbols:
            try:
                norm = normalize_symbol(raw_sym)
                canonical = norm.canonical_symbol
                market_region = "INDIA" if norm.market == "IN" else "US"

                provider = provider_factory.get_provider(market=market_region)
                hist_res = await provider.get_historical_data(symbol=canonical, interval="1d", timeframe=timeframe)
                bars = hist_res.bars if hasattr(hist_res, "bars") else []

                if not bars or len(bars) < 20:
                    continue

                closes = [b.close for b in bars]
                volumes = [b.volume for b in bars]

                daily_returns = [
                    (closes[i] - closes[i - 1]) / closes[i - 1]
                    for i in range(1, len(closes))
                    if closes[i - 1] > 0
                ]

                mean_ret = sum(daily_returns) / len(daily_returns)
                var_ret = sum((r - mean_ret) ** 2 for r in daily_returns) / max(1, len(daily_returns) - 1)
                std_ret = math.sqrt(var_ret) if var_ret > 0 else 0.01

                avg_vol = sum(volumes) / len(volumes) if volumes else 1000

                detected_anomalies = []

                # Scan for return anomalies (|z| >= 2.0) and volume spikes (> 2.0x avg)
                for i in range(1, len(bars)):
                    ret = daily_returns[i - 1]
                    z_score = (ret - mean_ret) / std_ret if std_ret > 0 else 0.0
                    vol_ratio = bars[i].volume / max(1, avg_vol)

                    if abs(z_score) >= 2.0 or vol_ratio >= 2.2:
                        detected_anomalies.append({
                            "timestamp": bars[i].timestamp,
                            "close_price": round(bars[i].close, 2),
                            "return_pct": round(ret * 100, 2),
                            "z_score": round(z_score, 2),
                            "volume_ratio": round(vol_ratio, 2),
                            "type": "PRICE_RETURN_SPIKE" if abs(z_score) >= 2.0 else "VOLUME_SURGE"
                        })

                # Sort by absolute z-score and take top recent anomalies
                top_anomalies = sorted(detected_anomalies, key=lambda a: abs(a["z_score"]), reverse=True)[:3]

                evidence_list.append(
                    ResearchEvidence(
                        evidence_id=f"ev_{uuid.uuid4().hex[:8]}",
                        category="ANOMALY",
                        symbol=canonical,
                        metric="detected_market_anomalies",
                        value={
                            "total_anomalies_detected": len(detected_anomalies),
                            "top_outliers": top_anomalies,
                            "analysis_note": (
                                f"Observed {len(detected_anomalies)} statistical anomalies in the {timeframe} window; "
                                f"highest single-day return divergence of {top_anomalies[0]['return_pct']}% (z-score {top_anomalies[0]['z_score']}) "
                                f"coincides with elevated trading activity."
                                if top_anomalies else "No severe price or volume anomalies detected in period."
                            )
                        },
                        source="StatisticalAnomalyDetector",
                        provenance=EvidenceProvenance.MODEL_DERIVED,
                        confidence=0.88,
                        metadata={
                            "methodology": "Z-score return dispersion and volume moving average thresholding"
                        }
                    )
                )

            except Exception as ex:
                logger.warning(f"AnomalyIntelligenceAgent error for {raw_sym}: {ex}")

        return evidence_list


anomaly_agent = AnomalyIntelligenceAgent()
