"""
=========================================================
 Evony Shield Watch - Server Setup & Channel Configuration
 Auto-starts on join with option to choose existing or create new channels
=========================================================
"""

import discord
from discord.ext import commands
from discord import app_commands
from database import db
from config import Config
from datetime import datetime, timedelta


# =======================================================
# MAIN SETUP COG
# =======================================================

class Setup(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_guild_join(self, guild: discord.Guild):

        channel = next(
            (ch for ch in guild.text_channels if ch.permissions_for(guild.me).send_messages),
            None
        )

        if not channel:
            return

        await db.set_server_config(guild_id=guild.id)

        embed = discord.Embed(
            title="🛡️ Evony Shield Watch Setup",
            description=(
                "Welcome! Let's configure your server.\n\n"
                "**Step 1:** Choose your 🫧 bubble channel\n"
                "All shield reminders will go here.\n\n"
                "Click a button below:"
            ),
            color=0x1abc9c
        )

        await channel.send(embed=embed, view=BubbleStepView())

    @app_commands.command(name="setup", description="Manual setup wizard")
    @app_commands.checks.has_permissions(administrator=True)
    async def slash_setup(self, interaction: discord.Interaction):

        await db.set_server_config(guild_id=interaction.guild_id)

        embed = discord.Embed(
            title="🛡️ Evony Shield Watch Setup",
            description="**Step 1:** Choose your 🫧 bubble channel",
            color=0x1abc9c
        )

        await interaction.response.send_message(
            embed=embed,
            view=BubbleStepView(),
            ephemeral=True
        )


# =======================================================
# STEP 1: BUBBLE CHANNEL
# =======================================================

class BubbleStepView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=300)

    @discord.ui.button(
        label="Use Existing Channel",
        style=discord.ButtonStyle.secondary,
        emoji="📋"
    )
    async def use_existing(self, interaction: discord.Interaction, button: discord.ui.Button):

        if not interaction.guild:
            return await interaction.response.send_message("❌ Guild not found.", ephemeral=True)

        await interaction.response.send_message(
            "Select a channel for bubble reminders:",
            view=ChannelSelectView(step="bubble"),
            ephemeral=True
        )

    @discord.ui.button(
        label="Create Bubble Channel",
        style=discord.ButtonStyle.primary,
        emoji="🫧"
    )
    async def create_new(self, interaction: discord.Interaction, button: discord.ui.Button):

        await interaction.response.defer(ephemeral=True)

        guild = interaction.guild
        if not guild:
            return await interaction.followup.send("❌ Guild not found.", ephemeral=True)

        existing = discord.utils.get(
            guild.text_channels,
            name=Config.DEFAULT_BUBBLE_CHANNEL
        )

        if existing:
            await db.set_server_config(
                guild_id=guild.id,
                bubble_channel_id=existing.id
            )

            await interaction.followup.send(
                f"✅ Using {existing.mention}",
                ephemeral=True
            )

            await self._next_step(interaction)
            return

        overwrites = {
            guild.default_role: discord.PermissionOverwrite(send_messages=False),
            guild.me: discord.PermissionOverwrite(send_messages=True),
        }

        channel = await guild.create_text_channel(
            Config.DEFAULT_BUBBLE_CHANNEL,
            overwrites=overwrites,
            topic="🛡️ Bubble shield reminders",
            reason="Evony Shield Watch setup"
        )

        await db.set_server_config(
            guild_id=guild.id,
            bubble_channel_id=channel.id
        )

        await interaction.followup.send(
            f"✅ Created {channel.mention}",
            ephemeral=True
        )

        await self._next_step(interaction)

    async def _next_step(self, interaction: discord.Interaction):

        embed = discord.Embed(
            title="Step 2/3: ⚔️ Battlefield Channel",
            description="Choose where event messages go:",
            color=0xe74c3c
        )

        await interaction.channel.send(embed=embed, view=BattlefieldStepView())


# =======================================================
# STEP 2: BATTLEFIELD CHANNEL
# =======================================================

class BattlefieldStepView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=300)

    @discord.ui.button(
        label="Use Existing Channel",
        style=discord.ButtonStyle.secondary,
        emoji="📋"
    )
    async def use_existing(self, interaction: discord.Interaction, button: discord.ui.Button):

        await interaction.response.send_message(
            "Select battlefield channel:",
            view=ChannelSelectView(step="battlefield"),
            ephemeral=True
        )

    @discord.ui.button(
        label="Create Battlefield Channel",
        style=discord.ButtonStyle.primary,
        emoji="⚔️"
    )
    async def create_new(self, interaction: discord.Interaction, button: discord.ui.Button):

        await interaction.response.defer(ephemeral=True)

        guild = interaction.guild
        if not guild:
            return await interaction.followup.send("❌ Guild not found.", ephemeral=True)

        existing = discord.utils.get(
            guild.text_channels,
            name=Config.DEFAULT_BATTLEFIELD_CHANNEL
        )

        if existing:
            await db.set_server_config(
                guild_id=guild.id,
                battlefield_channel_id=existing.id
            )

            await interaction.followup.send(
                f"✅ Using {existing.mention}",
                ephemeral=True
            )

            await self._next_step(interaction)
            return

        overwrites = {
            guild.default_role: discord.PermissionOverwrite(send_messages=False),
            guild.me: discord.PermissionOverwrite(send_messages=True),
        }

        channel = await guild.create_text_channel(
            Config.DEFAULT_BATTLEFIELD_CHANNEL,
            overwrites=overwrites,
            topic="⚔️ Battlefield announcements",
            reason="Evony Shield Watch setup"
        )

        await db.set_server_config(
            guild_id=guild.id,
            battlefield_channel_id=channel.id
        )

        await interaction.followup.send(
            f"✅ Created {channel.mention}",
            ephemeral=True
        )

        await self._next_step(interaction)

    async def _next_step(self, interaction: discord.Interaction):

        embed = discord.Embed(
            title="Step 3/3: 🔄 First Event",
            description="Which event is this Friday?",
            color=0x9b59b6
        )

        await interaction.channel.send(embed=embed, view=EventStepView())


# =======================================================
# CHANNEL SELECT (FIXED SAFE VERSION)
# =======================================================

class ChannelSelectView(discord.ui.View):
    def __init__(self, step: str):
        super().__init__(timeout=300)
        self.step = step

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
            f"✅ Set to {channel.mention}",
            ephemeral=True
        )


# =======================================================
# STEP 3: EVENT SELECTION
# =======================================================

class EventStepView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=300)

    @discord.ui.button(label="🏰 SVS", style=discord.ButtonStyle.primary)
    async def svs(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self._set(interaction, "svs", "🏰 SVS")

    @discord.ui.button(label="⚔️ KE", style=discord.ButtonStyle.danger)
    async def ke(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self._set(interaction, "ke", "⚔️ KE")

    async def _set(self, interaction, event_type, name):

        if not interaction.guild:
            return await interaction.response.send_message("❌ Guild missing.", ephemeral=True)

        today = datetime.now().date()

        days_until_friday = (4 - today.weekday()) % 7
        if days_until_friday == 0:
            days_until_friday = 7

        next_friday = today + timedelta(days=days_until_friday)

        await db.set_event_schedule(
            guild_id=interaction.guild_id,
            current_event=event_type,
            next_event_date=next_friday
        )

        await db.set_server_config(
            guild_id=interaction.guild_id,
            setup_complete=1
        )

        await interaction.response.send_message(
            f"✅ Setup complete: {name}",
            ephemeral=True
        )


# =======================================================
# EXTRA COMMANDS COG (PLACEHOLDER SAFE)
# =======================================================

class SetupCommands(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot


# =======================================================
# SETUP ENTRY
# =======================================================

async def setup(bot: commands.Bot):
    await bot.add_cog(Setup(bot))
    await bot.add_cog(SetupCommands(bot))
