"""
=========================================================
Evony Shield Watch
MAIN ENTRY POINT (FINAL ORCHESTRATION CORE)
- SINGLE EVENT PIPELINE
- NO DUPLICATE LISTENERS
- SAFE STARTUP ORDER
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
intents.guilds = True
intents.message_content = True


# =========================================================
# BOT CORE
# =========================================================

class ShieldWatchBot(commands.Bot):

    def __init__(self):

        super().__init__(
            command_prefix="!",
            intents=intents,
            help_command=None
        )

        # SINGLE TELEGRAM INSTANCE
        self.telegram = TelegramBotService()
        self.telegram_task = None

        # PREVENT DOUBLE INIT
        self._ready_once = False

    # =====================================================
    # STARTUP HOOK (ORDER IS CRITICAL)
    # =====================================================

    async def setup_hook(self):

        print("\n=================================================")
        print(" DATABASE INIT")
        print("=================================================\n")

        await db.init()

        # -------------------------------------------------
        # LOAD COGS (ORDERED PIPELINE)
        # -------------------------------------------------

        cogs = [

            # CORE SYSTEMS FIRST
            "cogs.setup",
            "cogs.events",

            # MEMBER + LIFECYCLE
            "cogs.members",

            # FEATURES
            "cogs.reminders",
            "cogs.custom_events",
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
        # SYNC SLASH COMMANDS
        # -------------------------------------------------

        try:
            synced = await self.tree.sync()
            print(f"✅ Synced {len(synced)} commands")
        except Exception as e:
            print(f"❌ Slash sync failed: {e}")

    # =====================================================
    # READY EVENT (SAFE SINGLE RUN)
    # =====================================================

    async def on_ready(self):

        if self._ready_once:
            return

        self._ready_once = True

        print("\n=================================================")
        print(" BOT ONLINE")
        print("=================================================\n")

        print(f"Logged in as: {self.user}")
        print(f"Servers: {len(self.guilds)}")

        # -------------------------------------------------
        # PRESENCE
        # -------------------------------------------------

        await self.change_presence(
            activity=discord.Activity(
                type=discord.ActivityType.watching,
                name="SVS / KE Events | /help"
            )
        )

        # -------------------------------------------------
        # TELEGRAM START (ONLY ONCE)
        # -------------------------------------------------

        if not self.telegram_task:

            self.telegram_task = asyncio.create_task(
                self.telegram.start_async()
            )

            print("📲 Telegram started")

        # -------------------------------------------------
        # ENSURE GUILD SETUP EXISTS
        # (THIS FIXES LATE INSTALL / SATURDAY INSTALL ISSUE)
        # -------------------------------------------------

        await self._ensure_guilds_ready()

    # =====================================================
    # AUTO GUILD INITIALISATION (CRITICAL FIX)
    # =====================================================

    async def _ensure_guilds_ready(self):

        for guild in self.guilds:

            config = await db.get_server_config(guild.id)

            # IF FIRST TIME INSTALL OR MISSING SETUP
            if not config or not config.get("setup_complete"):

                print(f"🛠️ Auto-initialising guild: {guild.name}")

                await db.set_server_config(
                    guild_id=guild.id,
                    setup_complete=0
                )

                # trigger setup flow automatically
                # (safe: only sends message, no duplication risk)
                await self._send_setup_prompt(guild)

    # =====================================================
    # AUTO SETUP PROMPT
    # =====================================================

    async def _send_setup_prompt(self, guild: discord.Guild):

        channel = next(
            (c for c in guild.text_channels
             if c.permissions_for(guild.me).send_messages),
            None
        )

        if not channel:
            return

        embed = discord.Embed(
            title="🛡️ Evony Shield Watch Setup Required",
            description=(
                "Welcome to Shield Watch.\n\n"
                "Run `/setup` to configure:\n"
                "• Bubble channel\n"
                "• Battlefield channel\n"
                "• Current event (SVS / KE)\n\n"
                "⚠️ This is required before alerts activate."
            ),
            color=0x1abc9c
        )

        await channel.send(embed=embed)

    # =====================================================
    # CLEAN SHUTDOWN
    # =====================================================

    async def close(self):

        print("\n=================================================")
        print(" SHUTTING DOWN")
        print("=================================================\n")

        try:
            await self.telegram.stop_async()
        except:
            pass

        if self.telegram_task:
            self.telegram_task.cancel()

        await super().close()


# =========================================================
# BOT INSTANCE
# =========================================================

bot = ShieldWatchBot()


# =========================================================
# GLOBAL ERROR HANDLER
# =========================================================

@bot.tree.error
async def on_app_command_error(interaction: discord.Interaction, error):

    print("❌ COMMAND ERROR:", error)

    try:
        if not interaction.response.is_done():
            await interaction.response.send_message(
                "❌ Error occurred.",
                ephemeral=True
            )
    except:
        pass


# =========================================================
# MAIN
# =========================================================

async def main():
    async with bot:
        await bot.start(Config.TOKEN)


if __name__ == "__main__":
    asyncio.run(main())
