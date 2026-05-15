"""
=========================================================
 Telegram Service Layer
 Discord ↔ Telegram Bridge Logic
=========================================================
"""

from database import db


class TelegramService:

    async def handle_start(self, telegram_id, username, token):
        """
        Links a Telegram user to a Discord account using a token.
        """

        if not telegram_id or not token:
            return "❌ Missing required data."

        try:
            success = await db.link_telegram_user(
                token,
                telegram_id,
                username
            )

            if not success:
                return "❌ Invalid or expired token."

            return "✅ Telegram linked successfully!"

        except Exception as e:
            print(f"[TelegramService ERROR] {e}")
            return "❌ Database error while linking account. Try again."
