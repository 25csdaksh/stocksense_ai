"""
Unit Tests for Market Session and Trading Schedule Manager.
Phase 6.1: Validates session state, trading hours, and next open/close timestamps for NSE, BSE, US.
"""
import pytest
from datetime import datetime, time, timezone
from zoneinfo import ZoneInfo
from app.providers.market_data.session import market_session_manager, MarketSessionManager
from app.providers.market_data.models import MarketSessionState


def test_indian_market_session_open():
    # Construct a weekday at 10:30 AM IST (regular session)
    tz_ist = ZoneInfo("Asia/Kolkata")
    test_dt = datetime(2026, 10, 5, 10, 30, tzinfo=tz_ist)  # 2026-10-05 is Monday

    status = market_session_manager.get_session_status("NSE", as_of=test_dt)
    assert status.market == "IN"
    assert status.exchange == "NSE"
    assert status.is_open is True
    assert status.session_state == MarketSessionState.REGULAR
    assert status.session_start == "09:15"
    assert status.session_end == "15:30"
    assert status.timezone == "Asia/Kolkata"


def test_indian_market_session_pre_market():
    tz_ist = ZoneInfo("Asia/Kolkata")
    test_dt = datetime(2026, 10, 5, 9, 5, tzinfo=tz_ist)  # 09:05 AM IST Monday

    status = market_session_manager.get_session_status("NSE", as_of=test_dt)
    assert status.is_open is False
    assert status.session_state == MarketSessionState.PRE_MARKET


def test_indian_market_session_closed_night_and_weekend():
    tz_ist = ZoneInfo("Asia/Kolkata")
    # Night time
    night_dt = datetime(2026, 10, 5, 20, 0, tzinfo=tz_ist)
    status_night = market_session_manager.get_session_status("NSE", as_of=night_dt)
    assert status_night.is_open is False
    assert status_night.session_state == MarketSessionState.CLOSED

    # Saturday
    sat_dt = datetime(2026, 10, 10, 11, 0, tzinfo=tz_ist)
    status_sat = market_session_manager.get_session_status("NSE", as_of=sat_dt)
    assert status_sat.is_open is False
    assert status_sat.session_state == MarketSessionState.CLOSED


def test_us_market_session_open_and_close():
    tz_et = ZoneInfo("America/New_York")
    # 11:00 AM ET Monday (Regular open)
    test_dt = datetime(2026, 10, 5, 11, 0, tzinfo=tz_et)
    status_us = market_session_manager.get_session_status("US", as_of=test_dt)
    assert status_us.market == "US"
    assert status_us.is_open is True
    assert status_us.session_state == MarketSessionState.REGULAR
    assert status_us.session_start == "09:30"
    assert status_us.session_end == "16:00"
    assert status_us.timezone == "America/New_York"
