"""

 Evony Shield Watch
 Events System (FINAL CLEAN ALIGNMENT)
 - Scheduler = triggers only
 - EventEngine = state only
 - Embeds = display only

"""

import discord
from discord.ext import commands
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger

from database import db
from config import Config
from utils.embeds import Embeds
from services.event_engine import EventEngine


class Events(commands.Cog):

    def __init__(self, bot: commands.Bot):

        self.bot = bot
        self.scheduler = AsyncIOScheduler()
        self.scheduler.start()

        self._register_jobs()

    # =====================================================
    # SCHEDULER SETUP (NO BUSINESS LOGIC HERE)
    # =====================================================

    def _register_jobs(self):

        # -------------------------------
        # SVS PURGE WARNING
        # -------------------------------
        self.scheduler.add_job(
            self.svs_purge_warning,
            CronTrigger(day_of_week="fri", hour=15, minute=21),
            id="svs_purge_warning",
            replace_existing=True
        )

        # -------------------------------
        # GENERAL WARNING
        # -------------------------------
        self.scheduler.add_job(
            self.general_warning,
            CronTrigger(day_of_week="fri", hour=16, minute=0),
            id="general_warning",
            replace_existing=True
        )

        # -------------------------------
        # EVENT START
        # -------------------------------
        self.scheduler.add_job(
            self.event_start,
            CronTrigger(day_of_week="fri", hour=17, minute=0),
            id="event_start",
            replace_existing=True
        )

        # -------------------------------
        # WEEK ROTATION
        # -------------------------------
        self.scheduler.add_job(
            self.rotate_week,
            CronTrigger(day_of_week="fri", hour=17, minute=1),
            id="rotate_week",
            replace_existing=True
        )

    # =====================================================
    # SVS PURGE WARNING
    # =====================================================

    async def svs_purge_warning(self):

        for guild in self.bot.guilds:

            event = await EventEngine.get_current_event(guild.id)

            if event != Config.SVS:
                continue

            config = await db.get_server_config(guild.id)
            if not config:
                continue

            channel = guild.get_channel(config.get("bubble_channel_id", 0))
            if not channel:
                continue

            embed = Embeds.shield_alert(
                event_type=Config.SVS,
                phase="svs_purge_warning"
            )

            await channel.send("@everyone", embed=embed)

    # =====================================================
    # GENERAL WARNING
    # =====================================================

    async def general_warning(self):

        for guild in self.bot.guilds:

            event = await EventEngine.get_current_event(guild.id)

            config = await db.get_server_config(guild.id)
            if not config:
                continue

            channel = guild.get_channel(config.get("bubble_channel_id", 0))
            if not channel:
                continue

            phase = "ke_warning" if event == Config.KE else "svs_warning"

            embed = Embeds.shield_alert(
                event_type=event,
                phase=phase
            )

            await channel.send("@everyone", embed=embed)

    # =====================================================
    # EVENT START
    # =====================================================

    async def event_start(self):

        for guild in self.bot.guilds:

            event = await EventEngine.get_current_event(guild.id)

            config = await db.get_server_config(guild.id)
            if not config:
                continue

            channel = guild.get_channel(config.get("battlefield_channel_id", 0))
            if not channel:
                continue

            embed = Embeds.event_start_notice(event)

            await channel.send("@everyone", embed=embed)

    # =====================================================
    # WEEK ROTATION (ONLY STATE CHANGE)
    # =====================================================

    async def rotate_week(self):

        for guild in self.bot.guilds:

            new_event = await EventEngine.toggle_event(guild.id)

            config = await db.get_server_config(guild.id)
            if not config:
                continue

            channel = guild.get_channel(config.get("battlefield_channel_id", 0))

            if channel:

                embed = discord.Embed(
                    title="🔄 Weekly Rotation",
                    description=f"Next cycle event: **{new_event.upper()}**",
                    color=0x3498db
                )

                await channel.send(embed=embed)


async def setup(bot: commands.Bot):
    await bot.add_cog(Events(bot))
