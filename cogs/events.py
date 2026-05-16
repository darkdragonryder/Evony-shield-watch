"""
=========================================================
Evony Shield Watch
Event Engine (CLEAN STATE VERSION)
NO SCHEDULER LOGIC — ONLY STATE BROADCASTS
=========================================================
"""

import discord
from discord.ext import commands

from database import db
from services.event_engine import EventEngine
from utils.embeds import Embeds


class Events(commands.Cog):

    def __init__(self, bot: commands.Bot):
        self.bot = bot

    # =====================================================
    # BROADCAST CURRENT EVENT STATE
    # =====================================================

    async def broadcast_event_start(self):

        for guild in self.bot.guilds:

            config = await db.get_server_config(guild.id)
            if not config:
                continue

            channel = guild.get_channel(config.get("battlefield_channel_id", 0))
            if not channel:
                continue

            event = EventEngine.get_current_event()

            embed = Embeds.event_start_notice(event)

            await channel.send("@everyone", embed=embed)
