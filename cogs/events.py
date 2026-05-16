"""
=========================================================
Evony Shield Watch
SVS / KE Event Engine (STATE-DRIVEN SYSTEM)
NO DESYNC - NO CRON RELIANCE FOR LOGIC
=========================================================
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

        self._register_jobs()

    # =====================================================
    # JOB REGISTRATION (TIMING ONLY, NO GAME LOGIC)
    # =====================================================

    def _register_jobs(self):

        # -------------------------------------------------
        # 39 MIN WARNING (SVS ONLY)
        # -------------------------------------------------
        self.scheduler.add_job(
            self.svs_purge_warning,
            CronTrigger(day_of_week="fri", hour=15, minute=21),
            id="svs_purge_warning",
            replace_existing=True
        )

        # -------------------------------------------------
        # 1 HOUR WARNING (SVS + KE)
        # -------------------------------------------------
        self.scheduler.add_job(
            self.general_warning,
            CronTrigger(day_of_week="fri", hour=16, minute=0),
            id="general_warning",
            replace_existing=True
        )

        # -------------------------------------------------
        # RESET START (EVENT BEGINS)
        # -------------------------------------------------
        self.scheduler.add_job(
            self.event_start,
            CronTrigger(day_of_week="fri", hour=17, minute=0),
            id="event_start",
            replace_existing=True
        )

        # -------------------------------------------------
        # WEEK ROTATION (STATE CHANGE ONLY)
        # -------------------------------------------------
        self.scheduler.add_job(
            self.rotate_event_week,
            CronTrigger(day_of_week="fri", hour=17, minute=1),
            id="rotate_week",
            replace_existing=True
        )

        # -------------------------------------------------
        # INIT SERVERS
        # -------------------------------------------------
        self.scheduler.add_job(
            self.init_servers,
            CronTrigger(hour=0, minute=5),
            id="init_servers",
            replace_existing=True
        )

    # =====================================================
    # EVENT STATE (SOURCE OF TRUTH)
    # =====================================================

    async def get_event(self, guild_id: int):

        schedule = await db.get_event_schedule(guild_id)

        if not schedule:
            return Config.SVS

        return schedule.get("current_event", Config.SVS)

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
    # PHASE 1 - SVS PURGE WARNING ONLY
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

            embed = Embeds.shield_alert(
                event_type=Config.SVS,
                is_purge=True
            )

            await channel.send("@everyone", embed=embed)

    # =====================================================
    # PHASE 2 - GENERAL WARNING (SVS OR KE)
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
                is_purge=False
            )

            await channel.send("@everyone", embed=embed)

    # =====================================================
    # PHASE 3 - EVENT START (RESET MOMENT)
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
    # PHASE 4 - WEEK ROTATION (CRITICAL STATE CHANGE)
    # =====================================================

    async def rotate_event_week(self):

        for guild in self.bot.guilds:

            schedule = await db.get_event_schedule(guild.id)
            if not schedule:
                continue

            current = schedule.get("current_event", Config.SVS)

            # STRICT TOGGLE RULE (NO DRIFT POSSIBLE)
            new_event = Config.KE if current == Config.SVS else Config.SVS

            await db.set_event_schedule(
                guild_id=guild.id,
                current_event=new_event
            )

            config = await db.get_server_config(guild.id)
            if not config:
                continue

            channel = guild.get_channel(config.get("battlefield_channel_id", 0))

            if channel:

                embed = discord.Embed(
                    title="🔄 Weekly Event Rotation",
                    description=f"Next week event is now: **{new_event.upper()}**",
                    color=0x3498db
                )

                await channel.send(embed=embed)


async def setup(bot: commands.Bot):
    await bot.add_cog(Events(bot))
