"""

 Evony Shield Watch
 Telegram Bridge (Guild Bound - FIXED & HARDENED)

"""

import discord
from discord.ext import commands
from discord import app_commands

import secrets
from datetime import datetime, timedelta

from config import Config
from database import db


class TelegramBridge(commands.Cog):

    def __init__(self, bot: commands.Bot):
        self.bot = bot

    # =====================================================
    # LINK TELEGRAM
    # =====================================================

    @app_commands.command(name="linktelegram")
    async def linktelegram(self, interaction: discord.Interaction):

        if not interaction.guild:
            return await interaction.response.send_message(
                "❌ Guild only command.",
                ephemeral=True
            )

        user_id = interaction.user.id
        guild_id = interaction.guild.id

        token = secrets.token_urlsafe(8)

        expiry = datetime.utcnow() + timedelta(
            minutes=Config.TELEGRAM_LINK_EXPIRE_MINUTES
        )

        # FIX: correct DB signature (user_id, token, expiry)
        await db.create_telegram_link_token(
            user_id,
            token,
            expiry
        )

        # Bot username must be hard-configured (TOKEN split is unsafe)
        bot_username = Config.TELEGRAM_BOT_USERNAME

        url = f"https://t.me/{bot_username}?start={token}"

        await interaction.response.send_message(
            f"📲 Click to link Telegram:\n{url}",
            ephemeral=True
        )

    # =====================================================
    # UNLINK TELEGRAM
    # =====================================================

    @app_commands.command(name="unlinktelegram")
    async def unlinktelegram(self, interaction: discord.Interaction):

        await db.set_member_contact(
            interaction.user.id,
            telegram_id=None,
            telegram_username=None
        )

        await interaction.response.send_message(
            "❌ Telegram unlinked.",
            ephemeral=True
        )


# =========================================================
# TELEGRAM SERVICE (BOT SIDE HANDLER)
# =========================================================

class TelegramService:

    async def handle_start_command(self, telegram_id: str, username: str, token: str):

        # FIX: DB returns bool
        success = await db.link_telegram_user(
            token,
            telegram_id,
            username
        )

        return "✅ Linked successfully" if success else "❌ Invalid or expired token"


async def setup(bot):
    await bot.add_cog(TelegramBridge(bot))
