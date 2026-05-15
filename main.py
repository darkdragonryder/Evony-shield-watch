"""
=========================================================
 Evony Shield Watch
 Main Entry Point
 Stable Oracle VM Production Version
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

from services.telegram_bot import TelegramBotService


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

        # Telegram bridge
        self.telegram = TelegramBotService()

        # Runtime state
        self.telegram_task = None

    # =====================================================
    # STARTUP
    # =====================================================

    async def setup_hook(self):

        print("\n=================================================")
        print(" INITIALIZING DATABASE")
        print("=================================================\n")

        try:
            await db.init()
            print("✅ Database initialized")

        except Exception as e:
            print(f"❌ Database initialization failed: {e}")
            raise

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
                print(f"❌ Failed to load {cog}")
                print(e)

        # -------------------------------------------------
        # SYNC COMMANDS
        # -------------------------------------------------

        print("\n=================================================")
        print(" SYNCING SLASH COMMANDS")
        print("=================================================\n")

        try:

            synced = await self.tree.sync()

            print(f"✅ Synced {len(synced)} slash commands")

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

        # -------------------------------------------------
        # PRESENCE
        # -------------------------------------------------

        try:

            await self.change_presence(

                activity=discord.Activity(
                    type=discord.ActivityType.watching,
                    name="SVS / KE Events | /help"
                )

            )

        except Exception as e:
            print(f"⚠️ Failed to set presence: {e}")

        # -------------------------------------------------
        # START TELEGRAM
        # -------------------------------------------------

        if not self.telegram_task:

            print("\n=================================================")
            print(" STARTING TELEGRAM")
            print("=================================================\n")

            try:

                self.telegram_task = asyncio.create_task(
                    self.telegram.start_async()
                )

                print("✅ Telegram startup task created")

            except Exception as e:

                print("❌ Telegram startup failed")
                print(e)

    # =====================================================
    # GUILD JOIN
    # =====================================================

    async def on_guild_join(self, guild: discord.Guild):

        print(f"➕ Joined server: {guild.name}")

        try:

            await db.set_server_config(
                guild_id=guild.id
            )

            print(f"✅ Initialized config for {guild.name}")

        except Exception as e:

            print(f"❌ Failed guild setup: {e}")

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

            print("✅ Ban cleanup completed")

        except Exception as e:

            print("❌ Ban cleanup failed")
            print(e)

    # =====================================================
    # GLOBAL ERROR HANDLER
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

        # Stop Telegram cleanly
        try:

            await self.telegram.stop_async()

        except Exception as e:

            print(f"⚠️ Telegram shutdown warning: {e}")

        # Cancel background task
        if self.telegram_task:

            self.telegram_task.cancel()

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
            "❌ You do not have permission to use this command.",
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
            "❌ You do not meet the requirements for this command.",
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
