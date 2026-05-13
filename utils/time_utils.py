"""
Timezone & Time Utilities
"""
import pytz
from datetime import datetime, timedelta
from config import Config

def get_host_reset_time() -> datetime:
    tz = pytz.timezone(Config.HOST_TIMEZONE)
    now = datetime.now(tz)
    reset = now.replace(hour=Config.RESET_HOUR, minute=Config.RESET_MINUTE,
                        second=0, microsecond=0)
    if reset < now:
        reset += timedelta(days=1)
    return reset

def convert_to_local_time(dt: datetime, user_timezone: str) -> datetime:
    if dt.tzinfo is None:
        dt = pytz.utc.localize(dt)
    return dt.astimezone(pytz.timezone(user_timezone))

def get_user_local_reset_time(user_timezone: str) -> datetime:
    return convert_to_local_time(get_host_reset_time(), user_timezone)

def format_local_time(dt: datetime) -> str:
    return dt.strftime("%A, %B %d at %I:%M %p %Z")

def get_svs_reminder_times():
    reset = get_host_reset_time()
    first = reset - Config.SVS_FIRST_REMINDER
    second = reset - Config.SVS_SECOND_REMINDER
    purge = reset - Config.SVS_PURGE_OFFSET
    return first, second, purge

def get_ke_reminder_time():
    return get_host_reset_time() - Config.KE_REMINDER

def is_event_monday():
    return datetime.now(pytz.timezone(Config.HOST_TIMEZONE)).weekday() == Config.EVENT_END_DAY
