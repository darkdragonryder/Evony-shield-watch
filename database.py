"""
=========================================================
 Evony Shield Watch
 Database Layer (Async SQLite Core System)
=========================================================
"""

# =========================================================
# IMPORTS
# =========================================================

import aiosqlite
from datetime import datetime
from config import Config


# =========================================================
# DATABASE CORE
# =========================================================

class Database:

    def __init__(self):
        self.path = Config.DB_PATH


    # =====================================================
    # INITIALISATION
    # =====================================================

    async def init(self):

        async with aiosqlite.connect(self.path) as db:

            # USERS TABLE
            await db.execute("""
            CREATE TABLE IF NOT EXISTS users (
                discord_id INTEGER PRIMARY KEY,
                telegram_id TEXT,
                telegram_username TEXT,
                role TEXT DEFAULT 'member',
                created_at TEXT
            )
            """)

            # TELEGRAM TOKENS TABLE
            await db.execute("""
            CREATE TABLE IF NOT EXISTS telegram_tokens (
                discord_id INTEGER,
                token TEXT,
                expiry TEXT
            )
            """)

            await db.commit()


    # =====================================================
    # USER MANAGEMENT
    # =====================================================

    async def set_member_contact(self, discord_id, telegram_id=None, telegram_username=None):

        async with aiosqlite.connect(self.path) as db:

            await db.execute("""
            INSERT OR IGNORE INTO users (discord_id, created_at)
            VALUES (?, ?)
            """, (discord_id, datetime.utcnow().isoformat()))

            await db.execute("""
            UPDATE users
            SET telegram_id = COALESCE(?, telegram_id),
                telegram_username = COALESCE(?, telegram_username)
            WHERE discord_id = ?
            """, (telegram_id, telegram_username, discord_id))

            await db.commit()


    async def delete_user_data(self, discord_id):

        async with aiosqlite.connect(self.path) as db:
            await db.execute("DELETE FROM users WHERE discord_id = ?", (discord_id,))
            await db.commit()


    async def get_member_contact(self, discord_id):

        async with aiosqlite.connect(self.path) as db:

            cur = await db.execute("""
            SELECT discord_id, telegram_id, telegram_username, role
            FROM users WHERE discord_id = ?
            """, (discord_id,))

            row = await cur.fetchone()

            if not row:
                return None

            return {
                "discord_id": row[0],
                "telegram_id": row[1],
                "telegram_username": row[2],
                "role": row[3]
            }


    # =====================================================
    # TELEGRAM LINK SYSTEM
    # =====================================================

    async def create_telegram_link_token(self, discord_id, token, expiry):

        async with aiosqlite.connect(self.path) as db:

            await db.execute("""
            INSERT INTO telegram_tokens (discord_id, token, expiry)
            VALUES (?, ?, ?)
            """, (discord_id, token, expiry.isoformat()))

            await db.commit()


    async def link_telegram_user(self, token, telegram_id, username):

        async with aiosqlite.connect(self.path) as db:

            cur = await db.execute("""
            SELECT discord_id FROM telegram_tokens
            WHERE token = ?
            """, (token,))

            row = await cur.fetchone()

            if not row:
                return False

            discord_id = row[0]

            await db.execute("""
            UPDATE users
            SET telegram_id = ?, telegram_username = ?
            WHERE discord_id = ?
            """, (telegram_id, username, discord_id))

            await db.execute("""
            DELETE FROM telegram_tokens WHERE token = ?
            """, (token,))

            await db.commit()

            return True


# =========================================================
# GLOBAL DB INSTANCE
# =========================================================

db = Database()
