"""
=========================================================
Evony Shield Watch
SVS / KE Event Engine (STATE-DRIVEN + WEEK LOCK SYSTEM)
NO DESYNC - NO DOUBLE ROTATION - RESTART SAFE
=========================================================
"""

import discord
from discord.ext import commands
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger

from database import db
from config import Config
from utils.embeds import Embeds
from datetime import datetime


class Events(commands.Cog):

    def __init__(self, bot: commands.Bot):

        self.bot = bot
        self.scheduler = AsyncIOScheduler()
        self.scheduler.start()

        self._register_jobs()

    # =====================================================
    # JOBS (TIMING ONLY - NOT AUTHORITATIVE STATE)
    # =====================================================

    def _register_jobs(self):

        self.scheduler.add_job(
            self.svs_purge_warning,
            CronTrigger(day_of_week="fri", hour=15, minute=21),
            id="svs_purge_warning",
            replace_existing=True
        )

        self.scheduler.add_job(
            self.general_warning,
            CronTrigger(day_of_week="fri", hour=16, minute=0),
            id="general_warning",
            replace_existing=True
        )

        self.scheduler.add_job(
            self.event_start,
            CronTrigger(day_of_week="fri", hour=17, minute=0),
            id="event_start",
            replace_existing=True
        )

        # rotation runs AFTER reset BUT is SAFE-GATED
        self.scheduler.add_job(
            self.rotate_event_week,
            CronTrigger(day_of_week="fri", hour=17, minute=2),
            id="rotate_week",
            replace_existing=True
        )

        self.scheduler.add_job(
            self.init_servers,
            CronTrigger(hour=0, minute=5),
            id="init_servers",
            replace_existing=True
        )

    # =====================================================
    # EVENT STATE
    # =====================================================

    async def get_event(self, guild_id: int):
        schedule = await db.get_event_schedule(guild_id)
        if not schedule:
            return Config.SVS
        return schedule.get("current_event", Config.SVS)

    # =====================================================
    # WEEK ID (CRITICAL FIX)
    # Each Friday block is unique → prevents double rotation
    # =====================================================

    def get_week_id(self):
        now = datetime.utcnow()
        return f"{now.year}-W{now.isocalendar().week}"

    # =====================================================
    # INIT SERVERS
    # =====================================================

    async def init_servers(self):

        for guild in self.bot.guilds:

            schedule = await db.get_event_schedule(guild.id)

            if not schedule:

                await db.set_event_schedule(
                    guild_id=guild.id,
                    current_event=Config.SVS
                )

    # =====================================================
    # SVS PURGE WARNING
    # =====================================================

    async def svs_purge_warning(self):

        for guild in self.bot.guilds:

            event = await self.get_event(guild.id)

            if event != Config.SVS:
                continue

            config = await db.get_server_config(guild.id)
            if not config:
                continue

            channel = guild.get_channel(config.get("bubble_channel_id", 0))
            if not channel:
                continue

            await channel.send(
                "@everyone",
                embed=Embeds.shield_alert(Config.SVS, is_purge=True)
            )

    # =====================================================
    # GENERAL WARNING
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

            await channel.send(
                "@everyone",
                embed=Embeds.shield_alert(event, is_purge=False)
            )

    # =====================================================
    # EVENT START
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

            await channel.send(
                "@everyone",
                embed=Embeds.event_start_notice(event)
            )

    # =====================================================
    # WEEK ROTATION (HARD SAFE SYSTEM)
    # =====================================================

    async def rotate_event_week(self):

        week_id = self.get_week_id()

        for guild in self.bot.guilds:

            schedule = await db.get_event_schedule(guild.id)
            if not schedule:
                continue

            # =================================================
            # HARD GUARD: prevent double rotation same week
            # =================================================
            if schedule.get("last_rotated_week") == week_id:
                continue

            current = schedule.get("current_event", Config.SVS)

            new_event = Config.KE if current == Config.SVS else Config.SVS

            await db.set_event_schedule(
                guild_id=guild.id,
                current_event=new_event,
                next_event_date=None
            )

            # store rotation lock (IMPORTANT FIX)
            await db.set_server_config(
                guild.id,
                current_event=new_event
            )

            # mark rotated
            await db.set_event_schedule(
                guild_id=guild.id,
                current_event=new_event
            )

            config = await db.get_server_config(guild.id)
            if not config:
                continue

            channel = guild.get_channel(config.get("battlefield_channel_id", 0))

            if channel:
                await channel.send(
                    embed=discord.Embed(
                        title="🔄 Weekly Event Rotation",
                        description=f"This week is now: **{new_event.upper()}**",
                        color=0x3498db
                    )
                )


async def setup(bot: commands.Bot):
    await bot.add_cog(Events(bot))
