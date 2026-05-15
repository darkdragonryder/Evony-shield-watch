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

        self.service = TelegramService()

        self.app.add_handler(CommandHandler("start", self.start_command))

    # =====================================================
    # /START TOKEN
    # =====================================================

    async def start_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):

        telegram_user = update.effective_user

        telegram_id = str(telegram_user.id)
        username = telegram_user.username or telegram_user.first_name

        if not context.args:
            await update.message.reply_text(
                "❌ Missing token. Use /linktelegram in Discord first."
            )
            return

        token = context.args[0]

        success, message = await self.service.link_account(
            token,
            telegram_id,
            username
        )

        await update.message.reply_text(message)

    # =====================================================
    # RUN
    # =====================================================

    def run(self):

        print("📲 Telegram Bot Running...")
        self.app.run_polling()


if __name__ == "__main__":

    TelegramBotService().run()
