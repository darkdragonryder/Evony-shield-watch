"""
=========================================================
Evony Shield Watch
ALERT ROUTER (COMPATIBILITY LAYER)
- Bridges event engine → dispatcher
- Prevents broken imports during rebuild
=========================================================
"""

from services.alert_dispatcher import AlertDispatcher


class NotificationRouter:
    """
    Thin routing layer so main.py / event engine
    never depends directly on dispatcher internals.
    """

    def __init__(self, bot=None, db=None):
        self.bot = bot
        self.db = db
        self.dispatcher = AlertDispatcher(bot=bot, db=db)

    # =====================================================
    # MAIN ROUTE ENTRYPOINT
    # =====================================================

    async def send_alert(self, guild_id: int, message: str, **kwargs):
        """
        Generic alert router entrypoint.

        Everything (SVS, KE, custom events, reminders)
        flows through here.
        """

        return await self.dispatcher.send_alert(
            guild_id=guild_id,
            message=message,
            **kwargs
        )

    # =====================================================
    # EVENT SPECIFIC HELPERS (SAFE WRAPPERS)
    # =====================================================

    async def send_svs_alert(self, guild_id: int, message: str):
        return await self.send_alert(
            guild_id=guild_id,
            message=message,
            event_type="svs"
        )

    async def send_ke_alert(self, guild_id: int, message: str):
        return await self.send_alert(
            guild_id=guild_id,
            message=message,
            event_type="ke"
        )

    async def send_custom_alert(self, guild_id: int, message: str):
        return await self.send_alert(
            guild_id=guild_id,
            message=message,
            event_type="custom"
        )
