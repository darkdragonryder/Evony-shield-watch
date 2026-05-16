"""
=========================================================
Evony Shield Watch
Reminders System (CLEAN EVENT PHASE ENGINE)
Discord + Telegram (QUEUE SAFE)
=========================================================
"""

import discord
from discord.ext import commands
from datetime import datetime

from database import db
from utils.time_utils import get_user_local_reset_time, format_local_time


class Reminders(commands.Cog):

    def __init__(self, bot: commands.Bot):
        self.bot = bot

    # =====================================================
    # CORE NOTIFICATION ENGINE
    # =====================================================

    async def notify_member(self, user_id: int, message: str, title: str, telegram_service=None):

        contact = await db.get_member_contact(user_id)
        if not contact:
            return

        results = {
            "discord": False,
            "telegram": False
        }

        user = self.bot.get_user(user_id)

        # =================================================
        # DISCORD DM (STRICT OPT-IN CHECK FIXED)
        # =================================================
        if user and contact.get("opt_in") == 1:

            try:

                embed = discord.Embed(
                    title=title,
                    description=message,
                    color=0xFF4B4B,
                    timestamp=datetime.utcnow()
                )

                await user.send(embed=embed)
                results["discord"] = True

            except Exception:
                pass

        # =================================================
        # TELEGRAM (SAFE OPTIONAL LAYER)
        # =================================================
        if telegram_service and contact.get("telegram_id"):

            try:

                sent = await telegram_service.send_message(
                    chat_id=contact["telegram_id"],
                    text=message,
                    title=title
                )

                results["telegram"] = bool(sent)

            except Exception:
                pass

        return results

    # =====================================================
    # MY TIME
    # =====================================================

    @commands.hybrid_command(name="mytime")
    async def mytime(self, ctx: commands.Context):

        contact = await db.get_member_contact(ctx.author.id)

        tz = contact.get("timezone", "UTC") if contact else "UTC"

        local = get_user_local_reset_time(tz)
        formatted = format_local_time(local)

        embed = discord.Embed(
            title="⏰ Your Local Reset Time",
            description=f"Server reset in your timezone:\n\n**{formatted}**",
            color=0x3498db
        )

        embed.add_field(name="Timezone", value=tz, inline=False)

        await ctx.send(embed=embed)

    # =====================================================
    # SET TIMEZONE
    # =====================================================

    @commands.hybrid_command(name="settimezone")
    async def settimezone(self, ctx: commands.Context, timezone: str):

        import pytz

        try:
            pytz.timezone(timezone)

            await db.set_member_contact(
                ctx.author.id,
                timezone=timezone
            )

            await ctx.send(f"✅ Timezone set to **{timezone}**")

        except pytz.UnknownTimeZoneError:
            await ctx.send("❌ Invalid timezone (e.g. Europe/London, Asia/Tokyo)")

    # =====================================================
    # OPT OUT
    # =====================================================

    @commands.hybrid_command(name="optout")
    async def optout(self, ctx: commands.Context):

        await db.set_member_contact(
            ctx.author.id,
            opt_in=0
        )

        await ctx.send("🔕 Notifications disabled.")

    # =====================================================
    # OPT IN
    # =====================================================

    @commands.hybrid_command(name="optin")
    async def optin(self, ctx: commands.Context):

        await db.set_member_contact(
            ctx.author.id,
            opt_in=1
        )

        await ctx.send("🔔 Notifications enabled.")

    # =====================================================
    # TEST NOTIFY
    # =====================================================

    @commands.hybrid_command(name="testnotify")
    @commands.has_permissions(administrator=True)
    async def testnotify(self, ctx: commands.Context, user: discord.Member):

        telegram_service = getattr(self.bot, "telegram", None)

        results = await self.notify_member(
            user.id,
            "This is a test notification from Evony Shield Watch.",
            "Test Alert",
            telegram_service=telegram_service
        )

        await ctx.send(
            f"📨 Discord: {'✅' if results['discord'] else '❌'}\n"
            f"📲 Telegram: {'✅' if results['telegram'] else '❌'}"
        )


async def setup(bot: commands.Bot):
    await bot.add_cog(Reminders(bot))
