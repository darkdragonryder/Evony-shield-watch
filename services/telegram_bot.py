"""
=========================================================
 Evony Shield Watch
 Telegram Bot Service (Polling Mode)
=========================================================
"""

# =========================================================
# IMPORTS
# =========================================================

import asyncio
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

from config import Config
from database import db
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

        # register handlers
        self.app.add_handler(CommandHandler("start", self.start_command))

    # =====================================================
    # START COMMAND (/start TOKEN)
    # =====================================================

    async def start_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):

        telegram_user = update.effective_user

        telegram_id = str(telegram_user.id)
        username = telegram_user.username or telegram_user.first_name

        # -------------------------------------------------
        # get token from /start argument
        # -------------------------------------------------

        token = None

        if context.args and len(context.args) > 0:
            token = context.args[0]

        if not token:

            await update.message.reply_text(
                "❌ No linking token provided.\n"
                "Please run /linktelegram in Discord first."
            )
            return

        # -------------------------------------------------
        # link account
        # -------------------------------------------------

        result = await self.bridge.handle_start_command(
            telegram_id,
            username,
            token
        )

        await update.message.reply_text(result)

    # =====================================================
    # RUN BOT
    # =====================================================

    def run(self):

        print("📲 Telegram Bot Service Starting...")

        self.app.run_polling()


# =========================================================
# ENTRY POINT
# =========================================================

if __name__ == "__main__":

    bot = TelegramBotService()
    bot.run()
