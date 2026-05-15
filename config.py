"""
=========================================================
 Evony Shield Watch Config
=========================================================
"""

import os
from dotenv import load_dotenv

load_dotenv()


class Config:

    # =========================
    # DISCORD
    # =========================
    TOKEN = os.getenv("DISCORD_TOKEN")

    # =========================
    # TELEGRAM
    # =========================
    TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
    TELEGRAM_LINK_EXPIRE_MINUTES = int(
        os.getenv("TELEGRAM_LINK_EXPIRE_MINUTES", 10)
    )

    # =========================
    # EVENTS
    # =========================
    SVS = "svs"
    KE = "ke"

    # =========================
    # WEB DASHBOARD
    # =========================
    WEB_SECRET = os.getenv("WEB_SECRET", "change-me")
