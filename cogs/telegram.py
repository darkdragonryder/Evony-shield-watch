"""
=========================================================
 Evony Shield Watch
 Telegram Bridge (Discord ↔ Telegram Linking)
=========================================================
"""

# =========================================================
# IMPORTS
# =========================================================

import discord
from discord.ext import commands
from discord import app_commands

import secrets
from datetime import datetime, timedelta

from config import Config
from database import db


# =========================================================
# DISCORD TELEGRAM BRIDGE
# =========================================================

class TelegramBridge(commands.Cog):

    def __init__(self, bot):
        self.bot = bot


    # =====================================================
    # LINK TELEGRAM COMMAND
    # =====================================================

    @app_commands.command(name="linktelegram")
    async def linktelegram(self, interaction: discord.Interaction):

        token = secrets.token_urlsafe(8)

        expiry = datetime.utcnow() + timedelta(
            minutes=Config.TELEGRAM_LINK_EXPIRE_MINUTES
        )

        await db.create_telegram_link_token(
            interaction.user.id,
            token,
            expiry
        )

        bot_username = Config.TELEGRAM_BOT_TOKEN.split(":")[0]

        url = f"https://t.me/{bot_username}?start={token}"

        await interaction.response.send_message(
            f"🔗 Telegram Link:\n{url}",
            ephemeral=True
        )


    # =====================================================
    # UNLINK TELEGRAM
    # =====================================================

    @app_commands.command(name="unlinktelegram")
    async def unlinktelegram(self, interaction: discord.Interaction):

        await db.set_member_contact(interaction.user.id, None, None)

        await interaction.response.send_message(
            "❌ Telegram unlinked",
            ephemeral=True
        )


# =========================================================
# TELEGRAM SERVICE (LOGIC LAYER)
# =========================================================

class TelegramService:

    async def handle_start_command(self, telegram_id, username, token):

        success = await db.link_telegram_user(token, telegram_id, username)

        return "✅ Telegram Linked" if success else "❌ Invalid Token"


# =========================================================
# SETUP
# =========================================================

async def setup(bot):
    await bot.add_cog(TelegramBridge(bot))
