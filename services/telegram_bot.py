"""
=========================================================
Evony Shield Watch
Telegram Bot Service (STABLE + SAFE + NON-BLOCKING)
=========================================================
"""

import aiohttp
import asyncio
import logging

from config import Config


class TelegramBotService:

    def __init__(self):

        self.session = None
        self.running = False
        self.base_url = None

        # simple outbound queue to prevent spam bursts
        self.queue = asyncio.Queue()

        self.worker_task = None

    # =====================================================
    # STARTUP
    # =====================================================

    async def start_async(self):

        if not Config.has_telegram():
            print("⚠️ Telegram disabled (no token)")
            return

        if self.running:
            return

        self.session = aiohttp.ClientSession()

        self.base_url = f"https://api.telegram.org/bot{Config.TELEGRAM_BOT_TOKEN}"

        self.running = True

        # start worker
        self.worker_task = asyncio.create_task(self._worker())

        print("✅ Telegram service started")

    # =====================================================
    # STOP
    # =====================================================

    async def stop_async(self):

        self.running = False

        # stop worker
        if self.worker_task:
            self.worker_task.cancel()

        # close session safely
        if self.session:
            await self.session.close()

        print("🛑 Telegram service stopped")

    # =====================================================
    # PUBLIC SEND METHOD (SAFE ENTRY POINT)
    # =====================================================

    async def send_message(self, chat_id: str, text: str, title: str = None):

        if not Config.has_telegram():
            return False

        if not self.running:
            return False

        message = text

        if title:
            message = f"🛡️ {title}\n\n{text}"

        await self.queue.put((chat_id, message))

        return True

    # =====================================================
    # WORKER LOOP (PREVENTS RATE LIMIT + CRASHES)
    # =====================================================

    async def _worker(self):

        while self.running:

            try:

                chat_id, message = await self.queue.get()

                await self._send_raw(chat_id, message)

                await asyncio.sleep(0.2)  # soft rate limit buffer

            except asyncio.CancelledError:
                break

            except Exception as e:
                print(f"Telegram worker error: {e}")

    # =====================================================
    # RAW SEND (ACTUAL API CALL)
    # =====================================================

    async def _send_raw(self, chat_id: str, message: str):

        if not self.session:
            return False

        try:

            payload = {
                "chat_id": chat_id,
                "text": message,
                "parse_mode": "HTML"
            }

            async with self.session.post(
                f"{self.base_url}/sendMessage",
                data=payload,
                timeout=aiohttp.ClientTimeout(total=10)
            ) as resp:

                if resp.status != 200:
                    text = await resp.text()
                    print(f"Telegram API error: {resp.status} {text}")
                    return False

                return True

        except asyncio.TimeoutError:
            print("Telegram timeout")
            return False

        except Exception as e:
            print(f"Telegram send error: {e}")
            return False

    # =====================================================
    # HEALTH CHECK
    # =====================================================

    async def is_alive(self):

        if not self.session:
            return False

        try:

            async with self.session.get(
                f"{self.base_url}/getMe",
                timeout=aiohttp.ClientTimeout(total=5)
            ) as resp:

                return resp.status == 200

        except:
            return False
