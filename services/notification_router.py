"""
=========================================================
 Evony Shield Watch
 Unified Notification Router (Discord + Telegram)
=========================================================
"""

from services.alert_dispatcher import AlertDispatcher
from services.telegram_service import TelegramService


class NotificationRouter:

    def __init__(self, discord_bot):

        self.discord = AlertDispatcher(discord_bot)
        self.telegram = TelegramService()

    # =====================================================
    # SEND SVS
    # =====================================================

    async def svs(self, guild, message):

        await self.discord.svs_alert(guild, message)

        # future: telegram broadcast here

    # =====================================================
    # SEND KE
    # =====================================================

    async def ke(self, guild, message):

        await self.discord.ke_alert(guild, message)

    # =====================================================
    # ADMIN MESSAGE
    # =====================================================

    async def admin(self, guild, message):

        await self.discord.admin_alert(guild, message)
