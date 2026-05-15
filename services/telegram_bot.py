"""
=========================================================
 Telegram Bot Service (Polling Mode)
 Clean Runner Layer - Evony Shield Watch
=========================================================
"""

from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

from config import Config
from services.telegram_service import TelegramService


class TelegramBotService:
    def __init__(self):

        # =====================================================
        # TELEGRAM APPLICATION
        # =====================================================
        self.app = (
            Application.builder()
            .token(Config.TELEGRAM_BOT_TOKEN)
            .build()
        )

        # Bridge (your logic layer)
        self.bridge = TelegramService()

        # Handlers
        self.app.add_handler(CommandHandler("start", self.start))

        self._running = False

    # =====================================================
    # /START HANDLER
    # =====================================================
    async def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE):

        if not update.message:
            return

        user = update.effective_user
        if not user:
            await update.message.reply_text("❌ User not found.")
            return

        telegram_id = str(user.id)
        username = user.username or user.first_name

        token = context.args[0] if context.args and len(context.args) > 0 else None

        if not token:
            await update.message.reply_text(
                "❌ Missing token.\nUse /linktelegram in Discord first."
            )
            return

        try:
            result = await self.bridge.handle_start(
                telegram_id,
                username,
                token
            )

            await update.message.reply_text(result)

        except Exception as e:
            await update.message.reply_text(
                "❌ Telegram linking failed. Try again later."
            )
            print(f"[Telegram ERROR] {e}")

    # =====================================================
    # START BOT (SAFE MODE)
    # =====================================================
    async def start_async(self):
        """
        Proper async startup (avoids 'not initialized' error in v22)
        """
        if self._running:
            return

        self._running = True

        print("\n=================================================")
        print("📱 STARTING TELEGRAM BOT")
        print("=================================================\n")

        await self.app.initialize()
        await self.app.start()
        await self.app.updater.start_polling()

        print("✅ Telegram bot running")

    # =====================================================
    # STOP BOT
    # =====================================================
    async def stop_async(self):
        if not self._running:
            return

        print("🛑 Stopping Telegram bot...")

        await self.app.updater.stop()
        await self.app.stop()
        await self.app.shutdown()

        self._running = False

        print("✅ Telegram bot stopped cleanly")

    # =====================================================
    # SIMPLE RUN (OPTIONAL MANUAL MODE)
    # =====================================================
    def run(self):
        """
        Used ONLY if running Telegram standalone
        """
        print("\n=================================================")
        print("📱 TELEGRAM BOT STARTING (STANDALONE)")
        print("=================================================\n")

        self.app.run_polling()
