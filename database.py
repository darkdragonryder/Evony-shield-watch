"""
=========================================================
 Evony Shield Watch
 Database Layer (FULL FIXED DROP-IN)
=========================================================
"""

import aiosqlite
from datetime import datetime


DB_PATH = "shield.db"


class Database:

    # =====================================================
    # INIT
    # =====================================================

    async def connect(self):
        self.db = await aiosqlite.connect(DB_PATH)
        await self.create_tables()

    # =====================================================
    # TABLES
    # =====================================================

    async def create_tables(self):

        await self.db.executescript("""
        CREATE TABLE IF NOT EXISTS members (
            discord_id INTEGER PRIMARY KEY,
            telegram_id TEXT,
            telegram_username TEXT,
            role TEXT DEFAULT 'member'
            timezone TEXT,
            created_at TEXT
        );

        CREATE TABLE IF NOT EXISTS telegram_tokens (
            token TEXT PRIMARY KEY,
            discord_id INTEGER,
            expires_at TEXT
        );
        """)

        await self.db.commit()

    # =====================================================
    # MEMBER CORE
    # =====================================================

    async def set_member_contact(self, discord_id, telegram_id=None, telegram_username=None):

        await self.db.execute("""
        INSERT OR IGNORE INTO members (discord_id, created_at)
        VALUES (?, ?)
        """, (discord_id, datetime.utcnow().isoformat()))

        await self.db.execute("""
        UPDATE members
        SET telegram_id = ?, telegram_username = ?
        WHERE discord_id = ?
        """, (telegram_id, telegram_username, discord_id))

        await self.db.commit()

    async def get_member_contact(self, discord_id):

        cursor = await self.db.execute("""
        SELECT discord_id, telegram_id, telegram_username, timezone
        FROM members
        WHERE discord_id = ?
        """, (discord_id,))

        row = await cursor.fetchone()

        if not row:
            return None

        return {
            "discord_id": row[0],
            "telegram_id": row[1],
            "telegram_username": row[2],
            "timezone": row[3]
        }

    async def delete_user_data(self, discord_id):

        await self.db.execute("""
        DELETE FROM members WHERE discord_id = ?
        """, (discord_id,))

        await self.db.execute("""
        DELETE FROM telegram_tokens WHERE discord_id = ?
        """, (discord_id,))

        await self.db.commit()

    # =====================================================
    # TELEGRAM TOKENS
    # =====================================================

    async def create_telegram_link_token(self, discord_id, token, expiry):

        await self.db.execute("""
        INSERT INTO telegram_tokens (token, discord_id, expires_at)
        VALUES (?, ?, ?)
        """, (token, discord_id, expiry.isoformat()))

        await self.db.commit()

    async def get_telegram_token(self, token):

        cursor = await self.db.execute("""
        SELECT token, discord_id, expires_at
        FROM telegram_tokens
        WHERE token = ?
        """, (token,))

        row = await cursor.fetchone()

        if not row:
            return None

        return {
            "token": row[0],
            "discord_id": row[1],
            "expires_at": datetime.fromisoformat(row[2])
        }

    async def link_telegram_user(self, token, telegram_id, username, discord_id):

        await self.set_member_contact(discord_id, telegram_id, username)

        await self.db.execute("""
        DELETE FROM telegram_tokens WHERE token = ?
        """, (token,))

        await self.db.commit()


# =========================================================
# GLOBAL INSTANCE
# =========================================================

db = Database()
