"""
=========================================================
 Evony Shield Watch
 Configuration Layer (Discord + Telegram Only)
=========================================================
"""

# =========================================================
# IMPORTS
# =========================================================

import os
from dotenv import load_dotenv
from datetime import timedelta

# =========================================================
# LOAD ENV
# =========================================================

load_dotenv()

# =========================================================
# CONFIG CLASS
# =========================================================

class Config:

    # -----------------------------------------------------
    # DISCORD CORE
    # -----------------------------------------------------

    DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
    OWNER_ID = int(os.getenv("OWNER_ID", "0"))

    # -----------------------------------------------------
    # TELEGRAM INTEGRATION
    # -----------------------------------------------------

    TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

    # how long a login/link token is valid (for account linking)
    TELEGRAM_LINK_EXPIRE_MINUTES = int(
        os.getenv("TELEGRAM_LINK_EXPIRE_MINUTES", "10")
    )

    @classmethod
    def has_telegram(cls):
        return bool(cls.TELEGRAM_BOT_TOKEN)

    # -----------------------------------------------------
    # TIME SETTINGS
    # -----------------------------------------------------

    HOST_TIMEZONE = os.getenv("HOST_TIMEZONE", "America/New_York")

    RESET_HOUR = int(os.getenv("RESET_HOUR", "17"))
    RESET_MINUTE = int(os.getenv("RESET_MINUTE", "0"))

    EVENT_END_DAY = 0  # Monday

    # -----------------------------------------------------
    # EVENT TYPES
    # -----------------------------------------------------

    SVS = "svs"
    KE = "ke"

    BOC = "boc"
    BOG = "bog"
    ALLSTARS = "allstars"
    BATTLEFIELD = "battlefield"

    CUSTOM_EVENT_TYPES = [
        BOC,
        BOG,
        ALLSTARS,
        BATTLEFIELD
    ]

    # -----------------------------------------------------
    # REMINDER TIMINGS
    # -----------------------------------------------------

    SVS_FIRST_REMINDER = timedelta(hours=1, minutes=39)
    SVS_SECOND_REMINDER = timedelta(hours=1)
    SVS_PURGE_OFFSET = timedelta(hours=1)

    KE_REMINDER = timedelta(hours=1)

    EVENT_CLEANUP_DELAY = timedelta(minutes=10)
    DEFAULT_CUTOFF_MINUTES = 30

    # -----------------------------------------------------
    # CHANNEL DEFAULTS
    # -----------------------------------------------------

    DEFAULT_BUBBLE_CHANNEL = "🫧bubble🫧"
    DEFAULT_BATTLEFIELD_CHANNEL = "battlefield-messages"

    # -----------------------------------------------------
    # DASHBOARD (READY FOR LATER)
    # -----------------------------------------------------

    DASHBOARD_SECRET_KEY = os.getenv("DASHBOARD_SECRET_KEY", "change_me")

    DASHBOARD_PORT = int(os.getenv("DASHBOARD_PORT", "8080"))
