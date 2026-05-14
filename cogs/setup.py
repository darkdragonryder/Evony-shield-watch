"""
Evony Shield Watch - Interactive Server Setup Wizard
Walks through: bubble channel → battlefield channel → first event → done
"""
import discord
from discord.ext import commands
from discord import app_commands
from database import db
from utils.embeds import Embeds
from config import Config
from datetime import datetime, timedelta

class Setup(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
    
    @commands.Cog.listener()
    async def on_guild_join(self, guild: discord.Guild):
        """When bot joins, send setup wizard to first available channel"""
        channel = None
        for ch in guild.text_channels:
            if ch.permissions_for(guild.me).send_messages:
                channel = ch
                break
        
        if channel:
            await db.set_server_config(guild_id=guild.id)
            embed = discord.Embed(
                title="🛡️ Evony Shield Watch Setup",
                description="Welcome! Let's configure your server.\n\n"
                           "Click **Start Setup** below to begin.",
                color=0x1abc9c
            )
            view = StartSetupView()
            await channel.send(embed=embed, view=view)
    
    @app_commands.command(name="setup", description="Start the server setup wizard")
    @app_commands.checks.has_permissions(administrator=True)
    async def slash_setup(self, interaction: discord.Interaction):
        """Manual trigger for setup wizard"""
        await db.set_server_config(guild_id=interaction.guild_id)
        embed = discord.Embed(
            title="🛡️ Evony Shield Watch Setup",
            description="Let's configure your server step by step.\n\n"
                       "Click **Start Setup** below to begin.",
            color=0x1abc9c
        )
        view = StartSetupView()
        await interaction.response.send_message(embed=embed, view=view, ephemeral=True)


class StartSetupView(discord.ui.View):
    """Initial button to start the wizard"""
    def __init__(self):
        super().__init__(timeout=300)
    
    @discord.ui.button(label="Start Setup", style=discord.ButtonStyle.primary, emoji="🚀")
    async def start(self, interaction: discord.Interaction, button: discord.ui.Button):
        # Step 1: Bubble channel
        embed = discord.Embed(
            title="Step 1/3: 🫧 Bubble Channel",
            description="Where should shield reminders go?\n\n"
                       "Choose an option below:",
            color=0x3498db
        )
        view = BubbleChannelView()
        await interaction.response.edit_message(embed=embed, view=view)


class BubbleChannelView(discord.ui.View):
    """Choose bubble channel: existing or create new"""
    def __init__(self):
        super().__init__(timeout=300)
    
    @discord.ui.button(label="Use Existing Channel", style=discord.ButtonStyle.secondary, emoji="📋")
    async def existing(self, interaction: discord.Interaction, button: discord.ui.Button):
        # Show channel select
        view = ChannelSelectView(channel_type="bubble")
        await interaction.response.edit_message(
            content="Select a channel from the dropdown below:",
            embed=None,
            view=view
        )
    
    @discord.ui.button(label="Create 🫧bubble🫧", style=discord.ButtonStyle.primary, emoji="🫧")
    async def create_new(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.defer(ephemeral=True)
        
        guild = interaction.guild
        # Check if already exists
        existing = discord.utils.get(guild.text_channels, name=Config.DEFAULT_BUBBLE_CHANNEL)
        if existing:
            await db.set_server_config(guild_id=guild.id, bubble_channel_id=existing.id)
            await interaction.followup.send(
                f"✅ Found existing {existing.mention}, using it for bubble reminders.",
                ephemeral=True
            )
            # Move to battlefield step
            await self._next_step(interaction, "bubble_done")
            return
        
        # Create new
        overwrites = {
            guild.default_role: discord.PermissionOverwrite(send_messages=False),
            guild.me: discord.PermissionOverwrite(send_messages=True)
        }
        try:
            channel = await guild.create_text_channel(
                Config.DEFAULT_BUBBLE_CHANNEL,
                overwrites=overwrites,
                topic="🛡️ Bubble shield reminders and notifications",
                reason="Evony Shield Watch setup"
            )
            await db.set_server_config(guild_id=guild.id, bubble_channel_id=channel.id)
            await interaction.followup.send(
                f"✅ Created {channel.mention} for bubble reminders.",
                ephemeral=True
            )
            await self._next_step(interaction, "bubble_done")
        except discord.Forbidden:
            await interaction.followup.send(
                "❌ I need 'Manage Channels' permission to create channels!",
                ephemeral=True
            )
    
    async def _next_step(self, interaction: discord.Interaction, step: str):
        # Send battlefield step as new message
        embed = discord.Embed(
            title="Step 2/3: ⚔️ Battlefield Channel",
            description="Where should event rosters and times go?\n\n"
                       "Choose an option below:",
            color=0xe74c3c
        )
        view = BattlefieldChannelView()
        await interaction.channel.send(embed=embed, view=view)


class ChannelSelectView(discord.ui.View):
    """Dropdown to select an existing channel"""
    def __init__(self, channel_type: str):
        super().__init__(timeout=300)
        self.channel_type = channel_type
    
    @discord.ui.select(
        placeholder="Choose a channel...",
        cls=discord.ui.ChannelSelect,
        channel_types=[discord.ChannelType.text]
    )
    async def select_channel(self, interaction: discord.Interaction, select: discord.ui.ChannelSelect):
        channel = select.values[0]
        
        if self.channel_type == "bubble":
            await db.set_server_config(guild_id=interaction.guild_id, bubble_channel_id=channel.id)
            await interaction.response.send_message(
                f"✅ Bubble channel set to {channel.mention}",
                ephemeral=True
            )
            # Move to battlefield step
            embed = discord.Embed(
                title="Step 2/3: ⚔️ Battlefield Channel",
                description="Where should event rosters and times go?\n\n"
                           "Choose an option below:",
                color=0xe74c3c
            )
            view = BattlefieldChannelView()
            await interaction.channel.send(embed=embed, view=view)
        
        elif self.channel_type == "battlefield":
            await db.set_server_config(guild_id=interaction.guild_id, battlefield_channel_id=channel.id)
            await interaction.response.send_message(
                f"✅ Battlefield channel set to {channel.mention}",
                ephemeral=True
            )
            # Move to event step
            embed = discord.Embed(
                title="Step 3/3: 🔄 First Event",
                description="Which event is happening **this Friday**?\n\n"
                           "The bot will auto-alternate each week after.",
                color=0x9b59b6
            )
            view = FirstEventView()
            await interaction.channel.send(embed=embed, view=view)


class BattlefieldChannelView(discord.ui.View):
    """Choose battlefield channel: existing or create new"""
    def __init__(self):
        super().__init__(timeout=300)
    
    @discord.ui.button(label="Use Existing Channel", style=discord.ButtonStyle.secondary, emoji="📋")
    async def existing(self, interaction: discord.Interaction, button: discord.ui.Button):
        view = ChannelSelectView(channel_type="battlefield")
        await interaction.response.send_message(
            "Select a channel from the dropdown below:",
            view=view,
            ephemeral=True
        )
    
    @discord.ui.button(label="Create battlefield-messages", style=discord.ButtonStyle.primary, emoji="⚔️")
    async def create_new(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.defer(ephemeral=True)
        
        guild = interaction.guild
        existing = discord.utils.get(guild.text_channels, name=Config.DEFAULT_BATTLEFIELD_CHANNEL)
        if existing:
            await db.set_server_config(guild_id=guild.id, battlefield_channel_id=existing.id)
            await interaction.followup.send(
                f"✅ Found existing {existing.mention}, using it for battlefield messages.",
                ephemeral=True
            )
            await self._next_step(interaction)
            return
        
        overwrites = {
            guild.default_role: discord.PermissionOverwrite(send_messages=False),
            guild.me: discord.PermissionOverwrite(send_messages=True)
        }
        try:
            channel = await guild.create_text_channel(
                Config.DEFAULT_BATTLEFIELD_CHANNEL,
                overwrites=overwrites,
                topic="⚔️ Battlefield announcements, event rosters & times",
                reason="Evony Shield Watch setup"
            )
            await db.set_server_config(guild_id=guild.id, battlefield_channel_id=channel.id)
            await interaction.followup.send(
                f"✅ Created {channel.mention} for battlefield messages.",
                ephemeral=True
            )
            await self._next_step(interaction)
        except discord.Forbidden:
            await interaction.followup.send(
                "❌ I need 'Manage Channels' permission to create channels!",
                ephemeral=True
            )
    
    async def _next_step(self, interaction: discord.Interaction):
        embed = discord.Embed(
            title="Step 3/3: 🔄 First Event",
            description="Which event is happening **this Friday**?\n\n"
                       "The bot will auto-alternate each week after.",
            color=0x9b59b6
        )
        view = FirstEventView()
        await interaction.channel.send(embed=embed, view=view)


class FirstEventView(discord.ui.View):
    """Choose SVS or KE as first event"""
    def __init__(self):
        super().__init__(timeout=300)
    
    @discord.ui.button(label="🏰 SVS - Server vs Server", style=discord.ButtonStyle.primary)
    async def svs(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self._set_event(interaction, Config.SVS, "🏰 SVS")
    
    @discord.ui.button(label="⚔️ KE - Kill Event", style=discord.ButtonStyle.danger)
    async def ke(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self._set_event(interaction, Config.KE, "⚔️ KE")
    
    async def _set_event(self, interaction: discord.Interaction, event_type: str, event_name: str):
        today = datetime.now().date()
        days_until_friday = (4 - today.weekday()) % 7 or 7
        next_friday = today + timedelta(days=days_until_friday)
        
        await db.set_event_schedule(
            guild_id=interaction.guild_id,
            current_event=event_type,
            next_event_date=next_friday
        )
        await db.set_server_config(guild_id=interaction.guild_id, setup_complete=1)
        
        embed = discord.Embed(
            title="✅ Setup Complete!",
            description=f"**{event_name}** set as first event.\n"
                       f"Next: **{next_friday.strftime('%A, %B %d')}**\n\n"
                       f"The bot will now:\n"
                       f"• Send reminders to your 🫧 bubble channel\n"
                       f"• Post rosters to your battlefield channel\n"
                       f"• Auto-alternate SVS ↔ KE each week\n\n"
                       f"Use `/help` for all commands.",
            color=0x2ecc71
        )
        await interaction.response.send_message(embed=embed, ephemeral=True)


# ========== STANDALONE SLASH COMMANDS (for changing later) ==========

class SetupSlashCommands(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
    
    @app_commands.command(name="setbubble", description="Change bubble channel settings")
    @app_commands.checks.has_permissions(administrator=True)
    async def slash_setbubble(self, interaction: discord.Interaction):
        embed = discord.Embed(
            title="🫧 Change Bubble Channel",
            description="Current settings can be changed here.",
            color=0x3498db
        )
        view = BubbleChannelView()
        await interaction.response.send_message(embed=embed, view=view, ephemeral=True)
    
    @app_commands.command(name="setbattlefield", description="Change battlefield channel settings")
    @app_commands.checks.has_permissions(administrator=True)
    async def slash_setbattlefield(self, interaction: discord.Interaction):
        embed = discord.Embed(
            title="⚔️ Change Battlefield Channel",
            description="Current settings can be changed here.",
            color=0xe74c3c
        )
        view = BattlefieldChannelView()
        await interaction.response.send_message(embed=embed, view=view, ephemeral=True)
    
    @app_commands.command(name="setfirstevent", description="Change/reset the event rotation")
    @app_commands.checks.has_permissions(administrator=True)
    @app_commands.describe(event_type="Which event is happening this Friday?")
    @app_commands.choices(event_type=[
        app_commands.Choice(name="🏰 SVS", value="svs"),
        app_commands.Choice(name="⚔️ KE", value="ke")
    ])
    async def slash_setfirstevent(self, interaction: discord.Interaction, event_type: app_commands.Choice[str]):
        today = datetime.now().date()
        days_until_friday = (4 - today.weekday()) % 7 or 7
        next_friday = today + timedelta(days=days_until_friday)
        
        await db.set_event_schedule(
            guild_id=interaction.guild_id,
            current_event=event_type.value,
            next_event_date=next_friday
        )
        
        embed = discord.Embed(
            title="🔄 Event Rotation Updated",
            description=f"Next event: **{event_type.name}**\n"
                       f"Date: **{next_friday.strftime('%A, %B %d')}**",
            color=0x9b59b6
        )
        await interaction.response.send_message(embed=embed, ephemeral=True)
    
    @app_commands.command(name="setcoordinator", description="Set the event coordinator role")
    @app_commands.checks.has_permissions(administrator=True)
    async def slash_setcoordinator(self, interaction: discord.Interaction, role: discord.Role):
        await db.set_server_config(guild_id=interaction.guild_id, event_coordinator_role_id=role.id)
        await interaction.response.send_message(f"✅ Coordinator role set to {role.mention}", ephemeral=True)


async def setup(bot: commands.Bot):
    await bot.add_cog(Setup(bot))
    await bot.add_cog(SetupSlashCommands(bot))
