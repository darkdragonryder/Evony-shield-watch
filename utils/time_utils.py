"""
=========================================================
Evony Shield Watch
Timezone & Time Utilities
=========================================================
"""

# =========================================================
# IMPORTS
# =========================================================

import pytz

from datetime import datetime, timedelta

from config import Config


# =========================================================
# HOST RESET TIME
# =========================================================

def get_host_reset_time() -> datetime:
    """
    Returns the next server reset time
    in HOST_TIMEZONE.
    """

    tz = pytz.timezone(Config.HOST_TIMEZONE)

    now = datetime.now(tz)

    reset = now.replace(
        hour=Config.RESET_HOUR,
        minute=Config.RESET_MINUTE,
        second=0,
        microsecond=0
    )

    # -----------------------------------------------------
    # If reset already passed today
    # move to tomorrow
    # -----------------------------------------------------

    if reset <= now:
        reset += timedelta(days=1)

    return reset


# =========================================================
# CONVERT TIMEZONE
# =========================================================

def convert_to_local_time(
    dt: datetime,
    user_timezone: str
) -> datetime:
    """
    Converts datetime to user's timezone.
    """

    if dt.tzinfo is None:
        dt = pytz.utc.localize(dt)

    return dt.astimezone(
        pytz.timezone(user_timezone)
    )


# =========================================================
# USER RESET TIME
# =========================================================

def get_user_local_reset_time(
    user_timezone: str
) -> datetime:
    """
    Returns reset time converted
    into user's timezone.
    """

    return convert_to_local_time(
        get_host_reset_time(),
        user_timezone
    )


# =========================================================
# FORMAT LOCAL TIME
# =========================================================

def format_local_time(dt: datetime) -> str:
    """
    Pretty formatted local time string.
    """

    return dt.strftime(
        "%A, %B %d at %I:%M %p %Z"
    )


# =========================================================
# EVENT CALCULATIONS
# =========================================================

def get_svs_first_warning() -> datetime:
    """
    1h39m before reset.
    """

    return get_host_reset_time() - timedelta(
        hours=1,
        minutes=39
    )


def get_svs_purge_warning() -> datetime:
    """
    1 hour before reset.
    """

    return get_host_reset_time() - timedelta(
        hours=1
    )


def get_ke_warning() -> datetime:
    """
    1 hour before reset.
    """

    return get_host_reset_time() - timedelta(
        hours=1
    )


# =========================================================
# MONDAY CHECK
# =========================================================

def is_event_monday() -> bool:
    """
    Checks if today is Monday
    in host timezone.
    """

    tz = pytz.timezone(
        Config.HOST_TIMEZONE
    )

    return datetime.now(tz).weekday() == 0
