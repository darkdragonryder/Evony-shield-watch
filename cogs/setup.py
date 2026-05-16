"""
=========================================================
Evony Shield Watch
Server Setup (AUTO INIT + SMART EVENT DETECTION)
=========================================================
"""

import discord
from discord.ext import commands
from discord import app_commands

from database import db
from services.event_engine import EventEngine


class Setup(commands.Cog):

    def __init__(self, bot: commands.Bot):
        self.bot = bot

    # =====================================================
    # AUTO SETUP ON GUILD JOIN
    # =====================================================

    @commands.Cog.listener()
    async def on_guild_join(self, guild: discord.Guild):

        channel = next(
            (c for c in guild.text_channels if c.permissions_for(guild.me).send_messages),
            None
        )

        if not channel:
            return

        await db.set_server_config(guild_id=guild.id)

        current_event = EventEngine.get_current_event()

        embed = discord.Embed(
            title="🛡️ Evony Shield Watch Setup",
            description=(
                "Welcome! Let's configure your server.\n\n"
                f"📅 Current detected event: **{current_event.upper()}**\n\n"
                "Step 1: Choose bubble channel"
            ),
            color=0x1abc9c
        )

        await channel.send(embed=embed, view=BubbleStepView(current_event))

    # =====================================================
    # MANUAL SETUP
    # =====================================================

    @app_commands.command(name="setup")
    @app_commands.checks.has_permissions(administrator=True)
    async def setup(self, interaction: discord.Interaction):

        current_event = EventEngine.get_current_event()

        await db.set_server_config(interaction.guild_id)

        embed = discord.Embed(
            title="🛡️ Setup Wizard",
            description=f"Detected event: **{current_event.upper()}**",
            color=0x1abc9c
        )

        await interaction.response.send_message(
            embed=embed,
            view=BubbleStepView(current_event),
            ephemeral=True
        )
    
