"""
=========================================================
 Evony Shield Watch
 Main Entry Point
 Oracle Cloud Free Tier Optimized
=========================================================

Features:
- Discord Slash Commands
- Auto SVS / KE Rotation
- Bubble Reminders
- Telegram Integration
- Event Check-ins
- Member Cleanup
- Dashboard Ready Structure
- Async Optimized

=========================================================
"""

# =========================================================
# IMPORTS
# =========================================================

import asyncio
import discord

from discord.ext import commands
from dotenv import load_dotenv

from database import db
from config import Config

# Telegram
from telegram_bot import TelegramBridge


# =========================================================
# LOAD ENVIRONMENT
# =========================================================

load_dotenv()


# =========================================================
# DISCORD INTENTS
# =========================================================

intents = discord.Intents.default()

intents.members = True
intents.message_content = True
intents.reactions = True
intents.guilds = True
intents.dm_messages = True


# =========================================================
# MAIN BOT CLASS
# =========================================================

class ShieldWatchBot(commands.Bot):

    def __init__(self):

        super().__init__(
            command_prefix="!",
            intents=intents,
            help_command=None
        )

        self.telegram = TelegramBridge(self)

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

            # Core
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

                print(f"❌ Failed {cog}")
                print(e)

        # -------------------------------------------------
        # START TELEGRAM
        # -------------------------------------------------

        print("\n=================================================")
        print(" STARTING TELEGRAM")
        print("=================================================\n")

        try:

            await self.telegram.start()

            print("✅ Telegram bridge online")

        except Exception as e:

            print("❌ Telegram failed")
            print(e)

        # -------------------------------------------------
        # SYNC COMMANDS
        # -------------------------------------------------

        print("\n=================================================")
        print(" SYNCING SLASH COMMANDS")
        print("=================================================\n")

        try:

            await self.tree.sync()

            print("✅ Slash commands synced")

        except Exception as e:

            print("❌ Slash sync failed")
            print(e)

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

        print("\n=================================================\n")

        await self.change_presence(

            activity=discord.Activity(
                type=discord.ActivityType.watching,
                name="SVS / KE Events | /help"
            )

        )

    # =====================================================
    # GUILD JOIN
    # =====================================================

    async def on_guild_join(self, guild: discord.Guild):

        print(f"➕ Joined server: {guild.name}")

        await db.set_server_config(
            guild_id=guild.id
        )

        await db.set_event_schedule(
            guild_id=guild.id,
            current_event=Config.SVS
        )

    # =====================================================
    # MEMBER JOIN
    # =====================================================

    async def on_member_join(self, member: discord.Member):

        if member.bot:
            return

        try:

            embed = discord.Embed(
                title="🛡️ Welcome to Shield Watch",
                description=(
                    "This server uses Evony Shield Watch.\n\n"
                    "You can link your Telegram account "
                    "to receive:\n\n"
                    "• Bubble reminders\n"
                    "• SVS / KE warnings\n"
                    "• Battlefield notifications\n"
                    "• Personal alerts\n\n"
                    "Use `/linktelegram` to begin."
                ),
                color=0x3498db
            )

            embed.add_field(
                name="📱 No Telegram?",
                value=(
                    "Download Telegram:\n"
                    "https://telegram.org/\n\n"
                    "Then create an account and run "
                    "`/linktelegram`."
                ),
                inline=False
            )

            embed.set_footer(
                text="Only you can see this message."
            )

            await member.send(embed=embed)

        except Exception:
            pass

    # =====================================================
    # MEMBER REMOVE
    # =====================================================

    async def on_member_remove(self, member: discord.Member):

        if member.bot:
            return

        print(f"🗑️ Cleaning member data: {member.id}")

        try:

            await db.delete_member_data(member.id)

            print(f"✅ Removed database data for {member.id}")

        except Exception as e:

            print(f"❌ Failed cleanup for {member.id}")
            print(e)

    # =====================================================
    # MEMBER BAN
    # =====================================================

    async def on_member_ban(
        self,
        guild: discord.Guild,
        user: discord.User
    ):

        print(f"🔨 User banned: {user.id}")

        try:

            await db.delete_member_data(user.id)

            print(f"✅ Ban cleanup completed")

        except Exception as e:

            print(f"❌ Ban cleanup failed")
            print(e)

    # =====================================================
    # ERROR HANDLER
    # =====================================================

    async def on_error(self, event_method, *args, **kwargs):

        print("\n=================================================")
        print(" GLOBAL ERROR")
        print("=================================================\n")

        print(f"Event: {event_method}")

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
# SLASH COMMAND ERRORS
# =========================================================

@bot.tree.error
async def on_app_command_error(
    interaction: discord.Interaction,
    error
):

    # -----------------------------------------------------
    # PERMISSIONS
    # -----------------------------------------------------

    if isinstance(
        error,
        discord.app_commands.MissingPermissions
    ):

        return await interaction.response.send_message(
            "❌ You do not have permission "
            "to use this command.",
            ephemeral=True
        )

    # -----------------------------------------------------
    # CHECK FAILURES
    # -----------------------------------------------------

    elif isinstance(
        error,
        discord.app_commands.CheckFailure
    ):

        return await interaction.response.send_message(
            "❌ You do not meet the requirements "
            "for this command.",
            ephemeral=True
        )

    # -----------------------------------------------------
    # UNKNOWN
    # -----------------------------------------------------

    print("\n=================================================")
    print(" COMMAND ERROR")
    print("=================================================\n")

    print(error)

    try:

        if not interaction.response.is_done():

            await interaction.response.send_message(
                "❌ An unexpected error occurred.",
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


# =========================================================
# ENTRY
# =========================================================

if __name__ == "__main__":

    asyncio.run(main())
