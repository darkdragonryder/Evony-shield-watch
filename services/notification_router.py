"""
Evony Shield Watch
Unified Notification Router (Discord + Telegram)
Fixed + Fully Routed + Safe Architecture
"""

from services.alert_dispatcher import AlertDispatcher
from database import db


class NotificationRouter:

    def __init__(self, discord_bot):

        self.discord = AlertDispatcher(discord_bot)

        # telegram intentionally optional (not blocking system)
        self.telegram = None

    # =====================================================
    # ATTACH TELEGRAM SERVICE (SAFE INJECTION)
    # =====================================================

    def attach_telegram(self, telegram_service):

        self.telegram = telegram_service

    # =====================================================
    # SEND SVS
    # =====================================================

    async def svs(self, guild, message):

        result = await self.discord.svs_alert(guild, message)

        # future-safe telegram hook
        if self.telegram:
            await self._telegram_broadcast(guild, "SVS", message)

        return result

    # =====================================================
    # SEND KE
    # =====================================================

    async def ke(self, guild, message):

        result = await self.discord.ke_alert(guild, message)

        if self.telegram:
            await self._telegram_broadcast(guild, "KE", message)

        return result

    # =====================================================
    # ADMIN MESSAGE
    # =====================================================

    async def admin(self, guild, message):

        return await self.discord.admin_alert(guild, message)

    # =====================================================
    # TELEGRAM BROADCAST (SAFE + OPT-IN AWARE)
    # =====================================================

    async def _telegram_broadcast(self, guild, event_type, message):

        members = guild.members

        for member in members:

            if member.bot:
                continue

            contact = await db.get_member_contact(member.id)

            if not contact:
                continue

            if contact.get("opt_in", 1) == 0:
                continue

            if not contact.get("telegram_id"):
                continue

            try:
                await self.telegram.send_message(
                    chat_id=contact["telegram_id"],
                    text=message,
                    title=f"{event_type} ALERT"
                )

            except Exception:
                continue
