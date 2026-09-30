"""
MarketMind AI — Central Data Freshness & Staleness Evaluator.
Phase 6.8: Domain-specific SLA thresholds for real-time quotes, timeseries OHLCV,
corporate fundamentals, breaking news feeds, and index benchmarks.
"""
from typing import Dict, Any, Optional, Tuple
from datetime import datetime, timezone, timedelta


class DataFreshnessService:
    """Evaluates data freshness and assigns SLA-based freshness scores."""

    # SLA Thresholds in seconds
    SLA_THRESHOLDS = {
        "quotes": {"live": 60.0, "demo": 300.0, "stale_cutoff": 900.0},
        "indices": {"live": 60.0, "demo": 300.0, "stale_cutoff": 900.0},
        "ohlcv_intraday": {"live": 300.0, "demo": 900.0, "stale_cutoff": 3600.0},
        "ohlcv_daily": {"live": 86400.0 * 3, "demo": 86400.0 * 5, "stale_cutoff": 86400.0 * 10}, # 3-5 days accounts for weekends
        "fundamentals": {"live": 86400.0 * 95, "demo": 86400.0 * 120, "stale_cutoff": 86400.0 * 180}, # ~90-120 days for quarterly
        "news": {"live": 3600.0, "demo": 86400.0 * 2, "stale_cutoff": 86400.0 * 7}, # 1 hour for breaking, 2 days for demo
    }

    @classmethod
    def evaluate_freshness(
        cls,
        dataset: str,
        timestamp_str: Optional[str],
        data_status: str = "DEMO",
        interval: Optional[str] = None
    ) -> Tuple[bool, Optional[float], float]:
        """
        Evaluates freshness of a dataset observation.
        Returns: (is_stale, freshness_seconds, freshness_score_0_to_100)
        """
        if not timestamp_str:
            return True, None, 30.0

        now_utc = datetime.now(timezone.utc)
        obs_dt = None

        # Parse timestamp formats
        try:
            clean_ts = timestamp_str.replace("Z", "+00:00")
            if "UTC" in clean_ts:
                clean_ts = clean_ts.replace(" UTC", "")
                obs_dt = datetime.strptime(clean_ts, "%Y-%m-%d %H:%M:%S").replace(tzinfo=timezone.utc)
            elif "T" in clean_ts:
                obs_dt = datetime.fromisoformat(clean_ts)
                if obs_dt.tzinfo is None:
                    obs_dt = obs_dt.replace(tzinfo=timezone.utc)
            else:
                obs_dt = datetime.strptime(clean_ts[:10], "%Y-%m-%d").replace(tzinfo=timezone.utc)
        except Exception:
            return True, None, 40.0

        age_seconds = max(0.0, (now_utc - obs_dt).total_seconds())

        # Select dataset thresholds
        target_dataset = dataset.lower()
        if target_dataset == "ohlcv":
            target_dataset = "ohlcv_daily" if interval == "1d" else "ohlcv_intraday"

        sla = cls.SLA_THRESHOLDS.get(target_dataset, cls.SLA_THRESHOLDS["quotes"])
        status_key = "live" if data_status.upper() == "LIVE" else "demo"
        threshold = sla.get(status_key, 300.0)
        stale_cutoff = sla.get("stale_cutoff", threshold * 3)

        is_stale = age_seconds > threshold

        if age_seconds <= threshold:
            # Full freshness score
            score = 100.0
        elif age_seconds <= stale_cutoff:
            # Linear decay from 100 down to 50
            decay = (age_seconds - threshold) / max(1.0, stale_cutoff - threshold)
            score = max(50.0, 100.0 - (decay * 50.0))
        else:
            # Degraded stale score
            score = max(20.0, 50.0 - ((age_seconds - stale_cutoff) / max(1.0, stale_cutoff) * 30.0))

        return is_stale, round(age_seconds, 2), round(score, 2)


freshness_service = DataFreshnessService()
