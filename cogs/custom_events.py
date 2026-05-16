"""
Custom Events (BOC / BOG / AllStars / Battlefield)
FIXED: Stable DB-driven + safe reaction handling + no scheduler spam
"""

import discord
from discord.ext import commands
from discord import app_commands

from datetime import datetime
import pytz

from database import db
from utils.embeds import Embeds
from config import Config


class CustomEvents(commands.Cog):

    def __init__(self, bot: commands.Bot):
        self.bot = bot

    # =====================================================
    # COORDINATOR CHECK
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
    # CREATE EVENT (MODAL)
    # =====================================================

    @app_commands.command(
        name="event_create",
        description="Create a custom PvP event"
    )
    async def event_create(self, interaction: discord.Interaction):

        if not await self._is_coordinator(interaction):
            return await interaction.response.send_message(
                "❌ You need Event Coordinator role.",
                ephemeral=True
            )

        await interaction.response.send_modal(EventCreateModal())

    # =====================================================
    # CANCEL EVENT
    # =====================================================

    @app_commands.command(name="event_cancel")
    async def event_cancel(self, interaction: discord.Interaction, event_id: int):

        if not await self._is_coordinator(interaction):
            return await interaction.response.send_message("❌ No permission.", ephemeral=True)

        event = await db.get_custom_event(event_id)

        if not event or event["guild_id"] != interaction.guild_id:
            return await interaction.response.send_message("❌ Not found.", ephemeral=True)

        # delete message safely
        try:
            channel = interaction.guild.get_channel(event["channel_id"])
            if channel and event.get("message_id"):
                msg = await channel.fetch_message(event["message_id"])
                await msg.delete()
        except:
            pass

        await db.delete_custom_event(event_id)

        await interaction.response.send_message("✅ Event cancelled.", ephemeral=True)

    # =====================================================
    # LIST EVENTS
    # =====================================================

    @app_commands.command(name="event_list")
    async def event_list(self, interaction: discord.Interaction):

        events = await db.get_active_custom_events(interaction.guild_id)

        if not events:
            return await interaction.response.send_message("📭 No active events.", ephemeral=True)

        embed = discord.Embed(title="📅 Active Events", color=0x3498db)

        for e in events:

            start = e["start_time"]
            if isinstance(start, str):
                start = datetime.fromisoformat(start)

            embed.add_field(
                name=f"{e['name']} (ID {e['event_id']})",
                value=(
                    f"Type: {e['event_type'].upper()}\n"
                    f"Start: {start.strftime('%a %H:%M')}\n"
                    f"Coord: <@{e['coordinator_id']}>"
                ),
                inline=False
            )

        await interaction.response.send_message(embed=embed, ephemeral=True)

    # =====================================================
    # ROSTER
    # =====================================================

    @app_commands.command(name="event_roster")
    async def event_roster(self, interaction: discord.Interaction, event_id: int):

        event = await db.get_custom_event(event_id)

        if not event or event["guild_id"] != interaction.guild_id:
            return await interaction.response.send_message("❌ Not found.", ephemeral=True)

        checkins = await db.get_event_checkins(event_id)

        yes, no = [], []

        for c in checkins:

            member = interaction.guild.get_member(c["user_id"])
            name = member.mention if member else str(c["user_id"])

            if c["status"] == "yes":
                yes.append(name)
            else:
                no.append(name)

        embed = Embeds.event_roster(event["name"], yes, no)

        await interaction.response.send_message(embed=embed, ephemeral=True)

    # =====================================================
    # REACTION HANDLER (FIXED)
    # =====================================================

    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload: discord.RawReactionActionEvent):

        if payload.user_id == self.bot.user.id:
            return

        events = await db.get_active_custom_events(payload.guild_id)

        for event in events:

            if event.get("message_id") != payload.message_id:
                continue

            # cutoff check
            cutoff = event["checkin_cutoff"]
            if isinstance(cutoff, str):
                cutoff = datetime.fromisoformat(cutoff)

            if datetime.utcnow() > cutoff:
                channel = self.bot.get_channel(payload.channel_id)
                if channel:
                    await channel.send(f"<@{payload.user_id}> check-in closed.", delete_after=10)
                return

            emoji = str(payload.emoji)

            if emoji not in ("✅", "❌"):
                return

            status = "yes" if emoji == "✅" else "no"

            await db.checkin_member(event["event_id"], payload.user_id, status)

            # DM user (safe)
            user = self.bot.get_user(payload.user_id)
            if user:
                try:
                    await user.send(f"✅ You are **{status.upper()}** for **{event['name']}**")
                except:
                    pass

            break


# =====================================================
# MODAL
# =====================================================

class EventCreateModal(discord.ui.Modal, title="Create Event"):

    event_name = discord.ui.TextInput(label="Event Name")
    event_type = discord.ui.TextInput(label="Type (boc/bog/allstars/battlefield)")
    start_time = discord.ui.TextInput(label="Start (YYYY-MM-DD HH:MM)")
    duration = discord.ui.TextInput(label="Duration hours")
    cutoff = discord.ui.TextInput(label="Check-in cutoff mins")

    async def on_submit(self, interaction: discord.Interaction):

        event_type = self.event_type.value.lower()

        if event_type not in Config.CUSTOM_EVENT_TYPES:
            return await interaction.response.send_message("❌ Invalid type.", ephemeral=True)

        try:
            start = datetime.strptime(self.start_time.value, "%Y-%m-%d %H:%M")
            start = pytz.timezone(Config.HOST_TIMEZONE).localize(start)
        except:
            return await interaction.response.send_message("❌ Invalid time format.", ephemeral=True)

        try:
            duration = float(self.duration.value)
            cutoff_mins = int(self.cutoff.value)
        except:
            return await interaction.response.send_message("❌ Invalid numbers.", ephemeral=True)

        end = start + timedelta(hours=duration)
        checkin_cutoff = start - timedelta(minutes=cutoff_mins)

        config = await db.get_server_config(interaction.guild_id)
        channel = interaction.guild.get_channel(config.get("battlefield_channel_id", 0)) if config else None

        if not channel:
            return await interaction.response.send_message("❌ No battlefield channel.", ephemeral=True)

        event_id = await db.create_custom_event(
            guild_id=interaction.guild_id,
            event_type=event_type,
            name=self.event_name.value,
            start_time=start,
            end_time=end,
            coordinator_id=interaction.user.id,
            checkin_cutoff=checkin_cutoff,
            channel_id=channel.id
        )

        embed = Embeds.custom_event_checkin(
            self.event_name.value,
            event_type,
            start.strftime("%A %H:%M"),
            interaction.user.mention,
            checkin_cutoff.strftime("%H:%M")
        )

        msg = await channel.send(
            f"@everyone **{self.event_name.value}** check-in open!",
            embed=embed
        )

        await msg.add_reaction("✅")
        await msg.add_reaction("❌")

        await db.update_custom_event(event_id, message_id=msg.id)

        await interaction.response.send_message(
            f"✅ Event created (ID: {event_id})",
            ephemeral=True
        )


# =====================================================
# SETUP
# =====================================================

async def setup(bot: commands.Bot):
    await bot.add_cog(CustomEvents(bot))
