"""
=========================================================
 Evony Shield Watch
 Member Lifecycle System (Multi-Guild Safe)
=========================================================
"""

import discord
from discord.ext import commands
from database import db


class Members(commands.Cog):

    def __init__(self, bot):
        self.bot = bot


    @commands.Cog.listener()
    async def on_member_join(self, member):

        if member.bot:
            return

        guild_id = member.guild.id

        await db.set_member_contact(member.id, guild_id)

        try:
            await member.send("🛡️ Welcome to Evony Shield Watch")
        except:
            pass


    @commands.Cog.listener()
    async def on_member_remove(self, member):

        if member.bot:
            return

        await db.delete_user_data(member.id, member.guild.id)


    @commands.Cog.listener()
    async def on_member_ban(self, guild, user):

        if user.bot:
            return

        await db.delete_user_data(user.id, guild.id)


async def setup(bot):
    await bot.add_cog(Members(bot))
