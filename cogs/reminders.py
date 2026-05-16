"""
=========================================================
 Evony Shield Watch
 Reminders System
 Discord + Telegram Notifications
=========================================================
"""

# =========================================================
# IMPORTS
# =========================================================

import discord
import aiohttp
import pytz

from datetime import datetime, UTC

from discord.ext import commands
from discord import app_commands

from config import Config
from database import db

from utils.time_utils import (
    get_user_local_reset_time,
    format_local_time
)


# =========================================================
# REMINDERS COG
# =========================================================

class Reminders(commands.Cog):

    def __init__(self, bot: commands.Bot):

        self.bot = bot
        self.session = aiohttp.ClientSession()

    # =====================================================
    # CLEANUP
    # =====================================================

    async def cog_unload(self):

        if not self.session.closed:
            await self.session.close()

    # =====================================================
    # TELEGRAM SENDER
    # =====================================================

    async def _send_telegram(
        self,
        telegram_id: str,
        message: str,
        title: str
    ) -> bool:

        if not Config.TELEGRAM_BOT_TOKEN:
            return False

        try:

            url = (
                f"https://api.telegram.org/bot"
                f"{Config.TELEGRAM_BOT_TOKEN}/sendMessage"
            )

            payload = {
                "chat_id": telegram_id,
                "text": (
                    f"🛡️ <b>{title}</b>\n\n"
                    f"{message}"
                ),
                "parse_mode": "HTML"
            }

            async with self.session.post(
                url,
                data=payload
            ) as response:

                return response.status == 200

        except Exception as e:

            print(f"[Telegram ERROR] {e}")
            return False

    # =====================================================
    # MAIN NOTIFICATION ENGINE
    # =====================================================

    async def notify_member(
        self,
        user_id: int,
        message: str,
        title: str = "Evony Alert"
    ):

        contact = await db.get_member_contact(user_id)

        if not contact:
            return {
                "discord": False,
                "telegram": False
            }

        results = {
            "discord": False,
            "telegram": False
        }

        # =================================================
        # DISCORD DM
        # =================================================

        discord_enabled = contact.get(
            "discord_opt_in",
            1
        )

        if discord_enabled:

            try:

                user = self.bot.get_user(user_id)

                if not user:
                    user = await self.bot.fetch_user(user_id)

                embed = discord.Embed(
                    title=title,
                    description=message,
                    color=0xE74C3C,
                    timestamp=datetime.now(UTC)
                )

                embed.set_footer(
                    text="Evony Shield Watch"
                )

                await user.send(embed=embed)

                results["discord"] = True

            except Exception as e:

                print(f"[Discord DM ERROR] {e}")

        # =================================================
        # TELEGRAM
        # =================================================

        telegram_id = contact.get("telegram_id")

        if telegram_id:

            results["telegram"] = await self._send_telegram(
                telegram_id,
                message,
                title
            )

        return results

    # =====================================================
    # MY TIME
    # =====================================================

    @app_commands.command(
        name="mytime",
        description="Check your local server reset time"
    )
    async def mytime(
        self,
        interaction: discord.Interaction
    ):

        contact = await db.get_member_contact(
            interaction.user.id
        )

        timezone = "UTC"

        if contact:
            timezone = contact.get(
                "timezone",
                "UTC"
            )

        local_time = get_user_local_reset_time(
            timezone
        )

        formatted = format_local_time(local_time)

        embed = discord.Embed(
            title="⏰ Your Local Reset Time",
            description=(
                "Server reset converts to:\n\n"
                f"**{formatted}**"
            ),
            color=0x3498db
        )

        embed.add_field(
            name="🌍 Timezone",
            value=timezone,
            inline=False
        )

        await interaction.response.send_message(
            embed=embed,
            ephemeral=True
        )

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
                (
                    "❌ Invalid timezone.\n\n"
                    "Example:\n"
                    "`Australia/Sydney`\n"
                    "`Europe/London`\n"
                    "`America/New_York`"
                ),
                ephemeral=True
            )

    # =====================================================
    # OPT OUT
    # =====================================================

    @app_commands.command(
        name="optout",
        description="Disable Discord notifications"
    )
    async def optout(
        self,
        interaction: discord.Interaction
    ):

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
    async def optin(
        self,
        interaction: discord.Interaction
    ):

        await db.set_member_contact(
            interaction.user.id,
            discord_opt_in=1
        )

        await interaction.response.send_message(
            "🔔 Discord notifications enabled.",
            ephemeral=True
        )

    # =====================================================
    # TEST NOTIFICATION
    # =====================================================

    @app_commands.command(
        name="testnotify",
        description="Test notifications"
    )
    @app_commands.checks.has_permissions(
        administrator=True
    )
    async def testnotify(
        self,
        interaction: discord.Interaction,
        user: discord.Member
    ):

        await interaction.response.defer(
            ephemeral=True
        )

        results = await self.notify_member(
            user.id,
            (
                "This is a test notification from "
                "Evony Shield Watch."
            ),
            "🧪 Test Alert"
        )

        message = (
            f"📨 Discord: "
            f"{'✅' if results['discord'] else '❌'}\n"
            f"📲 Telegram: "
            f"{'✅' if results['telegram'] else '❌'}"
        )

        await interaction.followup.send(
            message,
            ephemeral=True
        )


# =========================================================
# SETUP
# =========================================================

async def setup(bot: commands.Bot):

    await bot.add_cog(Reminders(bot))
