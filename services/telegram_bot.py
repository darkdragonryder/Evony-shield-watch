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

        self.bridge = TelegramService()

        self.app.add_handler(CommandHandler("start", self.start))

        self._running = False
        self._started = False

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
            print(f"[Telegram ERROR] {e}")
            await update.message.reply_text(
                "❌ Telegram linking failed. Try again later."
            )

    # =====================================================
    # START BOT (SAFE MODE FOR DISCORD INTEGRATION)
    # =====================================================
    async def start_async(self):

        if self._started:
            return

        self._started = True
        self._running = True

        print("\n=================================================")
        print("📱 STARTING TELEGRAM BOT")
        print("=================================================\n")

        await self.app.initialize()

        # Prevent double start crash
        if not self.app.running:
            await self.app.start()

        if self.app.updater:
            await self.app.updater.start_polling()

        print("✅ Telegram bot running")

    # =====================================================
    # STOP BOT (SAFE SHUTDOWN)
    # =====================================================
    async def stop_async(self):

        if not self._running:
            return

        print("🛑 Stopping Telegram bot...")

        try:
            if self.app.updater:
                await self.app.updater.stop()
        except Exception:
            pass

        try:
            await self.app.stop()
        except Exception:
            pass

        try:
            await self.app.shutdown()
        except Exception:
            pass

        self._running = False
        self._started = False

        print("✅ Telegram bot stopped cleanly")

    # =====================================================
    # SIMPLE RUN (STANDALONE MODE ONLY)
    # =====================================================
    def run(self):

        print("\n=================================================")
        print("📱 TELEGRAM BOT STARTING (STANDALONE)")
        print("=================================================\n")

        self.app.run_polling()
