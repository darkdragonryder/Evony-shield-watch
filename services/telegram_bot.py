"""
Evony Shield Watch
Telegram Bridge Service (HARDENED + PRODUCTION SAFE)
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
    # START
    # =====================================================

    async def start_async(self):

        async with self._lock:

            if self.running:
                return

            self.session = aiohttp.ClientSession()
            self.running = True

            print("📲 Telegram service started")

    # =====================================================
    # STOP
    # =====================================================

    async def stop_async(self):

        async with self._lock:

            self.running = False

            if self.session and not self.session.closed:
                await self.session.close()

            self.session = None

            print("📲 Telegram service stopped")

    # =====================================================
    # HEALTH CHECK
    # =====================================================

    def is_ready(self) -> bool:

        return (
            self.running
            and self.session is not None
            and not self.session.closed
        )

    # =====================================================
    # SEND MESSAGE (HARDENED)
    # =====================================================

    async def send_message(self, chat_id: str, text: str, title: str = "Alert") -> bool:

        if not Config.TELEGRAM_BOT_TOKEN:
            return False

        if not self.is_ready():
            return False

        url = f"https://api.telegram.org/bot{Config.TELEGRAM_BOT_TOKEN}/sendMessage"

        payload = {
            "chat_id": chat_id,
            "text": f"🛡️ {title}\n\n{text}",
            "parse_mode": "HTML",
            "disable_web_page_preview": True
        }

        for attempt in range(3):

            try:

                async with self.session.post(
                    url,
                    data=payload,
                    timeout=aiohttp.ClientTimeout(total=10)
                ) as resp:

                    # -------------------------------------------------
                    # SUCCESS
                    # -------------------------------------------------
                    if resp.status == 200:
                        return True

                    body = await resp.text()

                    # -------------------------------------------------
                    # NON-RETRYABLE ERRORS
                    # -------------------------------------------------
                    if resp.status in (400, 401, 403, 404):
                        logging.error(f"Telegram fatal error {resp.status}: {body}")
                        return False

                    # -------------------------------------------------
                    # RATE LIMIT HANDLING
                    # -------------------------------------------------
                    if resp.status == 429:
                        retry_after = resp.headers.get("Retry-After")

                        wait_time = int(retry_after) if retry_after else 5

                        logging.warning(f"Telegram rate limited, waiting {wait_time}s")
                        await asyncio.sleep(wait_time)
                        continue

                    logging.warning(f"Telegram error {resp.status}: {body}")

            except asyncio.TimeoutError:
                logging.warning("Telegram timeout, retrying...")

            except Exception as e:
                logging.error(f"Telegram exception: {e}")

            await asyncio.sleep(2 * (attempt + 1))

        return False

    # =====================================================
    # SAFE WRAPPER
    # =====================================================

    async def notify(self, chat_id: str, message: str, title: str = "Evony Alert"):

        try:
            return await self.send_message(chat_id, message, title)

        except Exception as e:
            logging.error(f"Telegram notify failed: {e}")
            return False
