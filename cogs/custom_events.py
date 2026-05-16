"""
Evony Shield Watch
Custom Events Cog
Clean Production Version
"""

from discord.ext import commands
import discord


class CustomEvents(commands.Cog):

    def __init__(self, bot: commands.Bot):
        self.bot = bot

    # =====================================================
    # TEST COMMAND (REMOVE OR KEEP)
    # =====================================================
    @commands.command(name="eventping")
    async def eventping(self, ctx):
        await ctx.send("✅ Custom Events Cog loaded correctly")

    # =====================================================
    # YOUR EVENT LOGIC GOES HERE
    # =====================================================

    async def handle_custom_event(self):
        pass


# =========================================================
# DISCORD EXTENSION ENTRYPOINT (REQUIRED)
# =========================================================

async def setup(bot: commands.Bot):
    await bot.add_cog(CustomEvents(bot))
