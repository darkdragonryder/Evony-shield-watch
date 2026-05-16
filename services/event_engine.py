"""
 Evony Shield Watch
 Event Engine (SINGLE SOURCE OF TRUTH)
 NO SCHEDULER LOGIC — PURE STATE ENGINE ONLY

"""

from database import db
from config import Config


class EventEngine:

    # =====================================================
    # GET CURRENT EVENT (SAFE FALLBACK)
    # =====================================================

    @staticmethod
    async def get_current_event(guild_id: int) -> str:

        schedule = await db.get_event_schedule(guild_id)

        if not schedule:
            # Default safe state for new servers
            return Config.SVS

        return schedule.get("current_event") or Config.SVS

    # =====================================================
    # GET NEXT EVENT (PURE RULE)
    # =====================================================

    @staticmethod
    async def get_next_event(guild_id: int) -> str:

        current = await EventEngine.get_current_event(guild_id)

        return Config.KE if current == Config.SVS else Config.SVS

    # =====================================================
    # TOGGLE EVENT (STATE TRANSITION ONLY)
    # =====================================================

    @staticmethod
    async def toggle_event(guild_id: int) -> str:

        next_event = await EventEngine.get_next_event(guild_id)

        await db.set_event_schedule(
            guild_id=guild_id,
            current_event=next_event
        )

        return next_event

    # =====================================================
    # ENSURE SERVER INITIAL STATE
    # =====================================================

    @staticmethod
    async def ensure_guild_state(guild_id: int):

        schedule = await db.get_event_schedule(guild_id)

        if schedule:
            return

        # First-time install defaults
        await db.set_event_schedule(
            guild_id=guild_id,
            current_event=Config.SVS,
            next_event_date=None
        )

    # =====================================================
    # FORCE SET EVENT (MANUAL OVERRIDE SAFETY TOOL)
    # =====================================================

    @staticmethod
    async def force_set_event(guild_id: int, event: str):

        event = event.lower()

        if event not in [Config.SVS, Config.KE]:
            raise ValueError("Invalid event type")

        await db.set_event_schedule(
            guild_id=guild_id,
            current_event=event
        )

        return event
