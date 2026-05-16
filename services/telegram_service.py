"""
Telegram Service Layer
Discord ↔ Telegram Bridge Logic (HARDENED)
"""

import logging
from database import db


class TelegramService:

    # =====================================================
    # HANDLE LINKING
    # =====================================================

    async def handle_start(self, telegram_id, username, token):
        """
        Links a Telegram user to a Discord account using a token.
        Returns structured result dict for safe integration.
        """

        # -------------------------------------------------
        # VALIDATION
        # -------------------------------------------------

        if not telegram_id:
            return {
                "ok": False,
                "error": "Missing Telegram ID"
            }

        if not token or not isinstance(token, str):
            return {
                "ok": False,
                "error": "Missing or invalid token"
            }

        token = token.strip()

        if not token:
            return {
                "ok": False,
                "error": "Empty token provided"
            }

        username = username or "unknown"

        # -------------------------------------------------
        # DATABASE LINK
        # -------------------------------------------------

        try:

            success = await db.link_telegram_user(
                token,
                telegram_id,
                username
            )

            if not success:
                return {
                    "ok": False,
                    "error": "Invalid or expired token"
                }

            return {
                "ok": True,
                "message": "Telegram linked successfully"
            }

        except Exception as e:

            logging.error(
                "Telegram linking failed",
                extra={
                    "telegram_id": telegram_id,
                    "username": username,
                    "token": token,
                    "error": str(e)
                }
            )

            return {
                "ok": False,
                "error": "Database error while linking account"
            }
