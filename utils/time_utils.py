"""
Timezone & Time Utilities
FULL RESET-ALIGNED SYSTEM (SVS / KE WEEK TOGGLE READY)
"""

import pytz
from datetime import datetime, timedelta

from config import Config


# =====================================================
# HOST RESET TIME (SOURCE OF TRUTH)
# =====================================================

def get_host_reset_time() -> datetime:
    """
    Returns next reset time in host timezone.
    Used as anchor for ALL event timing.
    """

    tz = pytz.timezone(Config.HOST_TIMEZONE)
    now = datetime.now(tz)

    reset = now.replace(
        hour=Config.RESET_HOUR,
        minute=Config.RESET_MINUTE,
        second=0,
        microsecond=0
    )

    if reset < now:
        reset += timedelta(days=1)

    return reset


# =====================================================
# TIMEZONE CONVERSION
# =====================================================

def convert_to_local_time(dt: datetime, user_timezone: str) -> datetime:

    if dt.tzinfo is None:
        dt = pytz.utc.localize(dt)

    return dt.astimezone(pytz.timezone(user_timezone))


# =====================================================
# USER RESET TIME
# =====================================================

def get_user_local_reset_time(user_timezone: str) -> datetime:
    return convert_to_local_time(
        get_host_reset_time(),
        user_timezone
    )


# =====================================================
# FORMAT DISPLAY TIME
# =====================================================

def format_local_time(dt: datetime) -> str:
    return dt.strftime("%A, %B %d at %I:%M %p %Z")


# =====================================================
# SVS TIMING (FIXED LOGIC)
# =====================================================
# RULES:
# - 1h 39m before reset → purge warning
# - 1h before reset → general warning
# - reset → SVS starts
# =====================================================

def get_svs_purge_time():
    return get_host_reset_time() - timedelta(hours=1, minutes=39)


def get_svs_warning_time():
    return get_host_reset_time() - timedelta(hours=1)


# =====================================================
# KE TIMING (FIXED LOGIC)
# =====================================================
# RULES:
# - 1h before reset → KE warning
# - reset → KE starts
# =====================================================

def get_ke_warning_time():
    return get_host_reset_time() - timedelta(hours=1)


# =====================================================
# WEEK TYPE HELPERS (OPTIONAL SAFE USE)
# =====================================================

def is_friday_reset_window() -> bool:
    """
    Used only if you ever need sanity checks.
    Not used for core logic anymore.
    """
    now = datetime.now(pytz.timezone(Config.HOST_TIMEZONE))
    return now.weekday() == 4  # Friday


def is_monday_reset_window() -> bool:
    now = datetime.now(pytz.timezone(Config.HOST_TIMEZONE))
    return now.weekday() == 0  # Monday
