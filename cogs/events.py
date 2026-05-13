"""
SVS/KE Auto Rotation - Slash Commands
"""
import discord
from discord.ext import commands
from discord import app_commands
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from datetime import datetime, timedelta
import pytz
from database import db
from utils.time_utils import get_host_reset_time, get_user_local_reset_time, format_local_time, is_event_monday
from utils.embeds import Embeds
from config import Config

class Events(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.scheduler = AsyncIOScheduler()
        self.scheduler.start()
        self._schedule_jobs()
    
    def _schedule_jobs(self):
        # SVS: 1h39m before (3:21pm), purge 1h before (4pm), start 5pm
        self.scheduler.add_job(self.svs_first_reminder, CronTrigger(day_of_week="fri", hour=15, minute=21), id="svs_first", replace_existing=True)
        self.scheduler.add_job(self.svs_purge_reminder, CronTrigger(day_of_week="fri", hour=16, minute=0), id="svs_purge", replace_existing=True)
        self.scheduler.add_job(self.svs_second_reminder, CronTrigger(day_of_week="fri", hour=16, minute=0), id="svs_second", replace_existing=True)
        self.scheduler.add_job(self.event_start, CronTrigger(day_of_week="fri", hour=17, minute=0), id="svs_start", replace_existing=True)
        
        # KE: 1h before (4pm), start 5pm
        self.scheduler.add_job(self.ke_reminder, CronTrigger(day_of_week="fri", hour=16, minute=0), id="ke_reminder", replace_existing=True)
        self.scheduler.add_job(self.event_start, CronTrigger(day_of_week="fri", hour=17, minute=0), id="ke_start", replace_existing=True)
        
        # Monday rotation
        self.scheduler.add_job(self.check_rotation, CronTrigger(day_of_week="mon", hour=0, minute=1), id="rotation", replace_existing=True)
        
        # Init new servers
        self.scheduler.add_job(self.init_new_servers, CronTrigger(hour=0, minute=5), id="init_servers", replace_existing=True)
    
    async def init_new_servers(self):
        for guild in self.bot.guilds:
            schedule = await db.get_event_schedule(guild.id)
            if not schedule:
                await db.set_event_schedule(guild_id=guild.id, current_event=Config.SVS)
    
    async def _get_channels(self, guild_id: int):
        config = await db.get_server_config(guild_id)
        if not config:
            return None, None
        guild = self.bot.get_guild(guild_id)
        if not guild:
            return None, None
        bubble = guild.get_channel(config.get("bubble_channel_id", 0))
        battlefield = guild.get_channel(config.get("battlefield_channel_id", 0))
        return bubble, battlefield
    
    async def _send_bubble_alert(self, guild_id: int, event_type: str, is_purge: bool = False):
        """Send to bubble channel + PM all members with local times"""
        bubble_ch, _ = await self._get_channels(guild_id)
        if not bubble_ch:
            return
        
        guild = self.bot.get_guild(guild_id)
        if not guild:
            return
        
        # Server-wide bubble channel message
        embed = Embeds.shield_alert(event_type, is_purge)
        await bubble_ch.send("@everyone", embed=embed)
        
        # PM each member with their local time
        for member in guild.members:
            if member.bot:
                continue
            
            contact = await db.get_member_contact(member.id)
            user_tz = contact.get("timezone", "UTC") if contact else "UTC"
            local_reset = get_user_local_reset_time(user_tz)
            local_str = format_local_time(local_reset)
            
            if is_purge:
                instruction = "🚨 **PURGE ATTACK IN 1 HOUR!** Put up your bubble NOW or join the fight!"
            else:
                instruction = f"🛡️ Put up your **bubble** if not participating in {event_type.upper()}!"
            
            pm_embed = Embeds.personal_reminder(event_type, local_str, instruction)
            
            try:
                await member.send(embed=pm_embed)
                if not await db.has_bubble_reminder_today(guild_id, member.id, event_type):
                    await db.track_bubble_reminder(guild_id, member.id, event_type)
            except discord.Forbidden:
                pass
            except Exception as e:
                print(f"DM error {member.id}: {e}")
    
    async def svs_first_reminder(self):
        for guild in self.bot.guilds:
            schedule = await db.get_event_schedule(guild.id)
            if schedule and schedule.get("current_event") == Config.SVS:
                if not await db.was_reminder_sent_today(guild.id, Config.SVS, "first"):
                    await self._send_bubble_alert(guild.id, Config.SVS)
                    await db.log_reminder(guild.id, Config.SVS, "first")
    
    async def svs_purge_reminder(self):
        for guild in self.bot.guilds:
            schedule = await db.get_event_schedule(guild.id)
            if schedule and schedule.get("current_event") == Config.SVS:
                if not await db.was_reminder_sent_today(guild.id, Config.SVS, "purge"):
                    await self._send_bubble_alert(guild.id, Config.SVS, is_purge=True)
                    await db.log_reminder(guild.id, Config.SVS, "purge")
    
    async def svs_second_reminder(self):
        for guild in self.bot.guilds:
            schedule = await db.get_event_schedule(guild.id)
            if schedule and schedule.get("current_event") == Config.SVS:
                if not await db.was_reminder_sent_today(guild.id, Config.SVS, "second"):
                    await self._send_bubble_alert(guild.id, Config.SVS)
                    await db.log_reminder(guild.id, Config.SVS, "second")
    
    async def ke_reminder(self):
        for guild in self.bot.guilds:
            schedule = await db.get_event_schedule(guild.id)
            if schedule and schedule.get("current_event") == Config.KE:
                if not await db.was_reminder_sent_today(guild.id, Config.KE, "reminder"):
                    await self._send_bubble_alert(guild.id, Config.KE)
                    await db.log_reminder(guild.id, Config.KE, "reminder")
    
    async def event_start(self):
        for guild in self.bot.guilds:
            schedule = await db.get_event_schedule(guild.id)
            if not schedule:
                continue
            current = schedule.get("current_event", Config.SVS)
            _, battlefield_ch = await self._get_channels(guild.id)
            if battlefield_ch:
                embed = Embeds.event_start_notice(current)
                await battlefield_ch.send("@everyone", embed=embed)
    
    async def check_rotation(self):
        for guild in self.bot.guilds:
            schedule = await db.get_event_schedule(guild.id)
            if not schedule:
                continue
            new_event = await db.rotate_event(guild.id)
            _, battlefield_ch = await self._get_channels(guild.id)
            if battlefield_ch:
                embed = discord.Embed(
                    title="🔄 Event Rotation",
                    description=f"Previous event ended. Next week: **{new_event.upper()}**",
                    color=0x3498db
                )
                await battlefield_ch.send(embed=embed)
    
    # ========== SLASH COMMANDS ==========
    
    @app_commands.command(name="forceevent", description="Force set current event type")
    @app_commands.checks.has_permissions(administrator=True)
    @app_commands.describe(event_type="svs or ke")
    @app_commands.choices(event_type=[
        app_commands.Choice(name="SVS", value="svs"),
        app_commands.Choice(name="KE", value="ke")
    ])
    async def slash_forceevent(self, interaction: discord.Interaction, event_type: app_commands.Choice[str]):
        await db.set_event_schedule(guild_id=interaction.guild_id, current_event=event_type.value)
        await interaction.response.send_message(f"✅ Current event forced to **{event_type.name}**", ephemeral=True)
    
    @app_commands.command(name="currentevent", description="Check this week's scheduled event")
    async def slash_currentevent(self, interaction: discord.Interaction):
        schedule = await db.get_event_schedule(interaction.guild_id)
        if not schedule:
            return await interaction.response.send_message("No schedule found.", ephemeral=True)
        current = schedule.get("current_event", "Unknown")
        next_date = schedule.get("next_event_date", "Unknown")
        await interaction.response.send_message(f"Current: **{current.upper()}** | Next: {next_date}", ephemeral=True)

async def setup(bot: commands.Bot):
    await bot.add_cog(Events(bot))
