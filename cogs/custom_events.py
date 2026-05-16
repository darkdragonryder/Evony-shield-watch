"""
Custom Events (BOC/BOG/AllStars/Battlefield)
FULLY FIXED - CLEAN DB + NO BROKEN SCHEDULERS
"""

import discord
from discord.ext import commands
from discord import app_commands
from datetime import datetime, timedelta
import pytz

from database import db
from utils.embeds import Embeds
from config import Config


class CustomEvents(commands.Cog):

    def __init__(self, bot: commands.Bot):
        self.bot = bot

    # =====================================================
    # PERMISSION CHECK
    # =====================================================

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

    # =====================================================
    # CREATE EVENT (NO LOCAL SCHEDULER ANYMORE)
    # =====================================================

    @app_commands.command(
        name="event_create",
        description="Create a custom event (BOC/BOG/AllStars/Battlefield)"
    )
    async def slash_event_create(self, interaction: discord.Interaction):

        if not await self._is_coordinator(interaction):
            return await interaction.response.send_message(
                "❌ You need the Event Coordinator role!",
                ephemeral=True
            )

        await interaction.response.send_modal(EventCreateModal())

    # =====================================================
    # CANCEL EVENT
    # =====================================================

    @app_commands.command(
        name="event_cancel",
        description="Cancel a custom event"
    )
    async def slash_event_cancel(self, interaction: discord.Interaction, event_id: int):

        if not await self._is_coordinator(interaction):
            return await interaction.response.send_message(
                "❌ You need the Event Coordinator role!",
                ephemeral=True
            )

        event = await db.get_custom_event(event_id)

        if not event or event["guild_id"] != interaction.guild_id:
            return await interaction.response.send_message(
                "❌ Event not found.",
                ephemeral=True
            )

        try:
            channel = interaction.guild.get_channel(event["channel_id"])
            if channel:
                msg = await channel.fetch_message(event["message_id"])
                await msg.delete()
        except:
            pass

        await db.delete_custom_event(event_id)

        await interaction.response.send_message(
            f"✅ Event **{event['name']}** cancelled.",
            ephemeral=True
        )

    # =====================================================
    # EVENT LIST
    # =====================================================

    @app_commands.command(
        name="event_list",
        description="List all active custom events"
    )
    async def slash_event_list(self, interaction: discord.Interaction):

        events = await db.get_active_custom_events(interaction.guild_id)

        if not events:
            return await interaction.response.send_message(
                "📭 No active events.",
                ephemeral=True
            )

        embed = discord.Embed(title="📅 Active Events", color=0x3498db)

        for event in events:

            start = event["start_time"]

            if isinstance(start, str):
                start = datetime.fromisoformat(start)

            embed.add_field(
                name=f"{event['name']} (ID: {event['event_id']})",
                value=(
                    f"Type: {event['event_type'].upper()}\n"
                    f"Start: {start.strftime('%a %I:%M %p')}\n"
                    f"Coord: <@{event['coordinator_id']}>"
                ),
                inline=False
            )

        await interaction.response.send_message(embed=embed, ephemeral=True)

    # =====================================================
    # EVENT ROSTER
    # =====================================================

    @app_commands.command(
        name="event_roster",
        description="Show final roster for an event"
    )
    async def slash_event_roster(self, interaction: discord.Interaction, event_id: int):

        event = await db.get_custom_event(event_id)

        if not event or event["guild_id"] != interaction.guild_id:
            return await interaction.response.send_message(
                "❌ Event not found.",
                ephemeral=True
            )

        checkins = await db.get_event_checkins(event_id)

        yes_list = []
        no_list = []

        for c in checkins:

            user = interaction.guild.get_member(c["user_id"])
            name = user.mention if user else f"User {c['user_id']}"

            if c["status"] == "yes":
                yes_list.append(name)
            else:
                no_list.append(name)

        embed = Embeds.event_roster(
            event["name"],
            yes_list,
            no_list
        )

        await interaction.response.send_message(embed=embed, ephemeral=True)

    # =====================================================
    # REACTION CHECK-IN (FIXED SAFE VERSION)
    # =====================================================

    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload: discord.RawReactionActionEvent):

        if payload.user_id == self.bot.user.id:
            return

        events = await db.get_active_custom_events(payload.guild_id)

        for event in events:

            if event.get("message_id") != payload.message_id:
                continue

            cutoff = event["checkin_cutoff"]

            if isinstance(cutoff, str):
                cutoff = datetime.fromisoformat(cutoff)

            if datetime.utcnow() > cutoff:

                channel = self.bot.get_channel(payload.channel_id)

                if channel:
                    await channel.send(
                        f"<@{payload.user_id}> Check-in is closed!",
                        delete_after=10
                    )

                return

            emoji = str(payload.emoji)

            status = None
            if emoji == "✅":
                status = "yes"
            elif emoji == "❌":
                status = "no"

            if not status:
                return

            await db.checkin_member(
                event["event_id"],
                payload.user_id,
                status
            )

            user = self.bot.get_user(payload.user_id)

            if user:
                try:
                    await user.send(
                        f"✅ You're **{status.upper()}** for **{event['name']}**!"
                    )
                except:
                    pass

            break


# =====================================================
# MODAL
# =====================================================

class EventCreateModal(discord.ui.Modal, title="Create Event"):

    event_name = discord.ui.TextInput(label="Event Name", max_length=50)
    event_type = discord.ui.TextInput(label="Type (boc/bog/allstars/battlefield)", max_length=15)
    start_time = discord.ui.TextInput(label="Start Time (YYYY-MM-DD HH:MM)", max_length=16)
    duration = discord.ui.TextInput(label="Duration (hours)", max_length=3)
    cutoff = discord.ui.TextInput(label="Check-in Cutoff (mins before start)", max_length=3)

    async def on_submit(self, interaction: discord.Interaction):

        event_type = self.event_type.value.lower()

        if event_type not in Config.CUSTOM_EVENT_TYPES:
            return await interaction.response.send_message(
                "❌ Invalid type.",
                ephemeral=True
            )

        try:
            tz = pytz.timezone(Config.HOST_TIMEZONE)

            start = datetime.strptime(
                self.start_time.value,
                "%Y-%m-%d %H:%M"
            )

            start = tz.localize(start)

        except:
            return await interaction.response.send_message(
                "❌ Invalid time format.",
                ephemeral=True
            )

        try:
            duration = float(self.duration.value)
            cutoff_mins = int(self.cutoff.value)

            end = start + timedelta(hours=duration)
            checkin_cutoff = start - timedelta(minutes=cutoff_mins)

        except:
            return await interaction.response.send_message(
                "❌ Invalid duration/cutoff.",
                ephemeral=True
            )

        config = await db.get_server_config(interaction.guild_id)

        battlefield = interaction.guild.get_channel(
            config.get("battlefield_channel_id", 0)
        ) if config else None

        if not battlefield:
            return await interaction.response.send_message(
                "❌ Battlefield channel not set.",
                ephemeral=True
            )

        event_id = await db.create_custom_event(
            guild_id=interaction.guild_id,
            event_type=event_type,
            name=self.event_name.value,
            start_time=start,
            end_time=end,
            coordinator_id=interaction.user.id,
            checkin_cutoff=checkin_cutoff,
            channel_id=battlefield.id
        )

        embed = Embeds.custom_event_checkin(
            self.event_name.value,
            event_type,
            start.strftime("%A %B %d %I:%M %p"),
            interaction.user.mention,
            checkin_cutoff.strftime("%I:%M %p")
        )

        msg = await battlefield.send(
            f"@everyone **{self.event_name.value}**",
            embed=embed
        )

        await msg.add_reaction("✅")
        await msg.add_reaction("❌")

        await db.update_custom_event(
            event_id,
            message_id=msg.id
        )

        await interaction.response.send_message(
            f"✅ Event created (ID: {event_id})",
            ephemeral=True
        )


# =====================================================
# SETUP
# =====================================================

async def setup(bot: commands.Bot):
    await bot.add_cog(CustomEvents(bot))
