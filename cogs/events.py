"""
SVS/KE Auto Rotation - FINAL RESET-TOGGLE SYSTEM
Fully aligned with event_week_toggle (DB source of truth)
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
    # EVENT RESOLUTION (SOURCE OF TRUTH)
    # =====================================================

    async def get_current_event(self, guild_id: int) -> str:
        """
        Returns SVS or KE based on DB toggle.
        """
        config = await db.get_server_config(guild_id)
        if not config:
            return Config.SVS

        toggle = config.get("event_week_toggle", 0)

        return Config.SVS if toggle == 1 else Config.KE

    # =====================================================
    # INIT NEW SERVERS
    # =====================================================

    async def init_new_servers(self):
        for guild in self.bot.guilds:
            config = await db.get_server_config(guild.id)
            if not config:
                await db.set_server_config(
                    guild_id=guild.id,
                    current_event=Config.SVS,
                    event_week_toggle=0
                )

    # =====================================================
    # SCHEDULER SETUP (ONLY RESET EVENTS)
    # =====================================================

    def _register_jobs(self):

        # -------------------------------------------------
        # FRIDAY 15:21 → SVS PURGE WARNING (ONLY IF SVS WEEK)
        # -------------------------------------------------
        self.scheduler.add_job(
            self.svs_purge_warning,
            CronTrigger(day_of_week="fri", hour=15, minute=21),
            id="svs_purge_warning",
            replace_existing=True
        )

        # -------------------------------------------------
        # FRIDAY 16:00 → 1 HOUR WARNING (ALL EVENTS)
        # -------------------------------------------------
        self.scheduler.add_job(
            self.hour_warning,
            CronTrigger(day_of_week="fri", hour=16, minute=0),
            id="fri_hour_warning",
            replace_existing=True
        )

        # -------------------------------------------------
        # MONDAY 16:00 → 1 HOUR WARNING (ALL EVENTS)
        # -------------------------------------------------
        self.scheduler.add_job(
            self.hour_warning,
            CronTrigger(day_of_week="mon", hour=16, minute=0),
            id="mon_hour_warning",
            replace_existing=True
        )

        # -------------------------------------------------
        # FRIDAY RESET START → EVENT START + FLIP
        # -------------------------------------------------
        self.scheduler.add_job(
            self.reset_start,
            CronTrigger(day_of_week="fri", hour=17, minute=0),
            id="fri_reset_start",
            replace_existing=True
        )

        # -------------------------------------------------
        # MONDAY RESET START → EVENT START + FLIP
        # -------------------------------------------------
        self.scheduler.add_job(
            self.reset_start,
            CronTrigger(day_of_week="mon", hour=17, minute=0),
            id="mon_reset_start",
            replace_existing=True
        )

        # -------------------------------------------------
        # SERVER INIT
        # -------------------------------------------------
        self.scheduler.add_job(
            self.init_new_servers,
            CronTrigger(hour=0, minute=5),
            id="init_servers",
            replace_existing=True
        )

    # =====================================================
    # WARNING: SVS PURGE ONLY
    # =====================================================

    async def svs_purge_warning(self):

        for guild in self.bot.guilds:

            event = await self.get_current_event(guild.id)

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
    # WARNING: 1 HOUR (ALL EVENTS)
    # =====================================================

    async def hour_warning(self):

        for guild in self.bot.guilds:

            event = await self.get_current_event(guild.id)

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
    # RESET START + FLIP WEEK
    # =====================================================

    async def reset_start(self):

        for guild in self.bot.guilds:

            config = await db.get_server_config(guild.id)
            if not config:
                continue

            event = await self.get_current_event(guild.id)

            battlefield = guild.get_channel(
                config.get("battlefield_channel_id", 0)
            )

            # -------------------------------------------------
            # EVENT START MESSAGE
            # -------------------------------------------------
            if battlefield:
                embed = Embeds.event_start_notice(event)
                await battlefield.send("@everyone", embed=embed)

            # -------------------------------------------------
            # FLIP WEEK (IMPORTANT)
            # -------------------------------------------------
            current_toggle = config.get("event_week_toggle", 0)
            new_toggle = 1 - int(current_toggle)

            await db.set_server_config(
                guild_id=guild.id,
                event_week_toggle=new_toggle
            )

            # -------------------------------------------------
            # LOG NEW STATE
            # -------------------------------------------------
            print(
                f"[EVENT FLIP] Guild {guild.id} "
                f"Toggle {current_toggle} → {new_toggle} "
                f"(Now {'SVS' if new_toggle == 1 else 'KE'})"
            )


# =====================================================
# SETUP
# =====================================================

async def setup(bot: commands.Bot):
    await bot.add_cog(Events(bot))
