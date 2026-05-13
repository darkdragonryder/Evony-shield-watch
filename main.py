"""
Evony Shield Watch - Main Entry Point
Optimized for Oracle Cloud Free Tier VM
"""
import os
import asyncio
import discord
from discord.ext import commands
from dotenv import load_dotenv
from database import db
from config import Config

load_dotenv()

intents = discord.Intents.default()
intents.members = True
intents.message_content = True
intents.reactions = True

class ShieldWatchBot(commands.Bot):
    def __init__(self):
        super().__init__(
            command_prefix="!",  # Fallback prefix (not used, all slash)
            intents=intents,
            help_command=None
        )
    
    async def setup_hook(self):
        # Initialize database
        await db.init()
        
        # Load cogs
        cogs = [
            "cogs.setup",
            "cogs.events",
            "cogs.custom_events",
            "cogs.reminders",
            "cogs.admin"
        ]
        for cog in cogs:
            try:
                await self.load_extension(cog)
                print(f"✅ Loaded {cog}")
            except Exception as e:
                print(f"❌ Failed {cog}: {e}")
        
        # Sync slash commands globally
        print("🔄 Syncing slash commands...")
        await self.tree.sync()
        print("✅ Slash commands synced!")
    
    async def on_ready(self):
        print(f"🛡️ Evony Shield Watch logged in as {self.user}")
        print(f"📊 Serving {len(self.guilds)} servers")
        await self.change_presence(
            activity=discord.Activity(
                type=discord.ActivityType.watching,
                name="for SVS/KE events | /help"
            )
        )
    
    async def on_guild_join(self, guild: discord.Guild):
        # Auto-init new servers
        await db.set_server_config(guild_id=guild.id)
        await db.set_event_schedule(guild_id=guild.id, current_event=Config.SVS)

bot = ShieldWatchBot()

@bot.tree.error
async def on_app_command_error(interaction: discord.Interaction, error: discord.app_commands.AppCommandError):
    if isinstance(error, discord.app_commands.MissingPermissions):
        await interaction.response.send_message("❌ You don't have permission for this command.", ephemeral=True)
    elif isinstance(error, discord.app_commands.CheckFailure):
        await interaction.response.send_message("❌ You don't meet the requirements for this command.", ephemeral=True)
    else:
        print(f"Command error: {error}")
        if not interaction.response.is_done():
            await interaction.response.send_message("❌ An error occurred.", ephemeral=True)

async def main():
    async with bot:
        await bot.start(Config.TOKEN)

if __name__ == "__main__":
    asyncio.run(main())
