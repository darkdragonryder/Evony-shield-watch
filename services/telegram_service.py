"""
Telegram Service Layer
Handles secure linking + message sending
"""

import secrets
import aiohttp
from database import db
from config import Config


class TelegramService:

    # =========================================================
    # GENERATE LINK TOKEN
    # =========================================================
    @staticmethod
    async def generate_link_token(user_id: int):
        token = secrets.token_urlsafe(16)

        await db.set_member_contact(
            user_id,
            telegram_link_token=token
        )

        return token

    # =========================================================
    # VERIFY LINK TOKEN
    # =========================================================
    @staticmethod
    async def link_telegram(user_id: int, telegram_id: str, token: str):

        user = await db.get_member_contact(user_id)

        if not user:
            return False, "User not found"

        if user.get("telegram_link_token") != token:
            return False, "Invalid token"

        await db.set_member_contact(
            user_id,
            telegram_id=telegram_id,
            telegram_linked_at="now",
            telegram_link_token=None
        )

        return True, "Telegram linked successfully"

    # =========================================================
    # SEND TELEGRAM MESSAGE
    # =========================================================
    @staticmethod
    async def send_message(telegram_id: str, message: str):

        if not Config.TELEGRAM_BOT_TOKEN:
            return False

        url = f"https://api.telegram.org/bot{Config.TELEGRAM_BOT_TOKEN}/sendMessage"

        async with aiohttp.ClientSession() as session:
            async with session.post(url, json={
                "chat_id": telegram_id,
                "text": message,
                "parse_mode": "HTML"
            }) as resp:
                return resp.status == 200
