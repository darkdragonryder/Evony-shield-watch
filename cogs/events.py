"""
SVS/KE Auto Rotation - FIXED (Reset-Based System)
Clean single-scheduler architecture
"""

import discord
from discord.ext import commands
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger

from database import db
from config import Config
from utils.embeds import Embeds


class Events(commands.Cog):

    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.scheduler = AsyncIOScheduler()
        self.scheduler.start()

        self._schedule_jobs()

    # =====================================================
    # CORE SCHEDULER (ONLY 3 EVENTS)
    # =====================================================

    def _schedule_jobs(self):

        # 1) 1h 39m before reset → purge warning (SVS special)
        self.scheduler.add_job(
            self.warning_39_min,
            CronTrigger(day_of_week="fri", hour=15, minute=21),
            id="warning_39",
            replace_existing=True
        )

        # 2) 1 hour before reset → general warning
        self.scheduler.add_job(
            self.warning_1_hour,
            CronTrigger(day_of_week="fri", hour=16, minute=0),
            id="warning_1h",
            replace_existing=True
        )

        # 3) RESET START → event begins
        self.scheduler.add_job(
            self.reset_start,
            CronTrigger(day_of_week="fri", hour=17, minute=0),
            id="reset_start",
            replace_existing=True
        )

        # 4) WEEK ROTATION (AFTER RESET)
        self.scheduler.add_job(
            self.rotate_weekly_event,
            CronTrigger(day_of_week="fri", hour=17, minute=1),
            id="rotate_event",
            replace_existing=True
        )

        # 5) INIT NEW SERVERS
        self.scheduler.add_job(
            self.init_new_servers,
            CronTrigger(hour=0, minute=5),
            id="init_servers",
            replace_existing=True
        )

    # =====================================================
    # EVENT STATE HELPERS
    # =====================================================

    async def get_event(self, guild_id: int):
        schedule = await db.get_event_schedule(guild_id)
        if not schedule:
            return Config.SVS
        return schedule.get("current_event", Config.SVS)

    # =====================================================
    # INIT SERVERS
    # =====================================================

    async def init_new_servers(self):
        for guild in self.bot.guilds:
            schedule = await db.get_event_schedule(guild.id)
            if not schedule:
                await db.set_event_schedule(
                    guild_id=guild.id,
                    current_event=Config.SVS
                )

    # =====================================================
    # PHASE 1 - 39 MIN WARNING
    # =====================================================

    async def warning_39_min(self):
        for guild in self.bot.guilds:

            event = await self.get_event(guild.id)

            # Only SVS uses purge warning
            if event != Config.SVS:
                continue

            config = await db.get_server_config(guild.id)
            if not config:
                continue

            channel = guild.get_channel(config.get("bubble_channel_id", 0))
            if not channel:
                continue

            embed = Embeds.shield_alert(event_type=Config.SVS, is_purge=True)

            await channel.send("@everyone", embed=embed)

    # =====================================================
    # PHASE 2 - 1 HOUR WARNING
    # =====================================================

    async def warning_1_hour(self):
        for guild in self.bot.guilds:

            event = await self.get_event(guild.id)

            config = await db.get_server_config(guild.id)
            if not config:
                continue

            channel = guild.get_channel(config.get("bubble_channel_id", 0))
            if not channel:
                continue

            embed = Embeds.shield_alert(event_type=event, is_purge=False)

            await channel.send("@everyone", embed=embed)

    # =====================================================
    # PHASE 3 - RESET START
    # =====================================================

    async def reset_start(self):
        for guild in self.bot.guilds:

            event = await self.get_event(guild.id)

            config = await db.get_server_config(guild.id)
            if not config:
                continue

            battlefield = guild.get_channel(config.get("battlefield_channel_id", 0))
            if not battlefield:
                continue

            embed = Embeds.event_start_notice(event)

            await battlefield.send("@everyone", embed=embed)

    # =====================================================
    # PHASE 4 - WEEK ROTATION
    # =====================================================

    async def rotate_weekly_event(self):
        for guild in self.bot.guilds:

            schedule = await db.get_event_schedule(guild.id)
            if not schedule:
                continue

            current = schedule.get("current_event", Config.SVS)

            new_event = Config.KE if current == Config.SVS else Config.SVS

            await db.set_event_schedule(
                guild_id=guild.id,
                current_event=new_event
            )

            config = await db.get_server_config(guild.id)
            if not config:
                continue

            battlefield = guild.get_channel(config.get("battlefield_channel_id", 0))
            if battlefield:

                embed = discord.Embed(
                    title="🔄 Event Rotation",
                    description=f"Next week event: **{new_event.upper()}**",
                    color=0x3498db
                )

                await battlefield.send(embed=embed)


# =====================================================
# SETUP
# =====================================================

async def setup(bot: commands.Bot):
    await bot.add_cog(Events(bot))
