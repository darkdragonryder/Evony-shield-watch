"""
Evony Shield Watch - Server Setup & Channel Configuration
Auto-starts on join with option to choose existing or create new channels
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
        """When bot joins a server, send setup message"""
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
                           "**Step 1:** Choose your 🫧 bubble channel\n"
                           "All shield reminders will go here.\n\n"
                           "Click a button below:",
                color=0x1abc9c
            )
            view = BubbleStepView()
            await channel.send(embed=embed, view=view)
    
    @app_commands.command(name="setup", description="Manual setup wizard")
    @app_commands.checks.has_permissions(administrator=True)
    async def slash_setup(self, interaction: discord.Interaction):
        """Manual trigger if auto-setup was missed"""
        await db.set_server_config(guild_id=interaction.guild_id)
        embed = discord.Embed(
            title="🛡️ Evony Shield Watch Setup",
            description="**Step 1:** Choose your 🫧 bubble channel\n\n"
                       "Click a button below:",
            color=0x1abc9c
        )
        view = BubbleStepView()
        await interaction.response.send_message(embed=embed, view=view, ephemeral=True)


# ========== STEP 1: BUBBLE CHANNEL ==========

class BubbleStepView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=300)
    
    @discord.ui.button(label="Use Existing Channel", style=discord.ButtonStyle.secondary, emoji="📋")
    async def use_existing(self, interaction: discord.Interaction, button: discord.ui.Button):
        view = ChannelSelectView(step="bubble")
        await interaction.response.send_message(
            "Select a channel for bubble reminders:",
            view=view,
            ephemeral=True
        )
    
    @discord.ui.button(label="Create 🫧bubble🫧", style=discord.ButtonStyle.primary, emoji="🫧")
    async def create_new(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.defer(ephemeral=True)
        guild = interaction.guild
        
        existing = discord.utils.get(guild.text_channels, name=Config.DEFAULT_BUBBLE_CHANNEL)
        if existing:
            await db.set_server_config(guild_id=guild.id, bubble_channel_id=existing.id)
            await interaction.followup.send(
                f"✅ Using existing {existing.mention} for bubble reminders.",
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
                Config.DEFAULT_BUBBLE_CHANNEL,
                overwrites=overwrites,
                topic="🛡️ Bubble shield reminders",
                reason="Evony Shield Watch setup"
            )
            await db.set_server_config(guild_id=guild.id, bubble_channel_id=channel.id)
            await interaction.followup.send(
                f"✅ Created {channel.mention} for bubble reminders.",
                ephemeral=True
            )
            await self._next_step(interaction)
        except discord.Forbidden:
            await interaction.followup.send(
                "❌ I need 'Manage Channels' permission!",
                ephemeral=True
            )
    
    async def _next_step(self, interaction: discord.Interaction):
        embed = discord.Embed(
            title="Step 2/3: ⚔️ Battlefield Channel",
            description="Where should event rosters and times go?\n\n"
                       "Choose an option:",
            color=0xe74c3c
        )
        view = BattlefieldStepView()
        await interaction.channel.send(embed=embed, view=view)


# ========== STEP 2: BATTLEFIELD CHANNEL ==========

class BattlefieldStepView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=300)
    
    @discord.ui.button(label="Use Existing Channel", style=discord.ButtonStyle.secondary, emoji="📋")
    async def use_existing(self, interaction: discord.Interaction, button: discord.ui.Button):
        view = ChannelSelectView(step="battlefield")
        await interaction.response.send_message(
            "Select a channel for battlefield messages:",
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
                f"✅ Using existing {existing.mention} for battlefield messages.",
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
                topic="⚔️ Battlefield announcements & rosters",
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
                "❌ I need 'Manage Channels' permission!",
                ephemeral=True
            )
    
    async def _next_step(self, interaction: discord.Interaction):
        embed = discord.Embed(
            title="Step 3/3: 🔄 First Event",
            description="Which event is happening **this Friday**?\n"
                       "The bot will auto-alternate each week.",
            color=0x9b59b6
        )
        view = EventStepView()
        await interaction.channel.send(embed=embed, view=view)


# ========== CHANNEL DROPDOWN ==========

class ChannelSelectView(discord.ui.View):
    def __init__(self, step: str):
        super().__init__(timeout=300)
        self.step = step
    
    @discord.ui.select(
        placeholder="Choose a text channel...",
        cls=discord.ui.ChannelSelect,
        channel_types=[discord.ChannelType.text]
    )
    async def channel_select(self, interaction: discord.Interaction, select: discord.ui.ChannelSelect):
        channel = select.values[0]
        
        if self.step == "bubble":
            await db.set_server_config(guild_id=interaction.guild_id, bubble_channel_id=channel.id)
            await interaction.response.send_message(
                f"✅ Bubble channel set to {channel.mention}",
                ephemeral=True
            )
            embed = discord.Embed(
                title="Step 2/3: ⚔️ Battlefield Channel",
                description="Where should event rosters and times go?\n\n"
                           "Choose an option:",
                color=0xe74c3c
            )
            view = BattlefieldStepView()
            await interaction.channel.send(embed=embed, view=view)
        
        elif self.step == "battlefield":
            await db.set_server_config(guild_id=interaction.guild_id, battlefield_channel_id=channel.id)
            await interaction.response.send_message(
                f"✅ Battlefield channel set to {channel.mention}",
                ephemeral=True
            )
            embed = discord.Embed(
                title="Step 3/3: 🔄 First Event",
                description="Which event is happening **this Friday**?\n"
                           "The bot will auto-alternate each week.",
                color=0x9b59b6
            )
            view = EventStepView()
            await interaction.channel.send(embed=embed, view=view)


# ========== STEP 3: EVENT SELECTION ==========

class EventStepView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=300)
    
    @discord.ui.button(label="🏰 SVS", style=discord.ButtonStyle.primary)
    async def svs(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self._set_event(interaction, Config.SVS, "🏰 SVS - Server vs Server")
    
    @discord.ui.button(label="⚔️ KE", style=discord.ButtonStyle.danger)
    async def ke(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self._set_event(interaction, Config.KE, "⚔️ KE - Kill Event")
    
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
                       f"• Send bubble reminders before events\n"
                       f"• Post rosters to battlefield channel\n"
                       f"• Auto-alternate SVS ↔ KE each week\n\n"
                       f"Use `/help` for all commands.",
            color=0x2ecc71
        )
        await interaction.response.send_message(embed=embed, ephemeral=True)


# ========== STANDALONE COMMANDS ==========

class SetupCommands(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
    
    @app_commands.command(name="setbubble", description="Change bubble channel")
    @app_commands.checks.has_permissions(administrator=True)
    async def slash_setbubble(self, interaction: discord.Interaction):
        embed = discord.Embed(title="🫧 Change Bubble Channel", description="Choose:", color=0x3498db)
        view = BubbleStepView()
        await interaction.response.send_message(embed=embed, view=view, ephemeral=True)
    
    @app_commands.command(name="setbattlefield", description="Change battlefield channel")
    @app_commands.checks.has_permissions(administrator=True)
    async def slash_setbattlefield(self, interaction: discord.Interaction):
        embed = discord.Embed(title="⚔️ Change Battlefield Channel", description="Choose:", color=0xe74c3c)
        view = BattlefieldStepView()
        await interaction.response.send_message(embed=embed, view=view, ephemeral=True)
    
    @app_commands.command(name="setfirstevent", description="Change/reset event rotation")
    @app_commands.checks.has_permissions(administrator=True)
    @app_commands.describe(event_type="Which event this Friday?")
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
        await interaction.response.send_message(
            f"✅ Next event: **{event_type.name}** on {next_friday.strftime('%A, %B %d')}",
            ephemeral=True
        )
    
    @app_commands.command(name="setcoordinator", description="Set event coordinator role")
    @app_commands.checks.has_permissions(administrator=True)
    async def slash_setcoordinator(self, interaction: discord.Interaction, role: discord.Role):
        await db.set_server_config(guild_id=interaction.guild_id, event_coordinator_role_id=role.id)
        await interaction.response.send_message(f"✅ Coordinator role: {role.mention}", ephemeral=True)
    
    @app_commands.command(name="addeventcoord", description="Give user coordinator role")
    @app_commands.checks.has_permissions(administrator=True)
    async def slash_addeventcoord(self, interaction: discord.Interaction, user: discord.Member):
        config = await db.get_server_config(interaction.guild_id)
        if not config or not config.get("event_coordinator_role_id"):
            return await interaction.response.send_message("❌ Set coordinator role first with `/setcoordinator`", ephemeral=True)
        
        role = interaction.guild.get_role(config["event_coordinator_role_id"])
        if not role:
            return await interaction.response.send_message("❌ Role not found", ephemeral=True)
        
        await user.add_roles(role)
        await interaction.response.send_message(f"✅ {user.mention} is now coordinator", ephemeral=True)


async def setup(bot: commands.Bot):
    await bot.add_cog(Setup(bot))
    await bot.add_cog(SetupCommands(bot))
