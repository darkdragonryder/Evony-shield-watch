"""
=========================================================
 Evony Shield Watch
 Database Layer (STABLE - Telegram + Setup + Roles)
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
                    token TEXT UNIQUE,
                    expiry TEXT
                )
            """)

            # -----------------------------
            # SERVER CONFIG (EXPANDED FOR SETUP FLOW)
            # -----------------------------
            await db.execute("""
                CREATE TABLE IF NOT EXISTS servers (
                    guild_id INTEGER PRIMARY KEY,

                    current_event TEXT,

                    bubble_channel_id INTEGER,
                    battlefield_channel_id INTEGER,

                    event_coordinator_role_id INTEGER,

                    setup_complete INTEGER DEFAULT 0
                )
            """)

            # -----------------------------
            # ROLES SYSTEM
            # -----------------------------
            await db.execute("""
                CREATE TABLE IF NOT EXISTS roles (
                    user_id INTEGER PRIMARY KEY,
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

            # SAFE UPDATE (prevents SQL injection via key)
            allowed_fields = {
                "timezone",
                "opt_in",
                "telegram_id",
                "telegram_username"
            }

            for key, value in kwargs.items():

                if key not in allowed_fields:
                    continue

                await db.execute(f"""
                    UPDATE members
                    SET {key} = ?
                    WHERE user_id = ?
                """, (value, user_id))

            await db.commit()

    async def delete_member_data(self, user_id):

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
                DELETE FROM telegram_links
                WHERE token = ?
            """, (token,))

            await db.commit()

            return True

    # =====================================================
    # SERVER CONFIG
    # =====================================================

    async def set_server_config(self, guild_id, **kwargs):

        async with aiosqlite.connect(self.db_path) as db:

            await db.execute("""
                INSERT OR IGNORE INTO servers (guild_id)
                VALUES (?)
            """, (guild_id,))

            allowed_fields = {
                "current_event",
                "bubble_channel_id",
                "battlefield_channel_id",
                "event_coordinator_role_id",
                "setup_complete"
            }

            for key, value in kwargs.items():

                if key not in allowed_fields:
                    continue

                await db.execute(f"""
                    UPDATE servers
                    SET {key} = ?
                    WHERE guild_id = ?
                """, (value, guild_id))

            await db.commit()

    async def get_server_config(self, guild_id):

        async with aiosqlite.connect(self.db_path) as db:

            cursor = await db.execute("""
                SELECT *
                FROM servers
                WHERE guild_id = ?
            """, (guild_id,))

            row = await cursor.fetchone()

            if not row:
                return None

            return {
                "guild_id": row[0],
                "current_event": row[1],
                "bubble_channel_id": row[2],
                "battlefield_channel_id": row[3],
                "event_coordinator_role_id": row[4],
                "setup_complete": row[5],
            }

    # =====================================================
    # ROLE SYSTEM
    # =====================================================

    async def set_role(self, user_id, role):

        async with aiosqlite.connect(self.db_path) as db:

            await db.execute("""
                INSERT OR REPLACE INTO roles (user_id, role)
                VALUES (?, ?)
            """, (user_id, role))

            await db.commit()

    async def get_role(self, user_id):

        async with aiosqlite.connect(self.db_path) as db:

            cursor = await db.execute("""
                SELECT role
                FROM roles
                WHERE user_id = ?
            """, (user_id,))

            row = await cursor.fetchone()

            return row[0] if row else "member"


# =========================================================
# SINGLETON
# =========================================================

db = Database()
