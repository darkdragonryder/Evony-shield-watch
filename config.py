"""
=========================================================
 Evony Shield Watch Config
=========================================================
"""

import os
from dotenv import load_dotenv

load_dotenv()


class Config:

    # =====================================================
    # DISCORD
    # =====================================================

    TOKEN = os.getenv("DISCORD_TOKEN")
    OWNER_ID = int(os.getenv("OWNER_ID", 0))

    # =====================================================
    # TELEGRAM
    # =====================================================

    TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

    TELEGRAM_LINK_EXPIRE_MINUTES = int(
        os.getenv("TELEGRAM_LINK_EXPIRE_MINUTES", 10)
    )

    # =====================================================
    # DATABASE
    # =====================================================

    DATABASE_PATH = os.getenv(
        "DATABASE_PATH",
        "evony_bot.db"
    )

    # =====================================================
    # EVENT TYPES
    # =====================================================

    SVS = "svs"
    KE = "ke"

    # =====================================================
    # DEFAULT CHANNELS
    # =====================================================

    DEFAULT_BUBBLE_CHANNEL = "🫧bubble🫧"
    DEFAULT_BATTLEFIELD_CHANNEL = "⚔️battlefield⚔️"

    # =====================================================
    # SERVER RESET CONFIG
    # =====================================================

    HOST_TIMEZONE = os.getenv(
        "HOST_TIMEZONE",
        "America/New_York"
    )

    RESET_HOUR = int(
        os.getenv("RESET_HOUR", 17)
    )

    RESET_MINUTE = int(
        os.getenv("RESET_MINUTE", 0)
    )

    # =====================================================
    # WEB DASHBOARD
    # =====================================================

    WEB_SECRET = os.getenv(
        "WEB_SECRET",
        "change-me"
    )
