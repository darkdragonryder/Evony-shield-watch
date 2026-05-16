"""
=========================================================
Evony Shield Watch
Member Lifecycle System (FIXED + DB ALIGNED)
=========================================================
"""

import discord
from discord.ext import commands
from database import db


class Members(commands.Cog):

    def __init__(self, bot: commands.Bot):
        self.bot = bot

    # =====================================================
    # MEMBER JOIN
    # =====================================================

    @commands.Cog.listener()
    async def on_member_join(self, member: discord.Member):

        if member.bot:
            return

        # FIX: correct DB usage (NO guild_id here)
        await db.set_member_contact(member.id)

        try:
            await member.send(
                "🛡️ Welcome to Evony Shield Watch\n"
                "Use /help to get started."
            )
        except discord.Forbidden:
            pass

    # =====================================================
    # MEMBER REMOVE
    # =====================================================

    @commands.Cog.listener()
    async def on_member_remove(self, member: discord.Member):

        if member.bot:
            return

        # FIX: correct function name
        await db.delete_member_data(member.id)

    # =====================================================
    # MEMBER BAN
    # =====================================================

    @commands.Cog.listener()
    async def on_member_ban(self, guild: discord.Guild, user: discord.User):

        if user.bot:
            return

        # FIX: correct function name
        await db.delete_member_data(user.id)


# =========================================================
# SETUP
# =========================================================

async def setup(bot: commands.Bot):
    await bot.add_cog(Members(bot))
