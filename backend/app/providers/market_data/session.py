"""
MarketMind AI — Market Session & Trading Schedule Management.
Supports Indian (NSE/BSE) and US (NYSE/NASDAQ) market hours, timezones, and session states.
"""
from datetime import datetime, time, timedelta, timezone
from zoneinfo import ZoneInfo
from typing import Optional, Dict, Any
from app.providers.market_data.models import MarketSessionStatus, MarketSessionState


class MarketSessionManager:
    """Calculates real-time market session status for Indian and US exchanges."""

    # Timezone mappings
    TIMEZONES = {
        "NSE": "Asia/Kolkata",
        "BSE": "Asia/Kolkata",
        "IN": "Asia/Kolkata",
        "INDIAN": "Asia/Kolkata",
        "NASDAQ": "America/New_York",
        "NYSE": "America/New_York",
        "US": "America/New_York",
        "GLOBAL": "America/New_York",
    }

    # Trading Schedules in Local Market Time (24-hour format)
    SCHEDULES = {
        "IN": {
            "pre_open": time(9, 0),
            "regular_open": time(9, 15),
            "regular_close": time(15, 30),
            "post_close": time(16, 0),
            "exchange": "NSE",
            "market": "IN",
            "timezone": "Asia/Kolkata",
        },
        "US": {
            "pre_open": time(4, 0),
            "regular_open": time(9, 30),
            "regular_close": time(16, 0),
            "post_close": time(20, 0),
            "exchange": "NASDAQ",
            "market": "US",
            "timezone": "America/New_York",
        }
    }

    @classmethod
    def get_session_status(
        cls,
        market_or_exchange: str = "IN",
        as_of: Optional[datetime] = None
    ) -> MarketSessionStatus:
        """
        Determines current session state (REGULAR, PRE_MARKET, POST_MARKET, CLOSED),
        next open, and next close for the specified market or exchange.
        """
        code = market_or_exchange.strip().upper()
        if code in ["NSE", "BSE", "IN", "INDIAN"]:
            schedule = cls.SCHEDULES["IN"]
            exchange_name = "NSE" if code != "BSE" else "BSE"
            market_name = "IN"
        else:
            schedule = cls.SCHEDULES["US"]
            exchange_name = "NASDAQ" if code != "NYSE" else "NYSE"
            market_name = "US"

        tz = ZoneInfo(schedule["timezone"])

        if as_of is None:
            now_utc = datetime.now(timezone.utc)
            now_local = now_utc.astimezone(tz)
        else:
            if as_of.tzinfo is None:
                as_of = as_of.replace(tzinfo=timezone.utc)
            now_local = as_of.astimezone(tz)

        weekday = now_local.weekday()  # 0=Monday, 6=Sunday
        current_time = now_local.time()

        is_weekend = weekday >= 5

        # Determine session state
        if is_weekend:
            session_state = MarketSessionState.CLOSED
            is_open = False
        elif schedule["regular_open"] <= current_time < schedule["regular_close"]:
            session_state = MarketSessionState.REGULAR
            is_open = True
        elif schedule["pre_open"] <= current_time < schedule["regular_open"]:
            session_state = MarketSessionState.PRE_MARKET
            is_open = False
        elif schedule["regular_close"] <= current_time < schedule["post_close"]:
            session_state = MarketSessionState.POST_MARKET
            is_open = False
        else:
            session_state = MarketSessionState.CLOSED
            is_open = False

        # Calculate next open timestamp (in UTC)
        next_open_local = cls._calculate_next_open(now_local, schedule)
        next_close_local = cls._calculate_next_close(now_local, schedule)

        return MarketSessionStatus(
            market=market_name,
            exchange=exchange_name,
            is_open=is_open,
            session_state=session_state,
            session_start=schedule["regular_open"].strftime("%H:%M"),
            session_end=schedule["regular_close"].strftime("%H:%M"),
            timezone=schedule["timezone"],
            current_time_local=now_local.strftime("%Y-%m-%d %H:%M:%S %Z"),
            next_open=next_open_local.astimezone(timezone.utc).isoformat(),
            next_close=next_close_local.astimezone(timezone.utc).isoformat(),
        )

    @classmethod
    def _calculate_next_open(cls, now_local: datetime, schedule: Dict[str, Any]) -> datetime:
        """Finds the next upcoming regular market open datetime."""
        target_date = now_local.date()
        open_time = schedule["regular_open"]

        if now_local.weekday() < 5 and now_local.time() < open_time:
            # Opens later today
            target_dt = datetime.combine(target_date, open_time, tzinfo=now_local.tzinfo)
        else:
            # Opens on next weekday
            days_ahead = 1
            next_day = target_date + timedelta(days=days_ahead)
            while next_day.weekday() >= 5:  # Skip Saturday & Sunday
                days_ahead += 1
                next_day = target_date + timedelta(days=days_ahead)
            target_dt = datetime.combine(next_day, open_time, tzinfo=now_local.tzinfo)

        return target_dt

    @classmethod
    def _calculate_next_close(cls, now_local: datetime, schedule: Dict[str, Any]) -> datetime:
        """Finds the next upcoming regular market close datetime."""
        target_date = now_local.date()
        close_time = schedule["regular_close"]

        if now_local.weekday() < 5 and now_local.time() < close_time:
            # Closes later today
            target_dt = datetime.combine(target_date, close_time, tzinfo=now_local.tzinfo)
        else:
            # Closes on next open weekday
            days_ahead = 1
            next_day = target_date + timedelta(days=days_ahead)
            while next_day.weekday() >= 5:
                days_ahead += 1
                next_day = target_date + timedelta(days=days_ahead)
            target_dt = datetime.combine(next_day, close_time, tzinfo=now_local.tzinfo)

        return target_dt

    @classmethod
    def is_market_open(cls, market_or_exchange: str) -> bool:
        """Convenience boolean check for whether a given market is in regular trading session."""
        return cls.get_session_status(market_or_exchange).is_open


market_session_manager = MarketSessionManager()
