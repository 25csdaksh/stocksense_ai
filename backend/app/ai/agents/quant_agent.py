"""
MarketMind AI — Quantitative & Technical Specialist Agent.
Phase 6.9: Computes standardized technical indicators (RSI, MACD, SMA/EMA, Bollinger Bands, ATR)
and provides evidence-based quantitative interpretations without guaranteed price predictions.
"""
import uuid
import pandas as pd
from typing import List, Dict, Any, Optional
from datetime import datetime, timezone

from app.ai.models import (
    ResearchEvidence,
    EvidenceProvenance,
    Citation,
)
from app.providers.market_data.factory import provider_factory
from app.providers.market_data.symbol_normalizer import normalize_symbol
from app.analytics.technical import (
    calculate_sma,
    calculate_ema,
    calculate_rsi,
    calculate_macd,
    calculate_bollinger_bands,
    calculate_atr,
    calculate_realized_volatility,
)
from app.core.logging import logger


class QuantTechnicalAgent:
    """Specialist agent calculating deterministic technical indicators and momentum statistics."""

    async def run(self, symbols: List[str], timeframe: str = "6m") -> List[ResearchEvidence]:
        """Calculates structured quantitative evidence for the target symbols."""
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

                df_bars = [b.model_dump() if hasattr(b, "model_dump") else b for b in bars]
                df = pd.DataFrame(df_bars)
                closes = df["close"].astype(float)
                highs = df["high"].astype(float)
                lows = df["low"].astype(float)
                latest_close = float(closes.iloc[-1])

                # 1. Moving Averages
                sma20_series = calculate_sma(closes, window=20)
                sma50_series = calculate_sma(closes, window=min(50, len(closes)))
                ema12_series = calculate_ema(closes, window=12)
                ema26_series = calculate_ema(closes, window=min(26, len(closes)))

                sma20 = float(sma20_series.iloc[-1]) if not sma20_series.empty else None
                sma50 = float(sma50_series.iloc[-1]) if not sma50_series.empty else None
                ema12 = float(ema12_series.iloc[-1]) if not ema12_series.empty else None
                ema26 = float(ema26_series.iloc[-1]) if not ema26_series.empty else None

                trend_status = "BULLISH_TREND" if latest_close > (sma50 or latest_close) else "BEARISH_OR_CONSOLIDATING"

                evidence_list.append(
                    ResearchEvidence(
                        evidence_id=f"ev_{uuid.uuid4().hex[:8]}",
                        category="TECHNICAL",
                        symbol=canonical,
                        metric="trend_and_moving_averages",
                        value={
                            "latest_close": round(latest_close, 2),
                            "sma_20": round(sma20, 2) if sma20 else None,
                            "sma_50": round(sma50, 2) if sma50 else None,
                            "ema_12": round(ema12, 2) if ema12 else None,
                            "ema_26": round(ema26, 2) if ema26 else None,
                            "trend_regime": trend_status,
                            "price_vs_sma50_pct": round(((latest_close - sma50) / sma50) * 100, 2) if sma50 else 0.0
                        },
                        source="TechnicalAnalyticsEngine",
                        provenance=EvidenceProvenance.CALCULATED,
                        confidence=0.98
                    )
                )

                # 2. Momentum & Oscillators (RSI & MACD)
                rsi_series = calculate_rsi(closes, window=14)
                rsi_val = float(rsi_series.iloc[-1]) if not rsi_series.empty else 50.0

                macd_res = calculate_macd(closes)
                macd_line = float(macd_res["macd_line"].iloc[-1]) if not macd_res["macd_line"].empty else 0.0
                macd_signal = float(macd_res["signal_line"].iloc[-1]) if not macd_res["signal_line"].empty else 0.0
                macd_hist = float(macd_res["histogram"].iloc[-1]) if not macd_res["histogram"].empty else 0.0

                rsi_interpretation = (
                    "Overbought territory (>70)" if (rsi_val or 50) > 70
                    else "Oversold territory (<30)" if (rsi_val or 50) < 30
                    else "Neutral momentum band (30-70)"
                )

                evidence_list.append(
                    ResearchEvidence(
                        evidence_id=f"ev_{uuid.uuid4().hex[:8]}",
                        category="TECHNICAL",
                        symbol=canonical,
                        metric="momentum_oscillators",
                        value={
                            "rsi_14": round(rsi_val, 2),
                            "rsi_interpretation": rsi_interpretation,
                            "macd_line": round(macd_line, 2),
                            "macd_signal": round(macd_signal, 2),
                            "macd_histogram": round(macd_hist, 2),
                        },
                        source="TechnicalAnalyticsEngine",
                        provenance=EvidenceProvenance.CALCULATED,
                        confidence=0.95
                    )
                )

                # 3. Volatility & Bands (Bollinger & ATR)
                bb_res = calculate_bollinger_bands(closes, window=20, num_std=2.0)
                bb_upper = float(bb_res["upper"].iloc[-1]) if not bb_res["upper"].empty else None
                bb_middle = float(bb_res["middle"].iloc[-1]) if not bb_res["middle"].empty else None
                bb_lower = float(bb_res["lower"].iloc[-1]) if not bb_res["lower"].empty else None

                atr_series = calculate_atr(highs, lows, closes, window=14)
                atr_val = float(atr_series.iloc[-1]) if not atr_series.empty else None

                hist_vol_series = calculate_realized_volatility(closes, window=20)
                hist_vol = float(hist_vol_series.iloc[-1]) if not hist_vol_series.empty else 20.0

                evidence_list.append(
                    ResearchEvidence(
                        evidence_id=f"ev_{uuid.uuid4().hex[:8]}",
                        category="TECHNICAL",
                        symbol=canonical,
                        metric="volatility_and_bands",
                        value={
                            "bollinger_upper": round(bb_upper, 2) if bb_upper else None,
                            "bollinger_middle": round(bb_middle, 2) if bb_middle else None,
                            "bollinger_lower": round(bb_lower, 2) if bb_lower else None,
                            "atr_14": round(atr_val, 2) if atr_val else None,
                            "annualized_volatility_pct": round(hist_vol, 2),
                        },
                        source="TechnicalAnalyticsEngine",
                        provenance=EvidenceProvenance.CALCULATED,
                        confidence=0.95
                    )
                )

            except Exception as ex:
                logger.warning(f"QuantTechnicalAgent error for {raw_sym}: {ex}")

        return evidence_list


quant_agent = QuantTechnicalAgent()
