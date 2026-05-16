"""
=========================================================
Evony Shield Watch Config
CLEAN PRODUCTION VERSION (SVS / KE RESET SYSTEM)
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

    # =====================================================
    # TELEGRAM
    # =====================================================
    TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

    @staticmethod
    def has_telegram() -> bool:
        return bool(Config.TELEGRAM_BOT_TOKEN)


    TELEGRAM_LINK_EXPIRE_MINUTES = int(
        os.getenv("TELEGRAM_LINK_EXPIRE_MINUTES", 10)
    )

    # =====================================================
    # TIME / RESET SYSTEM (SOURCE OF TRUTH)
    # =====================================================
    HOST_TIMEZONE = os.getenv("HOST_TIMEZONE", "UTC")

    RESET_HOUR = int(os.getenv("RESET_HOUR", 17))
    RESET_MINUTE = int(os.getenv("RESET_MINUTE", 0))

    # =====================================================
    # WEEK EVENTS (CORE SYSTEM)
    # =====================================================
    SVS = "svs"
    KE = "ke"

    EVENT_TYPES = [SVS, KE]

    # =====================================================
    # CUSTOM EVENTS
    # =====================================================
    CUSTOM_EVENT_TYPES = ["boc", "bog", "allstars", "battlefield"]

    # =====================================================
    # REMINDER OFFSETS (IMPORTANT)
    # =====================================================

    # SVS timing
    SVS_PURGE_OFFSET_HOURS = 1
    SVS_PURGE_OFFSET_MINUTES = 39
    SVS_WARNING_OFFSET_HOURS = 1

    # KE timing
    KE_WARNING_OFFSET_HOURS = 1

    # =====================================================
    # EVENT CLEANUP
    # =====================================================
    EVENT_CLEANUP_DELAY = 300  # seconds after event end

    # =====================================================
    # WEB DASHBOARD
    # =====================================================
    WEB_SECRET = os.getenv("WEB_SECRET", "change-me")

    # =====================================================
    # SAFETY HELPERS
    # =====================================================

    @staticmethod
    def get_svs_purge_offset():
        from datetime import timedelta
        return timedelta(
            hours=Config.SVS_PURGE_OFFSET_HOURS,
            minutes=Config.SVS_PURGE_OFFSET_MINUTES
        )

    @staticmethod
    def get_svs_warning_offset():
        from datetime import timedelta
        return timedelta(hours=Config.SVS_WARNING_OFFSET_HOURS)

    @staticmethod
    def get_ke_warning_offset():
        from datetime import timedelta
        return timedelta(hours=Config.KE_WARNING_OFFSET_HOURS)
