"""
MarketMind AI — Market Data Quality Assessment & OHLCV Gap Detection Service.
Phase 6.3: Transparent, non-financial data quality scoring (freshness, completeness, validation integrity)
and timeseries gap identification.
"""
from enum import Enum
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime, timezone, timedelta
from pydantic import BaseModel, Field

from app.providers.market_data.models import HistoricalCandle, NormalizedQuote, DataStatus
from app.providers.market_data.validator import MarketDataValidator
from app.core.logging import logger


class DataQualityStatus(str, Enum):
    """Data feed and storage quality classification."""
    HEALTHY = "HEALTHY"      # Fully validated, recent timestamps, zero gaps
    DEGRADED = "DEGRADED"    # Minor gaps or fallback to demo feed
    STALE = "STALE"          # Observation is older than expected session interval
    INVALID = "INVALID"      # Fails financial boundary constraints (e.g. negative prices, low > high)


class MarketDataQualityReport(BaseModel):
    """
    Comprehensive data quality inspection result for a financial asset or time-series.
    """
    symbol: str
    quality_status: DataQualityStatus
    freshness_seconds: Optional[float] = None
    is_stale: bool = False
    validation_passed: bool = True
    validation_error: Optional[str] = None
    provider_status: str = "LIVE"
    data_source: str = "MARKET_FEED"
    data_status: DataStatus = DataStatus.LIVE
    total_candles_checked: int = 0
    gaps_detected: List[Dict[str, Any]] = Field(default_factory=list)
    duplicate_count: int = 0
    last_observed_timestamp: Optional[str] = None
    quality_score: float = Field(default=100.0, description="Quality index (0-100) based strictly on data integrity")


class MarketQualityService:
    """Service providing data quality assessment, gap analysis, and provenance auditing."""

    # Maximum acceptable age for 'LIVE' quotes in seconds
    LIVE_STALENESS_THRESHOLD_SECONDS = 60.0
    DEMO_STALENESS_THRESHOLD_SECONDS = 300.0

    @classmethod
    def evaluate_quote_quality(
        cls,
        quote: NormalizedQuote,
        provider_status: str = "LIVE"
    ) -> MarketDataQualityReport:
        """
        Assesses real-time quote freshness, mathematical integrity, and provenance.
        """
        # 1. Check Financial Boundaries
        is_valid, err_reason = MarketDataValidator.validate_quote(quote)
        if not is_valid:
            return MarketDataQualityReport(
                symbol=quote.symbol,
                quality_status=DataQualityStatus.INVALID,
                validation_passed=False,
                validation_error=err_reason,
                provider_status=provider_status,
                data_source=quote.data_source,
                data_status=quote.data_status,
                last_observed_timestamp=quote.timestamp,
                quality_score=0.0
            )

        # 2. Check Freshness
        now_dt = datetime.now(timezone.utc)
        freshness_sec = None
        is_stale = False
        try:
            ts_str = quote.timestamp.replace("Z", "+00:00")
            quote_dt = datetime.fromisoformat(ts_str)
            if quote_dt.tzinfo is None:
                quote_dt = quote_dt.replace(tzinfo=timezone.utc)
            freshness_sec = max(0.0, (now_dt - quote_dt).total_seconds())
            threshold = (
                cls.LIVE_STALENESS_THRESHOLD_SECONDS
                if quote.data_status == DataStatus.LIVE
                else cls.DEMO_STALENESS_THRESHOLD_SECONDS
            )
            is_stale = freshness_sec > threshold
        except Exception:
            pass

        # 3. Derive Overall Status
        if quote.data_status == DataStatus.DEMO or quote.data_status == DataStatus.MODEL_DERIVED:
            status = DataQualityStatus.DEGRADED
            score = 80.0
        elif is_stale:
            status = DataQualityStatus.STALE
            score = 60.0
        else:
            status = DataQualityStatus.HEALTHY
            score = 100.0

        return MarketDataQualityReport(
            symbol=quote.symbol,
            quality_status=status,
            freshness_seconds=round(freshness_sec, 2) if freshness_sec is not None else None,
            is_stale=is_stale,
            validation_passed=True,
            provider_status=provider_status,
            data_source=quote.data_source,
            data_status=quote.data_status,
            last_observed_timestamp=quote.timestamp,
            quality_score=score
        )

    @classmethod
    def detect_ohlcv_gaps(
        cls,
        candles: List[HistoricalCandle],
        interval: str = "1d"
    ) -> Tuple[List[Dict[str, Any]], int]:
        """
        Scans a chronological list of candles for:
        1. Duplicate timestamps
        2. Time gaps exceeding normal interval expectations (skipping weekend gaps for daily data)
        Returns (gaps_list, duplicate_count).
        """
        if not candles or len(candles) < 2:
            return [], 0

        # Sort candles chronologically
        sorted_candles = sorted(
            candles,
            key=lambda c: c.timestamp if isinstance(c.timestamp, datetime) else str(c.timestamp)
        )

        gaps: List[Dict[str, Any]] = []
        duplicate_count = 0
        seen_timestamps = set()

        interval_delta_map = {
            "1m": timedelta(minutes=1),
            "5m": timedelta(minutes=5),
            "15m": timedelta(minutes=15),
            "30m": timedelta(minutes=30),
            "60m": timedelta(hours=1),
            "1h": timedelta(hours=1),
            "1d": timedelta(days=1),
            "day": timedelta(days=1),
        }
        expected_step = interval_delta_map.get(interval.lower(), timedelta(days=1))
        # Allow tolerance (e.g. weekends 3 days for daily data)
        max_allowed_gap = expected_step * 3.5 if "d" in interval.lower() else expected_step * 5

        for i in range(len(sorted_candles)):
            curr = sorted_candles[i]
            curr_ts = curr.timestamp
            if isinstance(curr_ts, str):
                try:
                    curr_dt = datetime.fromisoformat(curr_ts.replace("Z", "+00:00"))
                except Exception:
                    curr_dt = None
            else:
                curr_dt = curr_ts

            if curr_dt:
                if curr_dt in seen_timestamps:
                    duplicate_count += 1
                seen_timestamps.add(curr_dt)

            if i > 0 and curr_dt:
                prev = sorted_candles[i - 1]
                prev_ts = prev.timestamp
                if isinstance(prev_ts, str):
                    try:
                        prev_dt = datetime.fromisoformat(prev_ts.replace("Z", "+00:00"))
                    except Exception:
                        prev_dt = None
                else:
                    prev_dt = prev_ts

                if prev_dt and curr_dt:
                    diff = curr_dt - prev_dt
                    if diff > max_allowed_gap:
                        gaps.append({
                            "from_timestamp": prev_dt.isoformat(),
                            "to_timestamp": curr_dt.isoformat(),
                            "gap_duration_hours": round(diff.total_seconds() / 3600.0, 2),
                            "severity": "HIGH" if diff.total_seconds() > 86400 * 5 else "MEDIUM"
                        })

        return gaps, duplicate_count

    @classmethod
    def evaluate_timeseries_quality(
        cls,
        symbol: str,
        candles: List[HistoricalCandle],
        interval: str = "1d",
        data_source: str = "HISTORICAL_FEED"
    ) -> MarketDataQualityReport:
        """
        Evaluates the completeness, gap frequency, and OHLC validity of a historical timeseries.
        """
        if not candles:
            return MarketDataQualityReport(
                symbol=symbol,
                quality_status=DataQualityStatus.INVALID,
                validation_passed=False,
                validation_error="Empty candle dataset.",
                data_source=data_source,
                total_candles_checked=0,
                quality_score=0.0
            )

        # 1. Validate every candle
        invalid_count = 0
        first_err = None
        for c in candles:
            is_valid, err = MarketDataValidator.validate_candle(c)
            if not is_valid:
                invalid_count += 1
                if not first_err:
                    first_err = err

        # 2. Check Gaps & Duplicates
        gaps, dup_count = cls.detect_ohlcv_gaps(candles, interval=interval)

        # 3. Compute Score
        total = len(candles)
        valid_ratio = (total - invalid_count) / max(1, total)
        gap_penalty = min(30.0, len(gaps) * 5.0)
        dup_penalty = min(20.0, dup_count * 2.0)
        score = max(0.0, (valid_ratio * 100.0) - gap_penalty - dup_penalty)

        if invalid_count > (total * 0.1):
            status = DataQualityStatus.INVALID
        elif len(gaps) > 3 or dup_count > 5:
            status = DataQualityStatus.DEGRADED
        else:
            status = DataQualityStatus.HEALTHY

        latest_ts = str(candles[-1].timestamp) if candles else None

        return MarketDataQualityReport(
            symbol=symbol,
            quality_status=status,
            validation_passed=(invalid_count == 0),
            validation_error=first_err,
            data_source=data_source,
            total_candles_checked=total,
            gaps_detected=gaps,
            duplicate_count=dup_count,
            last_observed_timestamp=latest_ts,
            quality_score=round(score, 2)
        )


market_quality_service = MarketQualityService()
