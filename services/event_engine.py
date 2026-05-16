"""
=========================================================
 Evony Shield Watch
 Event Engine (SINGLE SOURCE OF TRUTH)
 FIXED SVS / KE WEEK CYCLE SYSTEM
=========================================================
"""

from datetime import datetime, timedelta
from config import Config
from database import db
import pytz


class EventEngine:
    """
    Controls the GLOBAL event cycle:
    - Friday reset → KE starts OR SVS starts (based on state)
    - Monday reset → no change (cycle continues)
    - Persistent DB state prevents desync
    """

    # =====================================================
    # GET CURRENT EVENT (SOURCE OF TRUTH)
    # =====================================================

    @staticmethod
    async def get_current_event(guild_id: int) -> str:
        data = await db.get_event_schedule(guild_id)

        if not data:
            return Config.SVS

        return data.get("current_event", Config.SVS)

    # =====================================================
    # FORCE SET EVENT (MANUAL OVERRIDE SAFE)
    # =====================================================

    @staticmethod
    async def set_event(guild_id: int, event: str):
        await db.set_event_schedule(
            guild_id=guild_id,
            current_event=event
        )

    # =====================================================
    # TOGGLE EVENT (CYCLE LOGIC)
    # =====================================================

    @staticmethod
    async def toggle_event(guild_id: int):

        current = await EventEngine.get_current_event(guild_id)

        new_event = Config.KE if current == Config.SVS else Config.SVS

        await EventEngine.set_event(guild_id, new_event)

        return new_event

    # =====================================================
    # GET NEXT RESET (FRIDAY ANCHOR SYSTEM)
    # =====================================================

    @staticmethod
    def get_next_reset():
        tz = pytz.timezone(Config.HOST_TIMEZONE)
        now = datetime.now(tz)

        # next Friday reset
        days_ahead = (4 - now.weekday()) % 7
        if days_ahead == 0:
            days_ahead = 7

        reset = now + timedelta(days=days_ahead)
        reset = reset.replace(
            hour=Config.RESET_HOUR,
            minute=Config.RESET_MINUTE,
            second=0,
            microsecond=0
        )

        return reset
