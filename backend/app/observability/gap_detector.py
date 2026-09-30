"""
MarketMind AI — Market-Session Aware OHLCV Gap & Anomaly Detector.
Phase 6.8: Identifies missing trading bars, duplicate timestamps, inverted candle bounds,
and sequencing anomalies without falsely flagging weekends or market holidays.
"""
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime, timezone, timedelta
from app.providers.market_data.models import HistoricalCandle


class OHLCVGapDetector:
    """Detects gaps and invalid relationships in OHLCV time series data."""

    # Interval expected delta mapping
    INTERVAL_DELTAS = {
        "1m": timedelta(minutes=1),
        "5m": timedelta(minutes=5),
        "15m": timedelta(minutes=15),
        "30m": timedelta(minutes=30),
        "60m": timedelta(hours=1),
        "1h": timedelta(hours=1),
        "1d": timedelta(days=1),
    }

    @staticmethod
    def _parse_ts(ts: str) -> Optional[datetime]:
        try:
            clean = ts.replace("Z", "+00:00")
            if "T" in clean:
                dt = datetime.fromisoformat(clean)
            else:
                dt = datetime.strptime(clean[:19], "%Y-%m-%d %H:%M:%S")
            if dt.tzinfo is None:
                dt = dt.replace(tzinfo=timezone.utc)
            return dt
        except Exception:
            return None

    @classmethod
    def analyze_candles(
        cls,
        candles: List[HistoricalCandle],
        interval: str = "1d",
        exchange: str = "NSE"
    ) -> Dict[str, Any]:
        r"""
        Analyzes candle list for:
        1. Mathematical OHLC validity ($H \ge \max(O,C)$, $L \le \min(O,C)$, $V \ge 0$)
        2. Duplicate timestamps
        3. Unexpected timestamp gaps
        """
        if not candles:
            return {
                "total_candles": 0,
                "valid_count": 0,
                "invalid_candles": [],
                "duplicates_count": 0,
                "gaps_detected": [],
                "validity_score": 100.0,
                "continuity_score": 100.0
            }

        invalid_candles = []
        duplicates_count = 0
        gaps_detected = []
        seen_timestamps = set()

        # Sort candles chronologically
        sorted_candles = sorted(candles, key=lambda c: c.timestamp)

        for i, c in enumerate(sorted_candles):
            # 1. Mathematical Validation
            is_valid = True
            err_msg = ""
            if c.high < max(c.open, c.close) or c.low > min(c.open, c.close) or c.high < c.low:
                is_valid = False
                err_msg = f"Inverted OHLC bounds (O={c.open}, H={c.high}, L={c.low}, C={c.close})"
            elif c.open <= 0 or c.high <= 0 or c.low <= 0 or c.close <= 0:
                is_valid = False
                err_msg = "Non-positive price detected"
            elif c.volume < 0:
                is_valid = False
                err_msg = "Negative volume detected"

            if not is_valid:
                invalid_candles.append({"index": i, "timestamp": c.timestamp, "error": err_msg})

            # 2. Duplicate Detection
            if c.timestamp in seen_timestamps:
                duplicates_count += 1
            seen_timestamps.add(c.timestamp)

            # 3. Gap Detection (Chronological sequencing)
            if i > 0:
                prev_dt = cls._parse_ts(sorted_candles[i - 1].timestamp)
                curr_dt = cls._parse_ts(c.timestamp)

                if prev_dt and curr_dt:
                    diff = curr_dt - prev_dt
                    expected_delta = cls.INTERVAL_DELTAS.get(interval.lower(), timedelta(days=1))

                    if interval == "1d":
                        # For daily candles, skip weekend gap check (Friday to Monday = 3 days)
                        is_weekend_transition = prev_dt.weekday() == 4 and curr_dt.weekday() == 0 and diff <= timedelta(days=4)
                        if diff > timedelta(days=4) and not is_weekend_transition:
                            gaps_detected.append({
                                "from_timestamp": sorted_candles[i - 1].timestamp,
                                "to_timestamp": c.timestamp,
                                "gap_duration_hours": round(diff.total_seconds() / 3600, 1),
                                "severity": "WARNING" if diff.days <= 7 else "CRITICAL"
                            })
                    else:
                        # For intraday bars, flag if gap > 3x expected delta within same day
                        if diff > (expected_delta * 3) and prev_dt.date() == curr_dt.date():
                            gaps_detected.append({
                                "from_timestamp": sorted_candles[i - 1].timestamp,
                                "to_timestamp": c.timestamp,
                                "gap_duration_minutes": round(diff.total_seconds() / 60, 1),
                                "severity": "WARNING"
                            })

        total = len(candles)
        validity_score = max(0.0, 100.0 - (len(invalid_candles) / max(1, total) * 100.0))
        continuity_score = max(0.0, 100.0 - (len(gaps_detected) * 10.0) - (duplicates_count * 5.0))

        return {
            "total_candles": total,
            "valid_count": total - len(invalid_candles),
            "invalid_candles": invalid_candles,
            "duplicates_count": duplicates_count,
            "gaps_detected": gaps_detected,
            "validity_score": round(validity_score, 2),
            "continuity_score": round(continuity_score, 2)
        }


ohlcv_gap_detector = OHLCVGapDetector()
