"""
=========================================================
 Evony Shield Watch
 Setup System (FINAL INTEGRATION FIX)
 - Auto setup on join
 - Manual setup wizard
 - EventEngine driven (NO LOCAL LOGIC)
=========================================================
"""

import discord
from discord.ext import commands
from discord import app_commands

from database import db
from services.event_engine import EventEngine
from config import Config


# =========================================================
# SETUP COG
# =========================================================

class Setup(commands.Cog):

    def __init__(self, bot: commands.Bot):
        self.bot = bot

    # =====================================================
    # AUTO SETUP ON JOIN
    # =====================================================

    @commands.Cog.listener()
    async def on_guild_join(self, guild: discord.Guild):

        channel = next(
            (c for c in guild.text_channels if c.permissions_for(guild.me).send_messages),
            None
        )

        if not channel:
            return

        # Ensure DB row exists
        await db.set_server_config(guild_id=guild.id)

        # Ensure event state exists (IMPORTANT FIX)
        await EventEngine.ensure_guild_state(guild.id)

        embed = discord.Embed(
            title="🛡️ Evony Shield Watch Setup",
            description=(
                "Welcome! Let's configure your server.\n\n"
                "Step 1: Select bubble channel\n"
                "Step 2: Select battlefield channel\n"
                "Step 3: Confirm event system sync\n\n"
                "Click below to begin setup."
            ),
            color=0x1abc9c
        )

        await channel.send(embed=embed, view=SetupView())

    # =====================================================
    # MANUAL SETUP COMMAND
    # =====================================================

    @app_commands.command(name="setup", description="Run setup wizard")
    @app_commands.checks.has_permissions(administrator=True)
    async def setup(self, interaction: discord.Interaction):

        if not interaction.guild:
            return await interaction.response.send_message(
                "❌ Guild only command.",
                ephemeral=True
            )

        await db.set_server_config(guild_id=interaction.guild_id)
        await EventEngine.ensure_guild_state(interaction.guild_id)

        embed = discord.Embed(
            title="🛡️ Setup Wizard",
            description="Click below to configure your server.",
            color=0x1abc9c
        )

        await interaction.response.send_message(
            embed=embed,
            view=SetupView(),
            ephemeral=True
        )


# =========================================================
# MAIN SETUP VIEW
# =========================================================

class SetupView(discord.ui.View):

    def __init__(self):
        super().__init__(timeout=300)

    @discord.ui.button(label="Start Setup", style=discord.ButtonStyle.primary, emoji="🛠️")
    async def start(self, interaction: discord.Interaction, button: discord.ui.Button):

        await interaction.response.send_message(
            "Select bubble channel:",
            view=ChannelSelectView("bubble"),
            ephemeral=True
        )


# =========================================================
# CHANNEL SELECTOR
# =========================================================

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

            next_view = ChannelSelectView("battlefield")

            await interaction.response.send_message(
                f"✅ Bubble set: {channel.mention}\nNow select battlefield channel:",
                view=next_view,
                ephemeral=True
            )

        elif self.step == "battlefield":
            await db.set_server_config(
                guild_id=interaction.guild_id,
                battlefield_channel_id=channel.id
            )

            await EventEngine.ensure_guild_state(interaction.guild_id)

            await interaction.response.send_message(
                f"✅ Battlefield set: {channel.mention}\n\n🛡️ Setup complete.",
                ephemeral=True
            )


# =========================================================
# SETUP COG LOADER
# =========================================================

async def setup(bot: commands.Bot):
    await bot.add_cog(Setup(bot))
