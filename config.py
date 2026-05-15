"""
=========================================================
 Evony Shield Watch
 Configuration Layer (Environment + Settings)
=========================================================
"""

# =========================================================
# IMPORTS
# =========================================================

import os
from dotenv import load_dotenv

load_dotenv()


# =========================================================
# CONFIG CLASS
# =========================================================

class Config:

    # =====================================================
    # DISCORD SETTINGS
    # =====================================================

    DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")


    # =====================================================
    # TELEGRAM SETTINGS
    # =====================================================

    TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
    TELEGRAM_LINK_EXPIRE_MINUTES = int(
        os.getenv("TELEGRAM_LINK_EXPIRE_MINUTES", "10")
    )


    # =====================================================
    # DATABASE SETTINGS
    # =====================================================

    DB_PATH = os.getenv("DB_PATH", "data.db")


    # =====================================================
    # WEB DASHBOARD SETTINGS
    # =====================================================

    WEB_SECRET_KEY = os.getenv("WEB_SECRET_KEY", "change_me")
    WEB_HOST = os.getenv("WEB_HOST", "0.0.0.0")
    WEB_PORT = int(os.getenv("WEB_PORT", "5000"))
