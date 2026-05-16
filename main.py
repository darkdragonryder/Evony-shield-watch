"""
=========================================================
 Evony Shield Watch
 MAIN ENTRY POINT (PRODUCTION BOOTSTRAP)
 - Service init order controlled
 - No logic inside startup
 - Safe cog loading
=========================================================
"""

import discord
from discord.ext import commands
import asyncio
import logging

from config import Config
from database import db

from services.telegram_bot import TelegramBotService
from services.event_engine import EventEngine
from services.alert_router import NotificationRouter


# =========================================================
# BOT SETUP
# =========================================================

intents = discord.Intents.default()
intents.members = True
intents.guilds = True
intents.message_content = True


class EvonyBot(commands.Bot):

    def __init__(self):

        super().__init__(
            command_prefix="!",
            intents=intents
        )

        # -----------------------------
        # CORE SERVICES (SINGLETON STYLE)
        # -----------------------------

        self.telegram = TelegramBotService()
        self.router = NotificationRouter(self)

    # =====================================================
    # BOT READY EVENT
    # =====================================================

    async def on_ready(self):

        logging.info(f"Logged in as {self.user}")

        # -----------------------------
        # INIT DATABASE
        # -----------------------------
        await db.init()

        # -----------------------------
        # START TELEGRAM SERVICE
        # -----------------------------
        await self.telegram.start_async()

        # -----------------------------
        # INIT EVENT ENGINE STATE
        # -----------------------------
        await EventEngine.init_all_guilds(self)

        logging.info("Evony Shield Watch fully started")

    # =====================================================
    # COG LOADER
    # =====================================================

    async def setup_hook(self):

        await self.load_extension("cogs.setup")
        await self.load_extension("cogs.events")
        await self.load_extension("cogs.members")
        await self.load_extension("cogs.reminders")
        await self.load_extension("cogs.custom_events")
        await self.load_extension("cogs.admin")


# =========================================================
# START BOT
# =========================================================

async def main():

    bot = EvonyBot()

    async with bot:
        await bot.start(Config.BOT_TOKEN)


if __name__ == "__main__":
    asyncio.run(main())
