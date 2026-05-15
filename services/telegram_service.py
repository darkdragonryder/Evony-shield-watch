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

        # =====================================================
        # BASIC VALIDATION
        # =====================================================
        if not telegram_id:
            return "❌ Missing Telegram ID."

        if not token or not isinstance(token, str):
            return "❌ Missing or invalid token."

        token = token.strip()

        if not token:
            return "❌ Empty token provided."

        # Safe username fallback
        if not username:
            username = "unknown"

        try:
            # =================================================
            # LINK USER IN DATABASE
            # =================================================
            success = await db.link_telegram_user(
                token,
                telegram_id,
                username
            )

            # =================================================
            # RESULT HANDLING
            # =================================================
            if not success:
                return "❌ Invalid or expired token."

            return "✅ Telegram linked successfully!"

        except Exception as e:
            print("\n=================================================")
            print("❌ TELEGRAM SERVICE ERROR")
            print("=================================================")
            print(f"Telegram ID: {telegram_id}")
            print(f"Username: {username}")
            print(f"Token: {token}")
            print(f"Error: {e}")
            print("=================================================\n")

            return "❌ Database error while linking account. Try again later."
