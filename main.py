"""
=========================================================
 Evony Shield Watch
 Main Entry Point
=========================================================
"""

import asyncio
import discord

from discord.ext import commands
from dotenv import load_dotenv

from database import db
from config import Config

from services.telegram_bot import TelegramBotService


load_dotenv()


intents = discord.Intents.default()
intents.members = True
intents.message_content = True
intents.reactions = True
intents.guilds = True
intents.dm_messages = True


class ShieldWatchBot(commands.Bot):

    def __init__(self):

        super().__init__(
            command_prefix="!",
            intents=intents,
            help_command=None
        )

        self.telegram = TelegramBotService()

    async def setup_hook(self):

        print("\n=================================================")
        print(" INITIALIZING DATABASE")
        print("=================================================\n")

        await db.init()

        print("✅ Database initialized")

        print("\n=================================================")
        print(" LOADING COGS")
        print("=================================================\n")

        cogs = [
            "cogs.setup",
            "cogs.events",
            "cogs.custom_events",
            "cogs.reminders",
            "cogs.admin",
        ]

        for cog in cogs:
            try:
                await self.load_extension(cog)
                print(f"✅ Loaded {cog}")
            except Exception as e:
                print(f"❌ Failed {cog}: {e}")

        print("\n=================================================")
        print(" STARTING TELEGRAM")
        print("=================================================\n")

        try:
            asyncio.create_task(self.telegram.start_async())
            print("✅ Telegram bot started (background task)")
        except Exception as e:
            print(f"❌ Telegram failed: {e}")

        print("\n=================================================")
        print(" SYNCING SLASH COMMANDS")
        print("=================================================\n")

        try:
            await self.tree.sync()
            print("✅ Slash commands synced")
        except Exception as e:
            print(f"❌ Slash sync failed: {e}")

    async def on_ready(self):

        print("\n=================================================")
        print(" BOT ONLINE")
        print("=================================================\n")

        print(f"🛡️ Logged in as: {self.user}")
        print(f"📊 Servers: {len(self.guilds)}")

        await self.change_presence(
            activity=discord.Activity(
                type=discord.ActivityType.watching,
                name="SVS / KE Events | /help"
            )
        )

    async def close(self):

        print("\n=================================================")
        print(" SHUTTING DOWN")
        print("=================================================\n")

        try:
            await self.telegram.stop()
        except Exception:
            pass

        await super().close()


bot = ShieldWatchBot()


@bot.tree.error
async def on_app_command_error(interaction: discord.Interaction, error):

    if isinstance(error, discord.app_commands.MissingPermissions):
        return await interaction.response.send_message(
            "❌ No permission.",
            ephemeral=True
        )

    if isinstance(error, discord.app_commands.CheckFailure):
        return await interaction.response.send_message(
            "❌ Check failed.",
            ephemeral=True
        )

    print("❌ COMMAND ERROR:", error)

    try:
        if not interaction.response.is_done():
            await interaction.response.send_message(
                "❌ Unexpected error.",
                ephemeral=True
            )
    except Exception:
        pass


async def main():

    async with bot:
        await bot.start(Config.TOKEN)


if __name__ == "__main__":
    asyncio.run(main())
