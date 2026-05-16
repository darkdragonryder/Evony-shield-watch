"""
Evony Shield Watch
Reminders System (FULLY ALIGNED WITH WEEK TOGGLE SYSTEM)
"""

import discord
from discord.ext import commands
import aiohttp
from datetime import datetime

from database import db
from config import Config
from utils.time_utils import get_user_local_reset_time, format_local_time
from utils.embeds import Embeds


class Reminders(commands.Cog):

    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.session = aiohttp.ClientSession()

    # =====================================================
    # CLEANUP
    # =====================================================

    def cog_unload(self):
        self.bot.loop.create_task(self.session.close())

    # =====================================================
    # GET CURRENT EVENT (SOURCE OF TRUTH)
    # =====================================================

    async def get_event(self, guild_id: int) -> str:
        config = await db.get_server_config(guild_id)
        if not config:
            return Config.SVS

        toggle = config.get("event_week_toggle", 0)
        return Config.SVS if toggle == 1 else Config.KE

    # =====================================================
    # DISCORD DM SENDER
    # =====================================================

    async def _send_discord(self, user: discord.User, embed: discord.Embed):
        try:
            await user.send(embed=embed)
            return True
        except:
            return False

    # =====================================================
    # TELEGRAM SENDER
    # =====================================================

    async def _send_telegram(self, telegram_id: str, message: str, title: str):

        if not Config.TELEGRAM_BOT_TOKEN:
            return False

        try:
            url = f"https://api.telegram.org/bot{Config.TELEGRAM_BOT_TOKEN}/sendMessage"

            payload = {
                "chat_id": telegram_id,
                "text": f"🛡️ {title}\n\n{message}",
                "parse_mode": "HTML"
            }

            async with self.session.post(url, data=payload) as resp:
                return resp.status == 200

        except Exception:
            return False

    # =====================================================
    # MAIN NOTIFICATION ENGINE
    # =====================================================

    async def notify_member(self, user_id: int, message: str, title: str = "Evony Alert"):

        contact = await db.get_member_contact(user_id)
        if not contact:
            return

        results = {
            "discord": False,
            "telegram": False
        }

        user = self.bot.get_user(user_id)

        # -------------------------------------------------
        # DISCORD
        # -------------------------------------------------
        if user and contact.get("opt_in", 1):

            embed = discord.Embed(
                title=title,
                description=message,
                color=0xFF0000,
                timestamp=datetime.utcnow()
            )

            results["discord"] = await self._send_discord(user, embed)

        # -------------------------------------------------
        # TELEGRAM
        # -------------------------------------------------
        if contact.get("telegram_id"):

            results["telegram"] = await self._send_telegram(
                contact["telegram_id"],
                message,
                title
            )

        return results

    # =====================================================
    # SVS 39 MIN WARNING (PURGE PHASE)
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

            embed = Embeds.shield_alert(Config.SVS, is_purge=True)
            await channel.send("@everyone", embed=embed)

            # optional mass DM (safe loop)
            for member in guild.members:
                if member.bot:
                    continue

                contact = await db.get_member_contact(member.id)
                if not contact:
                    continue

                if contact.get("opt_in", 1):
                    local = get_user_local_reset_time(contact.get("timezone", "UTC"))
                    msg = f"Purge incoming. Local time: {format_local_time(local)}"

                    await self.notify_member(
                        member.id,
                        msg,
                        "SVS PURGE WARNING"
                    )

    # =====================================================
    # 1 HOUR WARNING (ALL EVENTS)
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

            embed = Embeds.shield_alert(event, is_purge=False)
            await channel.send("@everyone", embed=embed)

    # =====================================================
    # RESET START MESSAGE
    # =====================================================

    async def reset_start(self):

        for guild in self.bot.guilds:

            event = await self.get_event(guild.id)

            config = await db.get_server_config(guild.id)
            if not config:
                continue

            battlefield = guild.get_channel(config.get("battlefield_channel_id", 0))
            if battlefield:
                embed = Embeds.event_start_notice(event)
                await battlefield.send("@everyone", embed=embed)

    # =====================================================
    # SETUP
    # =====================================================

async def setup(bot: commands.Bot):
    await bot.add_cog(Reminders(bot))
