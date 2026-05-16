"""
=========================================================
SVS / KE Auto Rotation & Reminder System
Evony Shield Watch
=========================================================
"""

# =========================================================
# IMPORTS
# =========================================================

import discord
import pytz

from discord.ext import commands
from discord import app_commands

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger

from datetime import datetime, timedelta

from database import db
from config import Config
from utils.embeds import Embeds


# =========================================================
# EVENTS COG
# =========================================================

class Events(commands.Cog):

    def init(self, bot: commands.Bot):

        self.bot = bot

        # =====================================================
        # SCHEDULER
        # =====================================================

        self.scheduler = AsyncIOScheduler(
            timezone=pytz.timezone(Config.HOST_TIMEZONE)
        )

        self._schedule_jobs()

        if not self.scheduler.running:
            self.scheduler.start()

    # =====================================================
    # CLEANUP
    # =====================================================

    def cog_unload(self):

        if self.scheduler.running:
            self.scheduler.shutdown(wait=False)

    # =====================================================
    # SCHEDULE ALL JOBS
    # =====================================================

    def _schedule_jobs(self):

        reset_hour = Config.RESET_HOUR
        reset_minute = Config.RESET_MINUTE

        # -------------------------------------------------
        # SVS REMINDER 1
        # 1h39m before reset
        # Example:
        # Reset 5:00pm
        # Fires 3:21pm
        # -------------------------------------------------

        first_hour = reset_hour - 2
        first_minute = reset_minute + 21

        if first_minute >= 60:
            first_hour += 1
            first_minute -= 60

        self.scheduler.add_job(
            self.svs_first_warning,
            CronTrigger(
                day_of_week="fri",
                hour=first_hour,
                minute=first_minute
            ),
            id="svs_first_warning",
            replace_existing=True
        )

        # -------------------------------------------------
        # SVS PURGE WARNING
        # 1 hour before reset
        # -------------------------------------------------

        purge_hour = reset_hour - 1

        self.scheduler.add_job(
            self.svs_purge_warning,
            CronTrigger(
                day_of_week="fri",
                hour=purge_hour,
                minute=reset_minute
            ),
            id="svs_purge_warning",
            replace_existing=True
        )

        # -------------------------------------------------
        # KE WARNING
        # 1 hour before reset
        # -------------------------------------------------

        self.scheduler.add_job(
            self.ke_warning,
            CronTrigger(
                day_of_week="fri",
                hour=purge_hour,
                minute=reset_minute
            ),
            id="ke_warning",
            replace_existing=True
        )

        # -------------------------------------------------
        # EVENT START
        # -------------------------------------------------

        self.scheduler.add_job(
            self.event_start,
            CronTrigger(
                day_of_week="fri",
                hour=reset_hour,
                minute=reset_minute
            ),
            id="event_start",
            replace_existing=True
        )

        # -------------------------------------------------
        # MONDAY ROTATION
        # -------------------------------------------------

        self.scheduler.add_job(
            self.check_rotation,
            CronTrigger(
                day_of_week="mon",
                hour=0,
                minute=1
            ),
            id="rotation_check",
            replace_existing=True
        )

    # =====================================================
    # CHANNEL LOOKUP
    # =====================================================

    async def _get_channels(self, guild_id: int):

        config = await db.get_server_config(guild_id)

        if not config:
            return None, None

        guild = self.bot.get_guild(guild_id)

        if not guild:
            return None, None

        bubble_channel = guild.get_channel(
            config.get("bubble_channel_id", 0)
        )

        battlefield_channel = guild.get_channel(
            config.get("battlefield_channel_id", 0)
        )

        return bubble_channel, battlefield_channel

    # =====================================================
    # SEND PERSONAL ALERTS
    # =====================================================

    async def _notify_members(
        self,
        guild: discord.Guild,
        title: str,
        message: str
    ):

        reminders = self.bot.get_cog("Reminders")

        if not reminders:
            return

        for member in guild.members:

            if member.bot:
                continue

            try:

                await reminders.notify_member(
                    member.id,
                    message,
                    title
                )

            except Exception as e:
                print(f"Member notify failed: {member.id} | {e}")

    # =====================================================
    # SVS FIRST WARNING
    # =====================================================

    async def svs_first_warning(self):

        for guild in self.bot.guilds:

            schedule = await db.get_event_schedule(guild.id)

            if not schedule:
                continue

            if schedule.get("current_event") != Config.SVS:
                continue

            bubble_channel, _ = await self._get_channels(guild.id)

            if bubble_channel:

                embed = discord.Embed(
                    title="⚠️ SVS PURGE WARNING",
                    description=(
                        "🚨 Purge begins in 39 minutes.\n\n"
                        "🛡️ Bubble now if you are not participating.\n\n"
                        "⚔️ Prepare for Server War."
                    ),
                    color=0xf39c12
                )

                await bubble_channel.send(
                    "@everyone",
                    embed=embed
                )

            await self._notify_members(
                guild,
                "SVS Warning",
                (
                    "🚨 Purge begins in 39 minutes.\n\n"
                    "🛡️ Bubble now if not participating."
                )
            )

    # =====================================================
    # SVS PURGE START
    # =====================================================

    async def svs_purge_warning(self):

        for guild in self.bot.guilds:

            schedule = await db.get_event_schedule(guild.id)

            if not schedule:
                continue

            if schedule.get("current_event") != Config.SVS:
                continue

            bubble_channel, _ = await self._get_channels(guild.id)

            if bubble_channel:

                embed = discord.Embed(
                    title="🚨 SVS PURGE STARTED",
                    description=(
                        "⚠️ Purge has officially started.\n\n"
                        "🛡️ Bubble immediately.\n\n"
                        "🔥 Attacks may now begin."
                    ),
                    color=0xe74c3c
                )

                await bubble_channel.send(
                    "@everyone",
                    embed=embed
                )

            await self._notify_members(
                guild,
                "SVS Purge Started",
                (
                    "🚨 Purge has started.\n\n"
                    "🛡️ Bubble immediately."
                )
            )

    # =====================================================
    # KE WARNING
    # =====================================================

    async def ke_warning(self):

        for guild in self.bot.guilds:

            schedule = await db.get_event_schedule(guild.id)

            if not schedule:
                continue

            if schedule.get("current_event") != Config.KE:
                continue

            bubble_channel, _ = await self._get_channels(guild.id)

            if bubble_channel:

                embed = discord.Embed(
                    title="⚔️ KE STARTS IN 1 HOUR",
                    description=(
                        "🛡️ Bubble now.\n\n"
                        "🌾 All tiles and relics are SAFE until reset."
                    ),
                    color=0xe67e22
                )

                await bubble_channel.send(
                    "@everyone",
                    embed=embed
                )

            await self._notify_members(
                guild,
                "KE Starts In 1 Hour",
                (
                    "🛡️ Bubble now.\n\n"
                    "🌾 Tiles and relics remain safe until reset."
                )
            )

    # =====================================================
    # EVENT START
    # =====================================================

    async def event_start(self):

        for guild in self.bot.guilds:

            schedule = await db.get_event_schedule(guild.id)

            if not schedule:
                continue

            current_event = schedule.get(
                "current_event",
                Config.SVS
            )

            _, battlefield_channel = await self._get_channels(guild.id)

            if current_event == Config.SVS:

                title = "🏰 SVS HAS STARTED"

                description = (
                    "🛡️ Bubble immediately.\n\n"
                    "🚫 Stay out of ALL tiles and relics.\n\n"
                    "⚔️ Enemy server attacks are now active."
                )

            else:

                title = "⚔️ KE HAS STARTED"

                description = (
                    "🛡️ Bubble immediately.\n\n"
                    "🌾 Tiles and relics are SAFE.\n\n"
                    "⚔️ Kill Event is now active."
                )

            if battlefield_channel:

                embed = discord.Embed(
                    title=title,
                    description=description,
                    color=0xc0392b
                )

                await battlefield_channel.send(
                    "@everyone",
                    embed=embed
                )

            await self._notify_members(
                guild,
                title,
                description
            )

    # =====================================================
    # MONDAY EVENT ROTATION
    # =====================================================

    async def check_rotation(self):

        for guild in self.bot.guilds:

            schedule = await db.get_event_schedule(guild.id)

            if not schedule:
                continue

            new_event = await db.rotate_event(guild.id)

            _, battlefield_channel = await self._get_channels(guild.id)

            if battlefield_channel:

                embed = discord.Embed(
                    title="🔄 Weekly Rotation",
                    description=(
                        f"Next Friday event:\n\n"
                        f"{new_event.upper()}"
                    ),
                    color=0x3498db
                )

                await battlefield_channel.send(embed=embed)

    # =====================================================
    # FORCE EVENT
    # =====================================================

    @app_commands.command(
        name="forceevent",
        description="Force current event"
    )
    @app_commands.checks.has_permissions(administrator=True)

    @app_commands.choices(event_type=[
        app_commands.Choice(name="SVS", value="svs"),
        app_commands.Choice(name="KE", value="ke")
    ])

    async def forceevent(
        self,
        interaction: discord.Interaction,
        event_type: app_commands.Choice[str]
    ):

        await db.set_event_schedule(
            guild_id=interaction.guild_id,
            current_event=event_type.value
        )

        await interaction.response.send_message(
            f"✅ Event set to {event_type.name}",
            ephemeral=True
        )

    # =====================================================
    # CURRENT EVENT
    # =====================================================

    @app_commands.command(
        name="currentevent",
        description="Show current event"
    )

    async def currentevent(
        self,
        interaction: discord.Interaction
    ):

        schedule = await db.get_event_schedule(
            interaction.guild_id
        )

        if not schedule:

            return await interaction.response.send_message(
                "❌ No event configured.",
                ephemeral=True
            )

        current = schedule.get("current_event", "unknown")
        next_date = schedule.get("next_event_date", "unknown")

        embed = discord.Embed(
            title="📅 Current Event",
            color=0x3498db
        )

        embed.add_field(
            name="Current",
            value=current.upper(),
            inline=False
        )

        embed.add_field(
            name="Next Event Date",
            value=str(next_date),
            inline=False
        )

        await interaction.response.send_message(
            embed=embed,
            ephemeral=True
        )


# =========================================================
# SETUP
# =========================================================

async def setup(bot: commands.Bot):
    await bot.add_co
