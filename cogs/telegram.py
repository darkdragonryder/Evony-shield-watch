"""
=========================================================
 Telegram Discord Bridge (UI Layer Only)
=========================================================
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

        token = secrets.token_urlsafe(8)

        expiry = datetime.utcnow() + timedelta(
            minutes=Config.TELEGRAM_LINK_EXPIRE_MINUTES
        )

        await db.create_telegram_link_token(
            interaction.user.id,
            token,
            expiry
        )

        bot_username = (
            Config.TELEGRAM_BOT_TOKEN.split(":")[0]
            if Config.TELEGRAM_BOT_TOKEN else "bot"
        )

        url = f"https://t.me/{bot_username}?start={token}"

        embed = discord.Embed(
            title="📲 Link Telegram",
            description="Click below to link your Telegram account",
            color=0x3498db
        )

        embed.add_field(name="Link", value=url, inline=False)

        await interaction.response.send_message(embed=embed, ephemeral=True)

    # =====================================================
    # UNLINK
    # =====================================================

    @app_commands.command(name="unlinktelegram")
    async def unlinktelegram(self, interaction: discord.Interaction):

        await db.set_member_contact(
            interaction.user.id,
            telegram_id=None,
            telegram_username=None
        )

        await interaction.response.send_message(
            "❌ Telegram unlinked",
            ephemeral=True
        )


async def setup(bot: commands.Bot):
    await bot.add_cog(TelegramBridge(bot))
