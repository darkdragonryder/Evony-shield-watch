"""
=========================================================
 Evony Shield Watch
 Database Layer (UPDATED - Telegram + Roles + Cleanup)
=========================================================
"""

import aiosqlite
from datetime import datetime

DB_PATH = "evony_bot.db"


class Database:

    def __init__(self):
        self.db_path = DB_PATH

    # =====================================================
    # INIT DATABASE
    # =====================================================

    async def init(self):
        async with aiosqlite.connect(self.db_path) as db:

            # -----------------------------
            # MEMBERS TABLE
            # -----------------------------
            await db.execute("""
                CREATE TABLE IF NOT EXISTS members (
                    user_id INTEGER PRIMARY KEY,
                    timezone TEXT,
                    opt_in INTEGER DEFAULT 1,
                    telegram_id TEXT,
                    telegram_username TEXT
                )
            """)

            # -----------------------------
            # TELEGRAM TOKENS
            # -----------------------------
            await db.execute("""
                CREATE TABLE IF NOT EXISTS telegram_links (
                    user_id INTEGER,
                    token TEXT,
                    expiry TEXT
                )
            """)

            # -----------------------------
            # SERVER CONFIG
            # -----------------------------
            await db.execute("""
                CREATE TABLE IF NOT EXISTS servers (
                    guild_id INTEGER PRIMARY KEY,
                    current_event TEXT
                )
            """)

            # -----------------------------
            # ROLE SYSTEM (WEB DASHBOARD)
            # -----------------------------
            await db.execute("""
                CREATE TABLE IF NOT EXISTS roles (
                    user_id INTEGER,
                    role TEXT
                )
            """)

            await db.commit()

    # =====================================================
    # MEMBER SYSTEM
    # =====================================================

    async def set_member_contact(self, user_id, **kwargs):
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute("""
                INSERT OR IGNORE INTO members (user_id)
                VALUES (?)
            """, (user_id,))

            for key, value in kwargs.items():
                await db.execute(f"""
                    UPDATE members
                    SET {key} = ?
                    WHERE user_id = ?
                """, (value, user_id))

            await db.commit()

    async def delete_user_data(self, user_id):
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute("DELETE FROM members WHERE user_id=?", (user_id,))
            await db.execute("DELETE FROM roles WHERE user_id=?", (user_id,))
            await db.commit()

    # =====================================================
    # TELEGRAM SYSTEM
    # =====================================================

    async def create_telegram_link_token(self, user_id, token, expiry):
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute("""
                INSERT INTO telegram_links (user_id, token, expiry)
                VALUES (?, ?, ?)
            """, (user_id, token, expiry.isoformat()))
            await db.commit()

    async def link_telegram_user(self, token, telegram_id, username):
        async with aiosqlite.connect(self.db_path) as db:

            cursor = await db.execute("""
                SELECT user_id FROM telegram_links
                WHERE token = ?
            """, (token,))

            row = await cursor.fetchone()

            if not row:
                return False

            user_id = row[0]

            await db.execute("""
                UPDATE members
                SET telegram_id = ?, telegram_username = ?
                WHERE user_id = ?
            """, (telegram_id, username, user_id))

            await db.execute("""
                DELETE FROM telegram_links WHERE token = ?
            """, (token,))

            await db.commit()

            return True

    # =====================================================
    # SERVER CONFIG
    # =====================================================

    async def set_server_config(self, guild_id, current_event=None):
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute("""
                INSERT OR IGNORE INTO servers (guild_id, current_event)
                VALUES (?, ?)
            """, (guild_id, current_event))
            await db.commit()

    # =====================================================
    # ROLE SYSTEM (WEB DASHBOARD)
    # =====================================================

    async def set_role(self, user_id, role):
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute("""
                INSERT INTO roles (user_id, role)
                VALUES (?, ?)
            """, (user_id, role))
            await db.commit()

    async def get_role(self, user_id):
        async with aiosqlite.connect(self.db_path) as db:
            cursor = await db.execute("""
                SELECT role FROM roles WHERE user_id=?
            """, (user_id,))
            row = await cursor.fetchone()
            return row[0] if row else "member"


db = Database()
