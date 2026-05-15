"""
=========================================================
 Evony Shield Watch
 Member Lifecycle System (UPGRADED)
=========================================================
"""

import discord
from discord.ext import commands

from database import db


class Members(commands.Cog):

    def __init__(self, bot: commands.Bot):
        self.bot = bot

    # =====================================================
    # JOIN
    # =====================================================

    @commands.Cog.listener()
    async def on_member_join(self, member: discord.Member):

        if member.bot:
            return

        await db.set_member_contact(member.id)

        try:
            await member.send(
                "🛡️ Welcome to Evony Shield Watch\n\n"
                "Use /linktelegram to connect alerts."
            )
        except discord.Forbidden:
            pass

    # =====================================================
    # LEAVE
    # =====================================================

    @commands.Cog.listener()
    async def on_member_remove(self, member: discord.Member):

        if member.bot:
            return

        await db.delete_user_data(member.id)

    # =====================================================
    # BAN
    # =====================================================

    @commands.Cog.listener()
    async def on_member_ban(self, guild, user):

        if user.bot:
            return

        await db.delete_user_data(user.id)

    # =====================================================
    # UNBAN
    # =====================================================

    @commands.Cog.listener()
    async def on_member_unban(self, guild, user):

        await db.set_member_contact(user.id)


async def setup(bot: commands.Bot):
    await bot.add_cog(Members(bot))
