"""
=========================================================
 Evony Shield Watch
 Event System (STATE DRIVEN - NO DESYNC)
 Scheduler = TIMING ONLY / Engine = LOGIC
=========================================================
"""

import discord
from discord.ext import commands
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger

from config import Config
from database import db
from utils.embeds import Embeds
from services.event_engine import EventEngine


class Events(commands.Cog):

    def __init__(self, bot: commands.Bot):

        self.bot = bot
        self.scheduler = AsyncIOScheduler()
        self.scheduler.start()

        self._register_jobs()

    # =====================================================
    # SCHEDULER (TIMING ONLY — NO GAME LOGIC HERE)
    # =====================================================

    def _register_jobs(self):

        # -------------------------------------------------
        # 1 HOUR WARNING (ALL EVENTS)
        # -------------------------------------------------

        self.scheduler.add_job(
            self.general_warning,
            CronTrigger(day_of_week="fri", hour=16, minute=0),
            id="general_warning",
            replace_existing=True
        )

        # -------------------------------------------------
        # EVENT START (RESET MOMENT)
        # -------------------------------------------------

        self.scheduler.add_job(
            self.event_start,
            CronTrigger(day_of_week="fri", hour=17, minute=0),
            id="event_start",
            replace_existing=True
        )

        # -------------------------------------------------
        # WEEK ROTATION (STATE ONLY CHANGE)
        # -------------------------------------------------

        self.scheduler.add_job(
            self.rotate_week,
            CronTrigger(day_of_week="fri", hour=17, minute=1),
            id="rotate_week",
            replace_existing=True
        )

    # =====================================================
    # GET EVENT (SAFE SINGLE SOURCE)
    # =====================================================

    async def get_event(self, guild_id: int):
        return await EventEngine.get_current_event(guild_id)

    # =====================================================
    # GENERAL WARNING (SVS OR KE)
    # =====================================================

    async def general_warning(self):

        for guild in self.bot.guilds:

            event = await self.get_event(guild.id)

            config = await db.get_server_config(guild.id)
            if not config:
                continue

            channel = guild.get_channel(config.get("bubble_channel_id", 0))
            if not channel:
                continue

            embed = Embeds.shield_alert(
                event_type=event,
                phase="warning"
            )

            await channel.send("@everyone", embed=embed)

    # =====================================================
    # EVENT START (REAL TIME STATE BASED)
    # =====================================================

    async def event_start(self):

        for guild in self.bot.guilds:

            event = await self.get_event(guild.id)

            config = await db.get_server_config(guild.id)
            if not config:
                continue

            channel = guild.get_channel(config.get("battlefield_channel_id", 0))
            if not channel:
                continue

            embed = Embeds.event_start_notice(event)

            await channel.send("@everyone", embed=embed)

    # =====================================================
    # WEEK ROTATION (ONLY STATE CHANGE - NO LOGIC HERE)
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
                    description=f"Next cycle: **{new_event.upper()}**",
                    color=0x3498db
                )

                await channel.send(embed=embed)
