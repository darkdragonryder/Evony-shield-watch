"""
=========================================================
 Evony Shield Watch
 Alert Dispatcher (Unified Notification Engine)
=========================================================
"""

import discord
from database import db
from services.role_service import RoleService

roles = RoleService()


class AlertDispatcher:

    def __init__(self, bot: discord.Client):
        self.bot = bot

    # =====================================================
    # CORE SEND FUNCTION
    # =====================================================

    async def send_alert(self, guild: discord.Guild, title: str, message: str, min_role="member"):

        embed = discord.Embed(
            title=title,
            description=message,
            color=0xe74c3c
        )

        # -------------------------------------------------
        # iterate members
        # -------------------------------------------------

        for member in guild.members:

            if member.bot:
                continue

            user_role = await roles.get_role(member.id)

            if not self._allowed(user_role, min_role):
                continue

            try:
                await member.send(embed=embed)
            except discord.Forbidden:
                pass

    # =====================================================
    # ROLE FILTER
    # =====================================================

    def _allowed(self, user_role, min_role):

        hierarchy = {
            "member": 0,
            "coordinator": 1,
            "admin": 2,
            "owner": 3
        }

        return hierarchy[user_role] >= hierarchy[min_role]

    # =====================================================
    # PRESET ALERT TYPES
    # =====================================================

    async def svs_alert(self, guild, message):
        await self.send_alert(
            guild,
            "⚔️ SVS ALERT",
            message,
            min_role="member"
        )

    async def ke_alert(self, guild, message):
        await self.send_alert(
            guild,
            "🔥 KE ALERT",
            message,
            min_role="member"
        )

    async def admin_alert(self, guild, message):
        await self.send_alert(
            guild,
            "🛡️ ADMIN NOTICE",
            message,
            min_role="admin"
        )
