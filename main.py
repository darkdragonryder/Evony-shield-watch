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


# =========================================================
# ENV LOAD
# =========================================================

load_dotenv()


# =========================================================
# INTENTS
# =========================================================

intents = discord.Intents.default()
intents.members = True
intents.message_content = True
intents.reactions = True
intents.guilds = True
intents.dm_messages = True


# =========================================================
# BOT CLASS
# =========================================================

class ShieldWatchBot(commands.Bot):

    def __init__(self):

        super().__init__(
            command_prefix="!",
            intents=intents,
            help_command=None
        )

        self.telegram = TelegramBotService()

    # =====================================================
    # STARTUP
    # =====================================================

    async def setup_hook(self):

        print("\n=================================================")
        print(" INITIALIZING DATABASE")
        print("=================================================\n")

        await db.init()
        print("✅ Database initialized")

        # -------------------------------------------------
        # LOAD COGS
        # -------------------------------------------------

        cogs = [
            "cogs.setup",
            "cogs.events",
            "cogs.custom_events",
            "cogs.reminders",
            "cogs.admin",
        ]

        print("\n=================================================")
        print(" LOADING COGS")
        print("=================================================\n")

        for cog in cogs:
            try:
                await self.load_extension(cog)
                print(f"✅ Loaded {cog}")
            except Exception as e:
                print(f"❌ Failed {cog}: {e}")

        # -------------------------------------------------
        # START TELEGRAM (FIXED)
        # -------------------------------------------------

        print("\n=================================================")
        print(" STARTING TELEGRAM")
        print("=================================================\n")

        try:
            loop = asyncio.get_event_loop()
            loop.run_in_executor(None, self.telegram.run)
            print("✅ Telegram bot started (background thread)")
        except Exception as e:
            print(f"❌ Telegram failed: {e}")

        # -------------------------------------------------
        # SYNC SLASH COMMANDS
        # -------------------------------------------------

        print("\n=================================================")
        print(" SYNCING SLASH COMMANDS")
        print("=================================================\n")

        try:
            await self.tree.sync()
            print("✅ Slash commands synced")
        except Exception as e:
            print(f"❌ Slash sync failed: {e}")

    # =====================================================
    # READY EVENT
    # =====================================================

    async def on_ready(self):

        print("\n=================================================")
        print(" BOT ONLINE")
        print("=================================================\n")

        print(f"🛡️ Logged in as: {self.user}")
        print(f"📊 Servers: {len(self.guilds)}")
        print(f"👥 Users: {len(self.users)}")

        await self.change_presence(
            activity=discord.Activity(
                type=discord.ActivityType.watching,
                name="SVS / KE Events | /help"
            )
        )

    # =====================================================
    # CLEANUP FIX
    # =====================================================

    async def on_member_remove(self, member: discord.Member):

        if member.bot:
            return

        print(f"🗑️ Cleaning member data: {member.id}")

        try:
            await db.delete_user_data(member.id)
            print(f"✅ Removed database data for {member.id}")
        except Exception as e:
            print(f"❌ Failed cleanup: {e}")

    async def on_member_ban(self, guild: discord.Guild, user: discord.User):

        print(f"🔨 User banned: {user.id}")

        try:
            await db.delete_user_data(user.id)
            print("✅ Ban cleanup completed")
        except Exception as e:
            print(f"❌ Ban cleanup failed: {e}")

    # =====================================================
    # SHUTDOWN
    # =====================================================

    async def close(self):

        print("\n=================================================")
        print(" SHUTTING DOWN")
        print("=================================================\n")

        try:
            await self.telegram.stop()
        except Exception:
            pass

        await super().close()


# =========================================================
# BOT INSTANCE
# =========================================================

bot = ShieldWatchBot()


# =========================================================
# ERROR HANDLER
# =========================================================

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


# =========================================================
# MAIN
# =========================================================

async def main():
    async with bot:
        await bot.start(Config.TOKEN)


if __name__ == "__main__":
    asyncio.run(main())
