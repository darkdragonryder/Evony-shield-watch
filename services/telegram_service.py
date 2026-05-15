"""
=========================================================
 Telegram Service (Business Logic Layer)
=========================================================
"""

from database import db
from datetime import datetime


class TelegramService:

    # =====================================================
    # LINK TELEGRAM ACCOUNT
    # =====================================================

    async def link_account(self, token: str, telegram_id: str, username: str):

        record = await db.get_telegram_token(token)

        if not record:
            return False, "❌ Invalid token"

        if record["expires_at"] < datetime.utcnow():
            return False, "❌ Token expired"

        await db.link_telegram_user(
            token=token,
            telegram_id=telegram_id,
            username=username,
            discord_id=record["discord_id"]
        )

        return True, "✅ Telegram linked successfully"

    # =====================================================
    # UNLINK TELEGRAM
    # =====================================================

    async def unlink_account(self, discord_id: int):

        await db.set_member_contact(
            discord_id,
            telegram_id=None,
            telegram_username=None
        )

        return True

    # =====================================================
    # GET STATUS
    # =====================================================

    async def get_status(self, discord_id: int):

        return await db.get_member_contact(discord_id)
