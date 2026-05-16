"""
=========================================================
 Evony Shield Watch
 Server Setup System (AUTO + MANUAL SAFE)
 SMART EVENT DETECTION (KE / SVS WEEK CYCLE)
=========================================================
"""

import discord
from discord.ext import commands
from discord import app_commands

from database import db
from config import Config
from services.event_engine import EventEngine


# =======================================================
# SETUP COG
# =======================================================

class Setup(commands.Cog):

    def __init__(self, bot: commands.Bot):
        self.bot = bot

    # =====================================================
    # AUTO SETUP ON GUILD JOIN
    # =====================================================

    @commands.Cog.listener()
    async def on_guild_join(self, guild: discord.Guild):

        channel = next(
            (c for c in guild.text_channels
             if c.permissions_for(guild.me).send_messages),
            None
        )

        if not channel:
            return

        # -------------------------------------------------
        # INIT SERVER CONFIG
        # -------------------------------------------------

        await db.set_server_config(guild_id=guild.id)

        # -------------------------------------------------
        # DETERMINE CURRENT EVENT STATE (CRITICAL FIX)
        # -------------------------------------------------

        current_event = await EventEngine.get_current_event(guild.id)

        # If server joins mid-week (Sat/Sun), DO NOT reset blindly
        # Keep DB state consistent
        if current_event not in [Config.SVS, Config.KE]:
            current_event = Config.SVS

        await EventEngine.set_event(guild.id, current_event)

        # -------------------------------------------------
        # START SETUP FLOW
        # -------------------------------------------------

        embed = discord.Embed(
            title="🛡️ Evony Shield Watch Setup",
            description=(
                "Welcome to Shield Watch.\n\n"
                f"Detected current event cycle: **{current_event.upper()}**\n\n"
                "**Step 1:** Choose your 🫧 Bubble Channel"
            ),
            color=0x1abc9c
        )

        await channel.send(embed=embed, view=BubbleStepView())


    # =====================================================
    # MANUAL SETUP COMMAND
    # =====================================================

    @app_commands.command(name="setup", description="Manual setup wizard")
    @app_commands.checks.has_permissions(administrator=True)
    async def setup(self, interaction: discord.Interaction):

        await db.set_server_config(guild_id=interaction.guild_id)

        current_event = await EventEngine.get_current_event(interaction.guild_id)

        embed = discord.Embed(
            title="🛡️ Manual Setup",
            description=(
                f"Detected event: **{current_event.upper()}**\n\n"
                "Configure your server below."
            ),
            color=0x1abc9c
        )

        await interaction.response.send_message(
            embed=embed,
            view=BubbleStepView(),
            ephemeral=True
        )


# =======================================================
# STEP 1 - BUBBLE CHANNEL
# =======================================================

class BubbleStepView(discord.ui.View):

    def __init__(self):
        super().__init__(timeout=300)

    @discord.ui.button(
        label="Use Existing Channel",
        style=discord.ButtonStyle.secondary,
        emoji="📋"
    )
    async def existing(self, interaction: discord.Interaction, button: discord.ui.Button):

        await interaction.response.send_message(
            "Select bubble channel:",
            view=ChannelSelectView(step="bubble"),
            ephemeral=True
        )

    @discord.ui.button(
        label="Create Channel",
        style=discord.ButtonStyle.primary,
        emoji="🫧"
    )
    async def create(self, interaction: discord.Interaction, button: discord.ui.Button):

        guild = interaction.guild

        existing = discord.utils.get(
            guild.text_channels,
            name=Config.DEFAULT_BUBBLE_CHANNEL
        )

        if not existing:

            overwrites = {
                guild.default_role: discord.PermissionOverwrite(send_messages=False),
                guild.me: discord.PermissionOverwrite(send_messages=True),
            }

            existing = await guild.create_text_channel(
                Config.DEFAULT_BUBBLE_CHANNEL,
                overwrites=overwrites,
                topic="Shield Watch Bubble Alerts"
            )

        await db.set_server_config(
            guild_id=guild.id,
            bubble_channel_id=existing.id
        )

        await interaction.response.send_message(
            f"✅ Bubble channel set: {existing.mention}",
            ephemeral=True
        )


# =======================================================
# CHANNEL SELECT
# =======================================================

class ChannelSelectView(discord.ui.View):

    def __init__(self, step: str):
        super().__init__(timeout=300)
        self.add_item(ChannelSelect(step))


class ChannelSelect(discord.ui.ChannelSelect):

    def __init__(self, step: str):
        super().__init__(channel_types=[discord.ChannelType.text])
        self.step = step

    async def callback(self, interaction: discord.Interaction):

        channel = self.values[0]

        if self.step == "bubble":
            await db.set_server_config(
                guild_id=interaction.guild_id,
                bubble_channel_id=channel.id
            )

        elif self.step == "battlefield":
            await db.set_server_config(
                guild_id=interaction.guild_id,
                battlefield_channel_id=channel.id
            )

        await interaction.response.send_message(
            f"✅ Set: {channel.mention}",
            ephemeral=True
        )


# =======================================================
# STEP OBJECTS IMPORT SAFE PLACEHOLDER
# (battlefield + event step remain unchanged for now)
# =======================================================
