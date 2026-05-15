"""
=========================================================
 Evony Shield Watch
 Telegram Linking + Notification Bridge
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
# TELEGRAM COG
# =========================================================

class TelegramBridge(commands.Cog):

    def __init__(self, bot: commands.Bot):
        self.bot = bot

    # =====================================================
    # LINK TELEGRAM COMMAND
    # =====================================================

    @app_commands.command(
        name="linktelegram",
        description="Link your Discord account to Telegram"
    )
    async def linktelegram(self, interaction: discord.Interaction):

        # -------------------------------------------------
        # generate secure token
        # -------------------------------------------------

        token = secrets.token_urlsafe(8)

        expiry = datetime.utcnow() + timedelta(
            minutes=Config.TELEGRAM_LINK_EXPIRE_MINUTES
        )

        await db.create_telegram_link_token(
            interaction.user.id,
            token,
            expiry
        )

        # -------------------------------------------------
        # Telegram bot link
        # -------------------------------------------------

        bot_username = Config.TELEGRAM_BOT_TOKEN.split(":")[0] if Config.TELEGRAM_BOT_TOKEN else "your_bot"

        link_url = (
            f"https://t.me/{bot_username}"
            f"?start={token}"
        )

        embed = discord.Embed(
            title="📲 Link Your Telegram",
            description=(
                "Click below to link your Telegram account.\n\n"
                f"🔐 Token expires in **{Config.TELEGRAM_LINK_EXPIRE_MINUTES} minutes**\n\n"
                "👉 Open Telegram and press Start"
            ),
            color=0x3498db
        )

        embed.add_field(
            name="🔗 Link Button",
            value=link_url,
            inline=False
        )

        embed.add_field(
            name="⚠️ Important",
            value="Do NOT share this link with anyone.",
            inline=False
        )

        await interaction.response.send_message(embed=embed, ephemeral=True)

    # =====================================================
    # UNLINK TELEGRAM
    # =====================================================

    @app_commands.command(
        name="unlinktelegram",
        description="Remove your Telegram connection"
    )
    async def unlinktelegram(self, interaction: discord.Interaction):

        await db.set_member_contact(
            interaction.user.id,
            telegram_id=None,
            telegram_username=None
        )

        await interaction.response.send_message(
            "❌ Telegram unlinked successfully.",
            ephemeral=True
        )

    # =====================================================
    # ADMIN CHECK LINK STATUS
    # =====================================================

    @app_commands.command(
        name="telegramstatus",
        description="Check Telegram link status (Admin only)"
    )
    @app_commands.checks.has_permissions(administrator=True)
    async def telegramstatus(
        self,
        interaction: discord.Interaction,
        user: discord.Member
    ):

        data = await db.get_member_contact(user.id)

        if not data or not data.get("telegram_id"):

            return await interaction.response.send_message(
                f"❌ {user.mention} is NOT linked to Telegram.",
                ephemeral=True
            )

        embed = discord.Embed(
            title="📲 Telegram Linked",
            color=0x2ecc71
        )

        embed.add_field(
            name="User",
            value=user.mention,
            inline=False
        )

        embed.add_field(
            name="Telegram ID",
            value=data.get("telegram_id"),
            inline=False
        )

        embed.add_field(
            name="Username",
            value=data.get("telegram_username") or "Unknown",
            inline=False
        )

        await interaction.response.send_message(embed=embed, ephemeral=True)


# =========================================================
# TELEGRAM BOT WEBHOOK HANDLER (OPTIONAL SIMPLE POLLING HOOK)
# =========================================================

class TelegramService:

    """
    This is NOT a full bot framework.
    It is a lightweight bridge for webhook/polling integration.
    """

    def __init__(self):
        self.token = Config.TELEGRAM_BOT_TOKEN

    # -----------------------------------------------------
    # HANDLE /start TOKEN FROM TELEGRAM
    # -----------------------------------------------------

    async def handle_start_command(self, telegram_id: str, username: str, token: str):

        # link account in DB
        await db.link_telegram_user(token, telegram_id, username)

        return "✅ Telegram successfully linked to Discord account!"


# =========================================================
# SETUP FUNCTION
# =========================================================

async def setup(bot: commands.Bot):

    await bot.add_cog(TelegramBridge(bot))
