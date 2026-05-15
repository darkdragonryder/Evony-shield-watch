"""
=========================================================
 Evony Shield Watch
 Reminders System (Discord + Telegram + SMS optional removed)
=========================================================
"""

# =========================================================
# IMPORTS
# =========================================================

import discord
from discord.ext import commands
from discord import app_commands

import aiohttp
import asyncio
from datetime import datetime

import pytz

from config import Config
from database import db
from utils.time_utils import get_user_local_reset_time, format_local_time


# =========================================================
# REMINDERS COG
# =========================================================

class Reminders(commands.Cog):

    def __init__(self, bot: commands.Bot):

        self.bot = bot
        self.session = aiohttp.ClientSession()

    # =====================================================
    # CLEANUP SESSION
    # =====================================================

    def cog_unload(self):
        self.bot.loop.create_task(self.session.close())

    # =====================================================
    # TELEGRAM SENDER
    # =====================================================

    async def _send_telegram(self, telegram_id: str, message: str, title: str):

        if not Config.has_telegram():
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

        except Exception as e:
            print(f"Telegram error: {e}")
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
        # DISCORD DM
        # -------------------------------------------------

        if user and contact.get("discord_opt_in", 1):

            try:

                embed = discord.Embed(
                    title=title,
                    description=message,
                    color=0xFF0000,
                    timestamp=datetime.utcnow()
                )

                await user.send(embed=embed)
                results["discord"] = True

            except:
                pass

        # -------------------------------------------------
        # TELEGRAM DM
        # -------------------------------------------------

        if contact.get("telegram_id"):

            results["telegram"] = await self._send_telegram(
                contact["telegram_id"],
                message,
                title
            )

        return results

    # =====================================================
    # SLASH COMMANDS
    # =====================================================

    @app_commands.command(
        name="mytime",
        description="Check your local reset time"
    )
    async def mytime(self, interaction: discord.Interaction):

        contact = await db.get_member_contact(interaction.user.id)

        tz = contact.get("timezone", "UTC") if contact else "UTC"

        local = get_user_local_reset_time(tz)

        formatted = format_local_time(local)

        embed = discord.Embed(
            title="⏰ Your Local Reset Time",
            description=f"Server reset converts to:\n\n**{formatted}**",
            color=0x3498db
        )

        embed.add_field(name="Timezone", value=tz, inline=False)

        await interaction.response.send_message(embed=embed, ephemeral=True)

    # =====================================================
    # SET TIMEZONE
    # =====================================================

    @app_commands.command(
        name="settimezone",
        description="Set your timezone"
    )
    async def settimezone(
        self,
        interaction: discord.Interaction,
        timezone: str
    ):

        try:

            pytz.timezone(timezone)

            await db.set_member_contact(
                interaction.user.id,
                timezone=timezone
            )

            await interaction.response.send_message(
                f"✅ Timezone set to **{timezone}**",
                ephemeral=True
            )

        except pytz.UnknownTimeZoneError:

            await interaction.response.send_message(
                "❌ Invalid timezone (e.g. Europe/London, Asia/Tokyo)",
                ephemeral=True
            )

    # =====================================================
    # OPT OUT
    # =====================================================

    @app_commands.command(
        name="optout",
        description="Disable Discord notifications"
    )
    async def optout(self, interaction: discord.Interaction):

        await db.set_member_contact(
            interaction.user.id,
            discord_opt_in=0
        )

        await interaction.response.send_message(
            "🔕 Discord notifications disabled.",
            ephemeral=True
        )

    # =====================================================
    # OPT IN
    # =====================================================

    @app_commands.command(
        name="optin",
        description="Enable Discord notifications"
    )
    async def optin(self, interaction: discord.Interaction):

        await db.set_member_contact(
            interaction.user.id,
            discord_opt_in=1
        )

        await interaction.response.send_message(
            "🔔 Notifications re-enabled.",
            ephemeral=True
        )

    # =====================================================
    # TEST NOTIFICATIONS
    # =====================================================

    @app_commands.command(
        name="testnotify",
        description="Test Discord + Telegram alerts"
    )
    @app_commands.checks.has_permissions(administrator=True)
    async def testnotify(
        self,
        interaction: discord.Interaction,
        user: discord.Member
    ):

        results = await self.notify_member(
            user.id,
            "This is a test notification from Evony Shield Watch.",
            "Test Alert"
        )

        msg = (
            f"📨 Discord: {'✅' if results['discord'] else '❌'}\n"
            f"📲 Telegram: {'✅' if results['telegram'] else '❌'}"
        )

        await interaction.response.send_message(
            msg,
            ephemeral=True
        )


# =========================================================
# SETUP
# =========================================================

async def setup(bot: commands.Bot):
    await bot.add_cog(Reminders(bot))
