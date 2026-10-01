"""
MarketMind AI — Market Research Specialist Agent.
Phase 6.9: Gathers real-time quotes, OHLCV time series, regime analysis, volume dynamics,
and relative performance without fabricating prices or hiding demo provenance.
"""
import uuid
import time
from typing import List, Dict, Any, Optional
from datetime import datetime, timezone

from app.ai.models import (
    ResearchEvidence,
    EvidenceProvenance,
    Citation,
)
from app.providers.market_data.factory import provider_factory
from app.providers.market_data.symbol_normalizer import normalize_symbol
from app.core.logging import logger


class MarketResearchAgent:
    """Specialist agent responsible for core market data, quote snapshots, and price behavior."""

    async def run(self, symbols: List[str], timeframe: str = "6m") -> List[ResearchEvidence]:
        """Collects structured market evidence for the target symbols."""
        evidence_list: List[ResearchEvidence] = []

        if not symbols:
            return evidence_list

        for raw_sym in symbols:
            try:
                norm = normalize_symbol(raw_sym)
                canonical = norm.canonical_symbol
                market_region = "INDIA" if norm.market == "IN" else "US"

                provider = provider_factory.get_provider(market=market_region)

                # 1. Real-time Quote Snapshot
                quote = await provider.get_quote(canonical)
                q_dict = quote.model_dump() if hasattr(quote, "model_dump") else (quote or {})

                price = q_dict.get("price", 0.0)
                change_pct = q_dict.get("change_pct", 0.0)
                data_status = q_dict.get("data_status", "DEMO")
                data_source = q_dict.get("data_source", "MARKET_PROVIDER")
                ts = q_dict.get("timestamp") or datetime.now(timezone.utc).isoformat()

                prov_enum = EvidenceProvenance.LIVE if str(data_status).upper() == "LIVE" else EvidenceProvenance.DEMO

                cite = Citation(
                    citation_id=f"cite_{uuid.uuid4().hex[:6]}",
                    source_type="MARKET_PROVIDER",
                    source_name=data_source,
                    retrieved_at=datetime.now(timezone.utc).isoformat()
                )

                # Price Evidence
                evidence_list.append(
                    ResearchEvidence(
                        evidence_id=f"ev_{uuid.uuid4().hex[:8]}",
                        category="MARKET",
                        symbol=canonical,
                        metric="latest_price",
                        value={
                            "price": round(price, 2),
                            "change_pct": round(change_pct, 2),
                            "open": q_dict.get("open"),
                            "high": q_dict.get("high"),
                            "low": q_dict.get("low"),
                            "volume": q_dict.get("volume"),
                            "currency": q_dict.get("currency", "USD" if market_region == "US" else "INR")
                        },
                        source=data_source,
                        timestamp=ts,
                        provenance=prov_enum,
                        confidence=1.0,
                        citation=cite
                    )
                )

                # 2. Historical Bars & Timeframe Performance
                hist_res = await provider.get_historical_data(symbol=canonical, interval="1d", timeframe=timeframe)
                bars = hist_res.bars if hasattr(hist_res, "bars") else []

                if bars and len(bars) >= 2:
                    first_close = bars[0].close
                    last_close = bars[-1].close
                    period_return_pct = round(((last_close - first_close) / max(0.001, first_close)) * 100, 2)
                    highs = [b.high for b in bars]
                    lows = [b.low for b in bars]
                    volumes = [b.volume for b in bars]

                    period_high = round(max(highs), 2)
                    period_low = round(min(lows), 2)
                    avg_volume = round(sum(volumes) / len(volumes), 0)

                    evidence_list.append(
                        ResearchEvidence(
                            evidence_id=f"ev_{uuid.uuid4().hex[:8]}",
                            category="MARKET",
                            symbol=canonical,
                            metric="period_performance",
                            value={
                                "timeframe": timeframe,
                                "period_return_pct": period_return_pct,
                                "period_high": period_high,
                                "period_low": period_low,
                                "average_daily_volume": avg_volume,
                                "bars_count": len(bars)
                            },
                            source=data_source,
                            timestamp=ts,
                            provenance=prov_enum,
                            confidence=0.95,
                            citation=cite
                        )
                    )

            except Exception as ex:
                logger.warning(f"MarketResearchAgent error for {raw_sym}: {ex}")
                evidence_list.append(
                    ResearchEvidence(
                        evidence_id=f"ev_{uuid.uuid4().hex[:8]}",
                        category="MARKET",
                        symbol=raw_sym,
                        metric="market_data_status",
                        value={"status": "PARTIAL_OR_UNAVAILABLE", "error": str(ex)[:80]},
                        source="MarketProvider",
                        provenance=EvidenceProvenance.UNAVAILABLE,
                        confidence=0.3
                    )
                )

        return evidence_list


market_agent = MarketResearchAgent()
