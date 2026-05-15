"""
=========================================================
 Telegram Service Layer
 Discord ↔ Telegram Bridge Logic
=========================================================
"""

from database import db


class TelegramService:

    async def handle_start(self, telegram_id, username, token):

        success = await db.link_telegram_user(
            token,
            telegram_id,
            username
        )

        if not success:
            return "❌ Invalid or expired token."

        return "✅ Telegram linked successfully!"
