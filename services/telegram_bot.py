"""
=========================================================
Telegram Service (HARDENED + SAFE START/STOP)
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
        self.lock = asyncio.Lock()

    async def start_async(self):

        async with self.lock:

            if self.running:
                return

            self.session = aiohttp.ClientSession()
            self.running = True

            print("📲 Telegram service started")

    async def stop_async(self):

        async with self.lock:

            self.running = False

            if self.session:
                await self.session.close()

            self.session = None

    def is_ready(self):
        return self.running and self.session

    async def send_message(self, chat_id, text, title="Alert"):

        if not self.is_ready():
            return False

        url = f"https://api.telegram.org/bot{Config.TELEGRAM_BOT_TOKEN}/sendMessage"

        payload = {
            "chat_id": chat_id,
            "text": f"🛡️ {title}\n\n{text}"
        }

        for attempt in range(3):

            try:
                async with self.session.post(url, data=payload) as r:
                    if r.status == 200:
                        return True

            except Exception as e:
                logging.error(e)

            await asyncio.sleep(2)

        return False
