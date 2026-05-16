"""
=========================================================
Evony Shield Watch
Event Engine (SINGLE SOURCE OF TRUTH)
FIXED SVS / KE GLOBAL CYCLE
=========================================================
"""

from datetime import datetime, timedelta
import pytz

from database import db
from config import Config


class EventEngine:

    # =====================================================
    # CORE RULE:
    # FIXED GLOBAL CYCLE
    # =====================================================
    # Friday reset → KE STARTS
    # Sat → KE
    # Sun → KE
    # Mon → KE until reset
    # Next Friday reset → SVS starts
    # =====================================================

    KE_DAYS = {4, 5, 6, 0}  # Fri, Sat, Sun, Mon (Mon = 0 if week wraps in your system handling)
    SVS_DAYS = {1, 2, 3}    # Tue, Wed, Thu

    # =====================================================
    # GET CURRENT EVENT (GLOBAL TRUTH)
    # =====================================================

    @staticmethod
    async def get_current_event(guild_id: int) -> str:

        schedule = await db.get_event_schedule(guild_id)

        if not schedule:
            return "ke"  # default safe state

        return schedule.get("current_event", "ke")

    # =====================================================
    # DETERMINE EVENT FROM TIME (NO STATE DRIFT)
    # =====================================================

    @staticmethod
    def get_event_from_time(now: datetime = None) -> str:

        tz = pytz.timezone(Config.HOST_TIMEZONE)
        now = now or datetime.now(tz)

        weekday = now.weekday()

        # FIXED RULE SET
        if weekday in EventEngine.KE_DAYS:
            return "ke"

        return "svs"

    # =====================================================
    # SYNC DB STATE (CALLED ON STARTUP / DAILY)
    # =====================================================

    @staticmethod
    async def sync_guild_state(guild_id: int):

        current = EventEngine.get_event_from_time()

        await db.set_event_schedule(
            guild_id=guild_id,
            current_event=current
        )

        return current

    # =====================================================
    # NEXT EVENT PREDICTION
    # =====================================================

    @staticmethod
    def get_next_event(now: datetime = None) -> str:

        current = EventEngine.get_event_from_time(now)

        return "svs" if current == "ke" else "ke"

    # =====================================================
    # PURGE LOGIC (SVS ONLY)
    # =====================================================

    @staticmethod
    def is_svs_purge_time(now: datetime = None) -> bool:

        tz = pytz.timezone(Config.HOST_TIMEZONE)
        now = now or datetime.now(tz)

        # Example rule: 1h39 before reset
        reset = now.replace(
            hour=Config.RESET_HOUR,
            minute=Config.RESET_MINUTE,
            second=0,
            microsecond=0
        )

        if reset < now:
            reset += timedelta(days=1)

        return now >= (reset - timedelta(hours=1, minutes=39)) and now < (reset - timedelta(hours=1))

    # =====================================================
    # GENERAL WARNING WINDOW
    # =====================================================

    @staticmethod
    def is_warning_time(now: datetime = None) -> bool:

        tz = pytz.timezone(Config.HOST_TIMEZONE)
        now = now or datetime.now(tz)

        reset = now.replace(
            hour=Config.RESET_HOUR,
            minute=Config.RESET_MINUTE,
            second=0,
            microsecond=0
        )

        if reset < now:
            reset += timedelta(days=1)

        return now >= (reset - timedelta(hours=1)) and now < reset

    # =====================================================
    # RESET DETECTION
    # =====================================================

    @staticmethod
    def is_reset_time(now: datetime = None) -> bool:

        tz = pytz.timezone(Config.HOST_TIMEZONE)
        now = now or datetime.now(tz)

        return (
            now.hour == Config.RESET_HOUR and
            now.minute == Config.RESET_MINUTE
        )
