"""
Evony Shield Watch - Configuration (Enterprise + Telegram)
"""

import os
from datetime import timedelta
from dotenv import load_dotenv

load_dotenv()


class Config:

    # =========================================================
    # CORE
    # =========================================================

    TOKEN = os.getenv("DISCORD_TOKEN")
    OWNER_ID = int(os.getenv("OWNER_ID", "0"))

    HOST_TIMEZONE = os.getenv("HOST_TIMEZONE", "America/New_York")
    RESET_HOUR = int(os.getenv("RESET_HOUR", "17"))
    RESET_MINUTE = int(os.getenv("RESET_MINUTE", "0"))

    # =========================================================
    # EVENTS
    # =========================================================

    SVS_FIRST_REMINDER = timedelta(hours=1, minutes=39)
    SVS_SECOND_REMINDER = timedelta(hours=1)
    SVS_PURGE_OFFSET = timedelta(hours=1)

    KE_REMINDER = timedelta(hours=1)

    EVENT_END_DAY = 0
    EVENT_CLEANUP_DELAY = timedelta(minutes=10)

    DEFAULT_BUBBLE_CHANNEL = "🫧bubble🫧"
    DEFAULT_BATTLEFIELD_CHANNEL = "battlefield-messages"

    SVS = "svs"
    KE = "ke"

    # =========================================================
    # TELEGRAM (NEW)
    # =========================================================

    TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

    # token expiry for /linktelegram
    TELEGRAM_LINK_EXPIRE_MINUTES = int(
        os.getenv("TELEGRAM_LINK_EXPIRE_MINUTES", "10")
    )

    @classmethod
    def has_telegram(cls):
        return bool(cls.TELEGRAM_BOT_TOKEN)
