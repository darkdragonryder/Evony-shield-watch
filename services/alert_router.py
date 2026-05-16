"""
Evony Shield Watch
Alert Router (FIXED COMPATIBILITY LAYER)
"""

from services.alert_dispatcher import AlertDispatcher


class NotificationRouter:

    def __init__(self, bot=None):

        self.bot = bot
        self.dispatcher = AlertDispatcher(bot=bot)

    # =====================================================
    # MAIN ROUTE
    # =====================================================

    async def send_alert(self, guild_id: int, message: str, **kwargs):

        guild = self.bot.get_guild(guild_id)
        if not guild:
            return {"sent": 0, "failed": 0}

        return await self.dispatcher.send_alert(
            guild,
            title=kwargs.get("title", "Alert"),
            message=message,
            min_role=kwargs.get("min_role", "member")
        )

    # =====================================================
    # WRAPPERS
    # =====================================================

    async def send_svs_alert(self, guild_id: int, message: str):

        return await self.send_alert(
            guild_id,
            message,
            title="⚔️ SVS ALERT"
        )

    async def send_ke_alert(self, guild_id: int, message: str):

        return await self.send_alert(
            guild_id,
            message,
            title="🔥 KE ALERT"
        )

    async def send_custom_alert(self, guild_id: int, message: str):

        return await self.send_alert(
            guild_id,
            message,
            title="📢 CUSTOM ALERT"
        )
