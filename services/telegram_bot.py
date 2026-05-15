"""
=========================================================
 Evony Shield Watch
 Telegram Bot Service (Polling Engine)
=========================================================
"""

# =========================================================
# IMPORTS
# =========================================================

from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

from config import Config
from cogs.telegram import TelegramService


# =========================================================
# TELEGRAM BOT SERVICE
# =========================================================

class TelegramBotService:

    def __init__(self):

        self.app = Application.builder().token(
            Config.TELEGRAM_BOT_TOKEN
        ).build()

        self.bridge = TelegramService()

        self.app.add_handler(CommandHandler("start", self.start))


    # =====================================================
    # /START HANDLER
    # =====================================================

    async def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE):

        user = update.effective_user

        token = context.args[0] if context.args else None

        if not token:
            await update.message.reply_text("❌ Missing token")
            return

        result = await self.bridge.handle_start_command(
            str(user.id),
            user.username or user.first_name,
            token
        )

        await update.message.reply_text(result)


    # =====================================================
    # RUN BOT
    # =====================================================

    def run(self):

        print("📲 Telegram Bot Starting...")

        self.app.run_polling()


# =========================================================
# ENTRY POINT
# =========================================================

if __name__ == "__main__":

    TelegramBotService().run()
