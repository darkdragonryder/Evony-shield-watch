"""
Server Setup & Channel Configuration - Slash Commands
"""
import discord
from discord.ext import commands
from discord import app_commands
from database import db
from utils.embeds import Embeds
from config import Config

class Setup(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
    
    @commands.Cog.listener()
    async def on_guild_join(self, guild: discord.Guild):
        channel = None
        for ch in guild.text_channels:
            if ch.permissions_for(guild.me).send_messages:
                channel = ch
                break
        
        if channel:
            embed = Embeds.setup_welcome()
            view = SetupView(guild.id)
            await channel.send(embed=embed, view=view)
            await db.set_server_config(guild_id=guild.id)
    
    # ========== SLASH COMMANDS ==========
    
    @app_commands.command(name="setup", description="Start server configuration")
    @app_commands.checks.has_permissions(administrator=True)
    async def slash_setup(self, interaction: discord.Interaction):
        embed = Embeds.setup_welcome()
        view = SetupView(interaction.guild_id)
        await interaction.response.send_message(embed=embed, view=view, ephemeral=True)
    
    @app_commands.command(name="setbubble", description="Set or create bubble channel")
    @app_commands.checks.has_permissions(administrator=True)
    @app_commands.describe(channel="Existing channel (optional, creates 🫧bubble🫧 if not provided)")
    async def slash_setbubble(self, interaction: discord.Interaction,
                              channel: discord.TextChannel = None):
        if channel is None:
            channel = discord.utils.get(interaction.guild.text_channels, name=Config.DEFAULT_BUBBLE_CHANNEL)
            if channel is None:
                overwrites = {
                    interaction.guild.default_role: discord.PermissionOverwrite(send_messages=False),
                    interaction.guild.me: discord.PermissionOverwrite(send_messages=True)
                }
                channel = await interaction.guild.create_text_channel(
                    Config.DEFAULT_BUBBLE_CHANNEL,
                    overwrites=overwrites,
                    topic="🛡️ Bubble shield reminders"
                )
        
        await db.set_server_config(guild_id=interaction.guild_id, bubble_channel_id=channel.id)
        await interaction.response.send_message(f"✅ Bubble channel set to {channel.mention}", ephemeral=True)
    
    @app_commands.command(name="setbattlefield", description="Set or create battlefield channel")
    @app_commands.checks.has_permissions(administrator=True)
    @app_commands.describe(channel="Existing channel (optional, creates battlefield-messages if not provided)")
    async def slash_setbattlefield(self, interaction: discord.Interaction,
                                   channel: discord.TextChannel = None):
        if channel is None:
            channel = discord.utils.get(interaction.guild.text_channels, name=Config.DEFAULT_BATTLEFIELD_CHANNEL)
            if channel is None:
                overwrites = {
                    interaction.guild.default_role: discord.PermissionOverwrite(send_messages=False),
                    interaction.guild.me: discord.PermissionOverwrite(send_messages=True)
                }
                channel = await interaction.guild.create_text_channel(
                    Config.DEFAULT_BATTLEFIELD_CHANNEL,
                    overwrites=overwrites,
                    topic="⚔️ Battlefield announcements & event rosters"
                )
        
        await db.set_server_config(guild_id=interaction.guild_id, battlefield_channel_id=channel.id)
        await interaction.response.send_message(f"✅ Battlefield channel set to {channel.mention}", ephemeral=True)
    
    @app_commands.command(name="setcoordinator", description="Set the event coordinator role")
    @app_commands.checks.has_permissions(administrator=True)
    @app_commands.describe(role="The role that can create/manage events")
    async def slash_setcoordinator(self, interaction: discord.Interaction, role: discord.Role):
        await db.set_server_config(guild_id=interaction.guild_id, event_coordinator_role_id=role.id)
        await interaction.response.send_message(f"✅ Event coordinator role set to {role.mention}", ephemeral=True)
    
    @app_commands.command(name="addeventcoord", description="Give a user the event coordinator role")
    @app_commands.checks.has_permissions(administrator=True)
    @app_commands.describe(user="User to make coordinator")
    async def slash_addeventcoord(self, interaction: discord.Interaction, user: discord.Member):
        config = await db.get_server_config(interaction.guild_id)
        if not config or not config.get("event_coordinator_role_id"):
            return await interaction.response.send_message("❌ No coordinator role set. Use `/setcoordinator` first.", ephemeral=True)
        
        role = interaction.guild.get_role(config["event_coordinator_role_id"])
        if not role:
            return await interaction.response.send_message("❌ Coordinator role not found.", ephemeral=True)
        
        await user.add_roles(role)
        await interaction.response.send_message(f"✅ {user.mention} is now an Event Coordinator!", ephemeral=True)

class SetupView(discord.ui.View):
    def __init__(self, guild_id: int):
        super().__init__(timeout=300)
        self.guild_id = guild_id
    
    @discord.ui.button(label="Create 🫧bubble🫧", style=discord.ButtonStyle.primary, emoji="🫧")
    async def create_bubble(self, interaction: discord.Interaction, button: discord.ui.Button):
        guild = interaction.guild
        overwrites = {
            guild.default_role: discord.PermissionOverwrite(send_messages=False),
            guild.me: discord.PermissionOverwrite(send_messages=True)
        }
        channel = await guild.create_text_channel(
            Config.DEFAULT_BUBBLE_CHANNEL,
            overwrites=overwrites,
            topic="🛡️ Bubble shield reminders"
        )
        await db.set_server_config(guild_id=guild.id, bubble_channel_id=channel.id)
        await interaction.response.send_message(f"✅ Created {channel.mention}", ephemeral=True)
    
    @discord.ui.button(label="Create Battlefield Channel", style=discord.ButtonStyle.primary, emoji="⚔️")
    async def create_battlefield(self, interaction: discord.Interaction, button: discord.ui.Button):
        guild = interaction.guild
        overwrites = {
            guild.default_role: discord.PermissionOverwrite(send_messages=False),
            guild.me: discord.PermissionOverwrite(send_messages=True)
        }
        channel = await guild.create_text_channel(
            Config.DEFAULT_BATTLEFIELD_CHANNEL,
            overwrites=overwrites,
            topic="⚔️ Battlefield announcements & rosters"
        )
        await db.set_server_config(guild_id=guild.id, battlefield_channel_id=channel.id)
        await interaction.response.send_message(f"✅ Created {channel.mention}", ephemeral=True)
    
    @discord.ui.button(label="Finish Setup", style=discord.ButtonStyle.success, emoji="✅")
    async def finish_setup(self, interaction: discord.Interaction, button: discord.ui.Button):
        await db.set_server_config(guild_id=interaction.guild_id, setup_complete=1)
        await interaction.response.send_message(
            "✅ Setup complete! Use `/help` for all commands.", ephemeral=True
        )

async def setup(bot: commands.Bot):
    await bot.add_cog(Setup(bot))
