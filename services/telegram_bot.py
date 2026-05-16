"""

 Evony Shield Watch
 Telegram Bot Service (HARDENED CORE TRANSPORT LAYER)
 SINGLE RESPONSIBILITY: SEND + SESSION MANAGEMENT=========================================================
"""

import aiohttp
import asyncio
import logging
from config import Config


class TelegramBotService:

    def __init__(self):

        self.session: aiohttp.ClientSession | None = None
        self.running = False
        self._lock = asyncio.Lock()

    # =====================================================
    # START SERVICE
    # =====================================================

    async def start_async(self):

        async with self._lock:

            if self.running:
                return

            self.session = aiohttp.ClientSession()
            self.running = True

            print("📲 Telegram service ONLINE")

    # =====================================================
    # STOP SERVICE
    # =====================================================

    async def stop_async(self):

        async with self._lock:

            self.running = False

            if self.session:
                await self.session.close()
                self.session = None

            print("📲 Telegram service OFFLINE")

    # =====================================================
    # HEALTH CHECK
    # =====================================================

    def is_ready(self) -> bool:
        return self.running and self.session is not None

    # =====================================================
    # CORE SEND (RETRY SAFE + HARDENED)
    # =====================================================

    async def send_message(self, chat_id: str, text: str, title: str = "Alert") -> bool:

        if not self.is_ready():
            return False

        if not Config.TELEGRAM_BOT_TOKEN:
            return False

        url = f"https://api.telegram.org/bot{Config.TELEGRAM_BOT_TOKEN}/sendMessage"

        payload = {
            "chat_id": chat_id,
            "text": f"🛡️ {title}\n\n{text}",
            "parse_mode": "HTML",
            "disable_web_page_preview": True
        }

        # =================================================
        # RETRY SYSTEM (NETWORK RESILIENCE)
        # =================================================

        for attempt in range(3):

            try:
                async with self.session.post(url, data=payload, timeout=10) as resp:

                    if resp.status == 200:
                        return True

                    body = await resp.text()
                    logging.warning(f"Telegram error {resp.status}: {body}")

            except asyncio.TimeoutError:
                logging.warning("Telegram timeout retrying...")

            except Exception as e:
                logging.error(f"Telegram exception: {e}")

            await asyncio.sleep(2 * (attempt + 1))

        return False

    # =====================================================
    # SAFE WRAPPER (USED BY DISCORD SYSTEM)
    # =====================================================

    async def notify(self, chat_id: str, message: str, title: str = "Evony Alert"):

        try:
            return await self.send_message(chat_id, message, title)

        except Exception as e:
            logging.error(f"Telegram notify failed: {e}")
            return False
