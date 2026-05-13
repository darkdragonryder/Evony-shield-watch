"""
Admin & Utility Commands - Slash Commands
"""
import discord
from discord.ext import commands
from discord import app_commands
from utils.embeds import Embeds
from database import db

class Admin(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
    
    @app_commands.command(name="help", description="Show all available commands")
    async def slash_help(self, interaction: discord.Interaction):
        embed = Embeds.help_command()
        await interaction.response.send_message(embed=embed, ephemeral=True)
    
    @app_commands.command(name="botinfo", description="Show bot information")
    async def slash_botinfo(self, interaction: discord.Interaction):
        embed = discord.Embed(
            title="🛡️ Evony Shield Watch",
            description="Automated shield and event management for Evony: Return of the King",
            color=0x1abc9c
        )
        embed.add_field(name="Version", value="1.0.0", inline=True)
        embed.add_field(name="Servers", value=len(self.bot.guilds), inline=True)
        embed.add_field(
            name="Features",
            value="• Auto SVS/KE rotation\n• Bubble reminders with local times\n• Custom events (BOC/BOG/AllStars/BF)\n• Check-in system\n• SMS & Push notifications",
            inline=False
        )
        await interaction.response.send_message(embed=embed, ephemeral=True)
    
    @app_commands.command(name="ping", description="Check bot latency")
    async def slash_ping(self, interaction: discord.Interaction):
        latency = round(self.bot.latency * 1000)
        await interaction.response.send_message(f"🏓 Pong! `{latency}ms`", ephemeral=True)
    
    @app_commands.command(name="stats", description="Show server stats (Admin only)")
    @app_commands.checks.has_permissions(administrator=True)
    async def slash_stats(self, interaction: discord.Interaction):
        config = await db.get_server_config(interaction.guild_id)
        schedule = await db.get_event_schedule(interaction.guild_id)
        
        embed = discord.Embed(title=f"📊 {interaction.guild.name} Stats", color=0x34495e)
        
        if config:
            bubble = interaction.guild.get_channel(config.get("bubble_channel_id", 0))
            bf = interaction.guild.get_channel(config.get("battlefield_channel_id", 0))
            embed.add_field(name="Bubble Channel", value=bubble.mention if bubble else "Not set", inline=True)
            embed.add_field(name="Battlefield Channel", value=bf.mention if bf else "Not set", inline=True)
            embed.add_field(name="Setup", value="✅" if config.get("setup_complete") else "❌", inline=True)
        
        if schedule:
            embed.add_field(name="Current Event", value=schedule.get("current_event", "Unknown").upper(), inline=False)
            embed.add_field(name="Next Date", value=schedule.get("next_event_date", "Unknown"), inline=False)
        
        await interaction.response.send_message(embed=embed, ephemeral=True)
    
    @app_commands.command(name="broadcast", description="Send DM to all members (Admin only)")
    @app_commands.checks.has_permissions(administrator=True)
    @app_commands.describe(message="Message to broadcast")
    async def slash_broadcast(self, interaction: discord.Interaction, message: str):
        await interaction.response.defer(ephemeral=True)
        sent = 0
        failed = 0
        for member in interaction.guild.members:
            if member.bot:
                continue
            try:
                await member.send(f"📢 **Message from {interaction.guild.name}:**\n{message}")
                sent += 1
            except:
                failed += 1
        await interaction.followup.send(f"✅ Sent to {sent} | ❌ Failed: {failed}", ephemeral=True)

async def setup(bot: commands.Bot):
    await bot.add_cog(Admin(bot))
