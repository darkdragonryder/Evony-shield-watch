"""
SVS/KE Auto Rotation - FIXED (Proper Event Behavior)
Stable reset-based system (production safe)
"""

import discord
from discord.ext import commands
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger

from database import db
from config import Config


class Events(commands.Cog):

    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.scheduler = AsyncIOScheduler()
        self.scheduler.start()

        self._schedule_jobs()

    # =====================================================
    # SCHEDULER (RESET BASED ONLY)
    # =====================================================

    def _schedule_jobs(self):

        # 1) 1h 39m before reset → SVS purge warning ONLY
        self.scheduler.add_job(
            self.svs_purge_warning,
            CronTrigger(day_of_week="fri", hour=15, minute=21),
            id="svs_purge",
            replace_existing=True
        )

        # 2) 1 hour before reset → main warning (SVS or KE depending week)
        self.scheduler.add_job(
            self.hour_warning,
            CronTrigger(day_of_week="fri", hour=16, minute=0),
            id="hour_warning",
            replace_existing=True
        )

        # 3) RESET START → event start message
        self.scheduler.add_job(
            self.reset_start,
            CronTrigger(day_of_week="fri", hour=17, minute=0),
            id="reset_start",
            replace_existing=True
        )

        # 4) ROTATE AFTER RESET (SAFE DELAY)
        self.scheduler.add_job(
            self.rotate_event,
            CronTrigger(day_of_week="fri", hour=17, minute=2),
            id="rotate",
            replace_existing=True
        )

        # 5) INIT SERVERS
        self.scheduler.add_job(
            self.init_servers,
            CronTrigger(hour=0, minute=5),
            id="init_servers",
            replace_existing=True
        )

    # =====================================================
    # HELPERS
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

            await channel.send(
                "@everyone ⚔️ PURGE IN 39 MINUTES — PUT UP BUBBLE NOW!"
            )

    # =====================================================
    # PHASE 2 - 1 HOUR WARNING (DIFFERENT MESSAGE BY EVENT)
    # =====================================================

    async def hour_warning(self):

        for guild in self.bot.guilds:

            event = await self.get_event(guild.id)

            config = await db.get_server_config(guild.id)
            if not config:
                continue

            channel = guild.get_channel(config.get("bubble_channel_id", 0))
            if not channel:
                continue

            if event == Config.SVS:
                msg = "🛡️ SVS IN 1 HOUR — Bubble up if not fighting!"
            else:
                msg = "⚔️ KE IN 1 HOUR — Bubble up, all tiles safe soon!"

            await channel.send(f"@everyone {msg}")

    # =====================================================
    # PHASE 3 - RESET START MESSAGE
    # =====================================================

    async def reset_start(self):

        for guild in self.bot.guilds:

            event = await self.get_event(guild.id)

            config = await db.get_server_config(guild.id)
            if not config:
                continue

            channel = guild.get_channel(config.get("battlefield_channel_id", 0))
            if not channel:
                continue

            if event == Config.SVS:
                msg = "🔥 SVS STARTED — STAY BUBBLED OR FIGHT!"
            else:
                msg = "🔥 KE STARTED — ALL TILES & RELICS SAFE!"

            await channel.send(f"@everyone {msg}")

    # =====================================================
    # PHASE 4 - ROTATION
    # =====================================================

    async def rotate_event(self):

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

            channel = guild.get_channel(config.get("battlefield_channel_id", 0))
            if channel:

                await channel.send(
                    f"🔄 Next week event set to **{new_event.upper()}**"
                )


# =====================================================
# SETUP
# =====================================================

async def setup(bot: commands.Bot):
    await bot.add_cog(Events(bot))
