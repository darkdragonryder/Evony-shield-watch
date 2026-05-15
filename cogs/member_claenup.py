import discord
from discord.ext import commands
from database import db


class MemberCleanup(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_member_remove(self, member):
        await db.delete_member(member.id)

    @commands.Cog.listener()
    async def on_member_ban(self, guild, user):
        await db.delete_member(user.id)


async def setup(bot):
    await bot.add_cog(MemberCleanup(bot))
