"""
=========================================================
 Telegram Bot Service (Polling Mode)
 Clean Stable Runner - Evony Shield Watch
=========================================================
"""

from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    ContextTypes,
)

from config import Config
from services.telegram_service import TelegramService


class TelegramBotService:

    def __init__(self):

        # =====================================================
        # APPLICATION SETUP
        # =====================================================
        self.app = (
            Application.builder()
            .token(Config.TELEGRAM_BOT_TOKEN)
            .build()
        )

        self.bridge = TelegramService()

        # Handlers
        self.app.add_handler(CommandHandler("start", self.start))

        # State tracking (VERY IMPORTANT FOR VM STABILITY)
        self._running = False
        self._task = None

    # =====================================================
    # START COMMAND (/start)
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

        token = context.args[0] if context.args else None

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
    # START BOT (SAFE VM-PROOF VERSION)
    # =====================================================
    async def start_async(self):

        if self._running:
            print("⚠️ Telegram already running - ignoring duplicate start")
            return

        self._running = True

        print("\n=================================================")
        print("📱 STARTING TELEGRAM BOT")
        print("=================================================\n")

        try:
            # SAFE INIT FLOW (PTB v20+ correct order)
            await self.app.initialize()
            await self.app.start()

            # Polling runs as background task safely
            self._task = await self.app.updater.start_polling()

            print("✅ Telegram bot running")

        except Exception as e:
            self._running = False
            print(f"❌ Telegram failed to start: {e}")

    # =====================================================
    # STOP BOT (SAFE CLEAN SHUTDOWN)
    # =====================================================
    async def stop_async(self):

        if not self._running:
            return

        print("\n🛑 Stopping Telegram bot...")

        try:
            if self.app.updater:
                await self.app.updater.stop()

            await self.app.stop()
            await self.app.shutdown()

        except Exception as e:
            print(f"⚠️ Telegram shutdown warning: {e}")

        self._running = False
        self._task = None

        print("✅ Telegram bot stopped cleanly")

    # =====================================================
    # OPTIONAL: BLOCKING RUN (ONLY FOR LOCAL TESTING)
    # =====================================================
    def run(self):

        print("\n=================================================")
        print("📱 TELEGRAM BOT STARTING (STANDALONE)")
        print("=================================================\n")

        self.app.run_polling()
