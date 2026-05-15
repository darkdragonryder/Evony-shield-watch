"""
=========================================================
 Evony Shield Watch
 Config System (Enterprise Ready)
=========================================================
"""

import os
from dotenv import load_dotenv

load_dotenv()


class Config:

    # =====================================================
    # DISCORD
    # =====================================================

    DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
    GUILD_ID = int(os.getenv("GUILD_ID", "0"))

    # =====================================================
    # TELEGRAM
    # =====================================================

    TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
    TELEGRAM_LINK_EXPIRE_MINUTES = int(
        os.getenv("TELEGRAM_LINK_EXPIRE_MINUTES", "10")
    )

    # =====================================================
    # DATABASE
    # =====================================================

    DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///shield.db")

    # =====================================================
    # ROLES (WEB DASHBOARD READY)
    # =====================================================

    ROLE_OWNER = "owner"
    ROLE_ADMIN = "admin"
    ROLE_COORDINATOR = "coordinator"
    ROLE_MEMBER = "member"

    # =====================================================
    # FEATURE FLAGS
    # =====================================================

    ENABLE_TELEGRAM = True
    ENABLE_DISCORD = True
    ENABLE_WEB_DASHBOARD = False
