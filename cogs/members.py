"""
=========================================================
 Evony Shield Watch
 Member Lifecycle System
 (Join / Leave / Ban / Cleanup / Onboarding)
=========================================================
"""

# =========================================================
# IMPORTS
# =========================================================

import discord
from discord.ext import commands
from database import db


# =========================================================
# MEMBERS COG
# =========================================================

class Members(commands.Cog):

    def __init__(self, bot):
        self.bot = bot


    # =====================================================
    # MEMBER JOIN
    # =====================================================

    @commands.Cog.listener()
    async def on_member_join(self, member):

        if member.bot:
            return

        await db.set_member_contact(member.id)

        try:
            await member.send(
                "🛡️ Welcome to Evony Shield Watch\n\n"
                "Use /linktelegram to connect alerts."
            )
        except:
            pass


    # =====================================================
    # MEMBER LEAVE
    # =====================================================

    @commands.Cog.listener()
    async def on_member_remove(self, member):

        if not member.bot:
            await db.delete_user_data(member.id)


    # =====================================================
    # MEMBER BAN
    # =====================================================

    @commands.Cog.listener()
    async def on_member_ban(self, guild, user):

        if not user.bot:
            await db.delete_user_data(user.id)


# =========================================================
# SETUP
# =========================================================

async def setup(bot):
    await bot.add_cog(Members(bot))
