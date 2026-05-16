"""
Evony Shield Watch
Alert Dispatcher (Unified Notification Engine)
Fixed + Multi-Guild Safe + Opt-in Aware
"""

import discord
import asyncio
from database import db


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

        failed = 0
        sent = 0

        # -------------------------------------------------
        # iterate members safely
        # -------------------------------------------------

        for member in guild.members:

            if member.bot:
                continue

            # DB ROLE (single source of truth)
            role = await db.get_role(member.id)

            if not role:
                role = "member"

            if not self._allowed(role, min_role):
                continue

            # DB OPT-IN CHECK (CRITICAL FIX)
            contact = await db.get_member_contact(member.id)
            if contact and contact.get("opt_in", 1) == 0:
                continue

            try:
                await member.send(embed=embed)
                sent += 1

            except discord.Forbidden:
                failed += 1

            except discord.HTTPException:
                failed += 1
                await asyncio.sleep(0.5)  # small backoff

        return {"sent": sent, "failed": failed}

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

        return hierarchy.get(user_role, 0) >= hierarchy.get(min_role, 0)

    # =====================================================
    # PRESET ALERT TYPES
    # =====================================================

    async def svs_alert(self, guild, message):

        return await self.send_alert(
            guild,
            "⚔️ SVS ALERT",
            message,
            min_role="member"
        )

    async def ke_alert(self, guild, message):

        return await self.send_alert(
            guild,
            "🔥 KE ALERT",
            message,
            min_role="member"
        )

    async def admin_alert(self, guild, message):

        return await self.send_alert(
            guild,
            "🛡️ ADMIN NOTICE",
            message,
            min_role="admin"
        )
