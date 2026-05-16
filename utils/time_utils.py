"""
Timezone & Time Utilities
Stable + fallback-safe + Evony Shield Watch aligned
"""

import pytz
from datetime import datetime, timedelta
from config import Config


# =====================================================
# HOST RESET (SOURCE OF TRUTH)
# =====================================================

def get_host_reset_time() -> datetime:
    tz = pytz.timezone(Config.HOST_TIMEZONE)
    now = datetime.now(tz)

    reset = now.replace(
        hour=Config.RESET_HOUR,
        minute=Config.RESET_MINUTE,
        second=0,
        microsecond=0
    )

    if reset <= now:
        reset += timedelta(days=1)

    return reset


# =====================================================
# SAFE TIMEZONE CONVERSION
# =====================================================

def convert_to_local_time(dt: datetime, user_timezone: str) -> datetime:

    try:
        tz = pytz.timezone(user_timezone or "UTC")
    except Exception:
        tz = pytz.timezone("UTC")

    if dt.tzinfo is None:
        dt = pytz.utc.localize(dt)

    return dt.astimezone(tz)


# =====================================================
# USER RESET TIME
# =====================================================

def get_user_local_reset_time(user_timezone: str) -> datetime:
    return convert_to_local_time(get_host_reset_time(), user_timezone)


# =====================================================
# FORMATTER (HUMAN READABLE)
# =====================================================

def format_local_time(dt: datetime) -> str:
    return dt.strftime("%A, %d %B %Y • %I:%M %p (%Z)")


# =====================================================
# SVS TIMERS
# =====================================================

def get_svs_purge_time():
    return get_host_reset_time() - timedelta(hours=1, minutes=39)


def get_svs_warning_time():
    return get_host_reset_time() - timedelta(hours=1)


# =====================================================
# KE TIMERS
# =====================================================

def get_ke_warning_time():
    return get_host_reset_time() - timedelta(hours=1)


# =====================================================
# SAFE HELPERS
# =====================================================

def is_friday_reset_window() -> bool:
    now = datetime.now(pytz.timezone(Config.HOST_TIMEZONE))
    return now.weekday() == 4


def is_monday_reset_window() -> bool:
    now = datetime.now(pytz.timezone(Config.HOST_TIMEZONE))
    return now.weekday() == 0
