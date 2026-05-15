"""
=========================================================
 Telegram Bot Service (Polling Mode)
=========================================================
"""

from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

from config import Config
from services.telegram_service import TelegramService


class TelegramBotService:

    def __init__(self):

        self.app = Application.builder().token(
            Config.TELEGRAM_BOT_TOKEN
        ).build()

        self.bridge = TelegramService()

        self.app.add_handler(CommandHandler("start", self.start))

    async def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE):

        user = update.effective_user

        telegram_id = str(user.id)
        username = user.username or user.first_name

        token = context.args[0] if context.args else None

        if not token:
            await update.message.reply_text(
                "❌ Missing token. Use /linktelegram in Discord."
            )
            return

        result = await self.bridge.handle_start(
            telegram_id,
            username,
            token
        )

        await update.message.reply_text(result)

    def run(self):
        print("📲 Telegram Bot Starting...")
        self.app.run_polling()
