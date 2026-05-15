"""
=========================================================
 Evony Shield Watch
 Enterprise Member Lifecycle System
 (Join / Leave / Ban / Restore / Telegram Ready)
=========================================================
"""

# =========================================================
# IMPORTS
# =========================================================

import discord
from discord.ext import commands
from datetime import datetime

from database import db
from config import Config


# =========================================================
# MEMBERS COG
# =========================================================

class Members(commands.Cog):

    def __init__(self, bot: commands.Bot):
        self.bot = bot

    # =====================================================
    # MEMBER JOIN (ONBOARDING + RESTORE CHECK)
    # =====================================================

    @commands.Cog.listener()
    async def on_member_join(self, member: discord.Member):

        if member.bot:
            return

        # ---------------------------------------------
        # ensure or restore DB record
        # ---------------------------------------------

        existing = await db.get_member_contact(member.id)

        if existing:
            # restore returning user
            await db.set_member_contact(
                member.id,
                status="active",
                opted_in=1,
                last_seen=datetime.utcnow().isoformat()
            )
        else:
            # new user profile
            await db.set_member_contact(
                member.id,
                status="active",
                opted_in=1,
                timezone="UTC",
                last_seen=datetime.utcnow().isoformat()
            )

        # ---------------------------------------------
        # onboarding DM
        # ---------------------------------------------

        try:

            embed = discord.Embed(
                title="🛡️ Welcome to Evony Shield Watch",
                description=(
                    "To get full SVS / KE / Event alerts:\n\n"
                    "✔ Set your timezone\n"
                    "✔ Link Telegram for instant alerts (optional)\n"
                    "✔ Manage notification preferences anytime"
                ),
                color=0x1abc9c
            )

            embed.add_field(
                name="🔗 Telegram Linking",
                value="Use `/linktelegram` in the server (coming in next update)",
                inline=False
            )

            embed.add_field(
                name="⏰ Timezone Setup",
                value="`/settimezone Europe/London`",
                inline=False
            )

            embed.add_field(
                name="🔕 Controls",
                value="`/optout` or `/optin` anytime",
                inline=False
            )

            await member.send(embed=embed)

        except discord.Forbidden:
            pass

    # =====================================================
    # MEMBER LEAVE (SOFT DELETE - NO DATA LOSS)
    # =====================================================

    @commands.Cog.listener()
    async def on_member_remove(self, member: discord.Member):

        if member.bot:
            return

        await db.set_member_contact(
            member.id,
            status="left",
            opted_in=0,
            left_at=datetime.utcnow().isoformat()
        )

    # =====================================================
    # MEMBER BAN (FLAGGED - NO DELETE)
    # =====================================================

    @commands.Cog.listener()
    async def on_member_ban(self, guild: discord.Guild, user: discord.User):

        if user.bot:
            return

        await db.set_member_contact(
            user.id,
            status="banned",
            opted_in=0,
            banned_at=datetime.utcnow().isoformat()
        )

    # =====================================================
    # MEMBER UNBAN (RESTORE ELIGIBILITY)
    # =====================================================

    @commands.Cog.listener()
    async def on_member_unban(self, guild: discord.Guild, user: discord.User):

        await db.set_member_contact(
            user.id,
            status="inactive",
            opted_in=1
        )


# =========================================================
# SETUP
# =========================================================

async def setup(bot: commands.Bot):
    await bot.add_cog(Members(bot))
