"""
Custom Events (BOC/BOG/AllStars/Battlefield) - Slash Commands
"""
import discord
from discord.ext import commands
from discord import app_commands
from datetime import datetime, timedelta
import pytz
import asyncio
from database import db
from utils.embeds import Embeds
from config import Config

class CustomEvents(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
    
    async def _is_coordinator(self, interaction: discord.Interaction) -> bool:
        if interaction.user.guild_permissions.administrator:
            return True
        config = await db.get_server_config(interaction.guild_id)
        if not config:
            return False
        role_id = config.get("event_coordinator_role_id")
        if not role_id:
            return False
        role = interaction.guild.get_role(role_id)
        if not role:
            return False
        return role in interaction.user.roles
    
    # ========== SLASH COMMANDS ==========
    
    @app_commands.command(name="event_create", description="Create a custom event (BOC/BOG/AllStars/Battlefield)")
    async def slash_event_create(self, interaction: discord.Interaction):
        if not await self._is_coordinator(interaction):
            return await interaction.response.send_message("❌ You need the Event Coordinator role!", ephemeral=True)
        
        # Modal for event creation
        await interaction.response.send_modal(EventCreateModal())
    
    @app_commands.command(name="event_cancel", description="Cancel a custom event")
    @app_commands.describe(event_id="The event ID to cancel")
    async def slash_event_cancel(self, interaction: discord.Interaction, event_id: int):
        if not await self._is_coordinator(interaction):
            return await interaction.response.send_message("❌ You need the Event Coordinator role!", ephemeral=True)
        
        event = await db.get_custom_event(event_id)
        if not event or event["guild_id"] != interaction.guild_id:
            return await interaction.response.send_message("❌ Event not found.", ephemeral=True)
        
        # Delete message
        try:
            channel = interaction.guild.get_channel(event["channel_id"])
            if channel:
                msg = await channel.fetch_message(event["message_id"])
                await msg.delete()
        except:
            pass
        
        await db.delete_custom_event(event_id)
        await interaction.response.send_message(f"✅ Event **{event['name']}** cancelled.", ephemeral=True)
    
    @app_commands.command(name="event_list", description="List all active custom events")
    async def slash_event_list(self, interaction: discord.Interaction):
        events = await db.get_active_custom_events(interaction.guild_id)
        if not events:
            return await interaction.response.send_message("📭 No active events.", ephemeral=True)
        
        embed = discord.Embed(title="📅 Active Events", color=0x3498db)
        for event in events:
            start = event["start_time"]
            if isinstance(start, str):
                start = datetime.fromisoformat(start)
            embed.add_field(
                name=f"{event['name']} (ID: {event['event_id']})",
                value=f"Type: {event['event_type'].upper()}\nStart: {start.strftime('%a %I:%M %p')}\nCoord: <@{event['coordinator_id']}>",
                inline=False
            )
        await interaction.response.send_message(embed=embed, ephemeral=True)
    
    @app_commands.command(name="event_roster", description="Show final roster for an event")
    @app_commands.describe(event_id="The event ID")
    async def slash_event_roster(self, interaction: discord.Interaction, event_id: int):
        event = await db.get_custom_event(event_id)
        if not event or event["guild_id"] != interaction.guild_id:
            return await interaction.response.send_message("❌ Event not found.", ephemeral=True)
        
        checkins = await db.get_event_checkins(event_id)
        yes_list = []
        no_list = []
        
        for checkin in checkins:
            user = interaction.guild.get_member(checkin["user_id"])
            name = user.mention if user else f"User {checkin['user_id']}"
            if checkin["status"] == "yes":
                yes_list.append(name)
            else:
                no_list.append(name)
        
        embed = Embeds.event_roster(event["name"], yes_list, no_list)
        await interaction.response.send_message(embed=embed, ephemeral=True)
    
    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload: discord.RawReactionActionEvent):
        if payload.user_id == self.bot.user.id:
            return
        
        events = await db.get_active_custom_events(payload.guild_id)
        for event in events:
            if event.get("message_id") == payload.message_id:
                cutoff = event["checkin_cutoff"]
                if isinstance(cutoff, str):
                    cutoff = datetime.fromisoformat(cutoff)
                
                if datetime.now(pytz.utc) > cutoff.replace(tzinfo=pytz.utc):
                    channel = self.bot.get_channel(payload.channel_id)
                    if channel:
                        await channel.send(f"<@{payload.user_id}> Check-in is closed!", delete_after=10)
                    return
                
                status = "yes" if str(payload.emoji) == "✅" else "no" if str(payload.emoji) == "❌" else None
                if status:
                    await db.checkin_member(event["event_id"], payload.user_id, status)
                    user = self.bot.get_user(payload.user_id)
                    if user:
                        try:
                            await user.send(f"✅ You're **{status.upper()}** for **{event['name']}**!")
                        except:
                            pass
                break

class EventCreateModal(discord.ui.Modal, title="Create Event"):
    event_name = discord.ui.TextInput(label="Event Name", placeholder="Week 3 BOC", max_length=50)
    event_type = discord.ui.TextInput(label="Type (boc/bog/allstars/battlefield)", placeholder="boc", max_length=15)
    start_time = discord.ui.TextInput(label="Start Time (YYYY-MM-DD HH:MM)", placeholder="2026-05-16 18:00", max_length=16)
    duration = discord.ui.TextInput(label="Duration (hours)", placeholder="2", max_length=3)
    cutoff = discord.ui.TextInput(label="Check-in Cutoff (mins before start)", placeholder="30", max_length=3)
    
    async def on_submit(self, interaction: discord.Interaction):
        event_type = self.event_type.value.lower()
        if event_type not in Config.CUSTOM_EVENT_TYPES:
            return await interaction.response.send_message("❌ Invalid type. Use: boc, bog, allstars, battlefield", ephemeral=True)
        
        try:
            user_tz = pytz.timezone(Config.HOST_TIMEZONE)
            start = datetime.strptime(self.start_time.value, "%Y-%m-%d %H:%M")
            start = user_tz.localize(start)
        except ValueError:
            return await interaction.response.send_message("❌ Invalid time format. Use YYYY-MM-DD HH:MM", ephemeral=True)
        
        try:
            duration = float(self.duration.value)
            end = start + timedelta(hours=duration)
            cutoff_mins = int(self.cutoff.value)
            checkin_cutoff = start - timedelta(minutes=cutoff_mins)
        except ValueError:
            return await interaction.response.send_message("❌ Invalid duration or cutoff.", ephemeral=True)
        
        config = await db.get_server_config(interaction.guild_id)
        battlefield_ch = interaction.guild.get_channel(config.get("battlefield_channel_id", 0)) if config else None
        
        if not battlefield_ch:
            return await interaction.response.send_message("❌ No battlefield channel configured! Use `/setbattlefield`", ephemeral=True)
        
        event_id = await db.create_custom_event(
            guild_id=interaction.guild_id,
            event_type=event_type,
            name=self.event_name.value,
            start_time=start,
            end_time=end,
            coordinator_id=interaction.user.id,
            checkin_cutoff=checkin_cutoff,
            channel_id=battlefield_ch.id
        )
        
        start_str = start.strftime("%A, %B %d at %I:%M %p %Z")
        cutoff_str = checkin_cutoff.strftime("%I:%M %p %Z")
        
        embed = Embeds.custom_event_checkin(
            self.event_name.value, event_type, start_str, interaction.user.mention, cutoff_str
        )
        
        checkin_msg = await battlefield_ch.send(
            f"@everyone **{self.event_name.value}** - Check in now!", embed=embed
        )
        await checkin_msg.add_reaction("✅")
        await checkin_msg.add_reaction("❌")
        
        await db.update_custom_event(event_id, message_id=checkin_msg.id)
        
        # Schedule cleanup
        from apscheduler.schedulers.asyncio import AsyncIOScheduler
        from apscheduler.triggers.date import DateTrigger
        cleanup_time = end + Config.EVENT_CLEANUP_DELAY
        scheduler = AsyncIOScheduler()
        scheduler.add_job(
            self._cleanup_event, DateTrigger(run_date=cleanup_time),
            args=[event_id], id=f"cleanup_{event_id}"
        )
        scheduler.start()
        
        await interaction.response.send_message(
            f"✅ **{self.event_name.value}** created!\nID: `{event_id}` | Check-in closes at {cutoff_str}",
            ephemeral=True
        )
    
    async def _cleanup_event(self, event_id: int):
        event = await db.get_custom_event(event_id)
        if not event:
            return
        try:
            guild = self.bot.get_guild(event["guild_id"])
            if guild:
                channel = guild.get_channel(event["channel_id"])
                if channel:
                    msg = await channel.fetch_message(event["message_id"])
                    await msg.delete()
        except:
            pass
        await db.update_custom_event(event_id, status="completed")

async def setup(bot: commands.Bot):
    await bot.add_cog(CustomEvents(bot))
