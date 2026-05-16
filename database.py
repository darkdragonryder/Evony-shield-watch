"""
=========================================================
Evony Shield Watch
Database Layer (FINAL ARCHITECTURE FIX)
=========================================================
"""

import aiosqlite
from datetime import datetime, date

DB_PATH = "evony_bot.db"


class Database:

    def __init__(self):
        self.db_path = DB_PATH

    # =====================================================
    # INIT
    # =====================================================

    async def init(self):

        async with aiosqlite.connect(self.db_path) as db:

            # ---------------- MEMBERS ----------------
            await db.execute("""
                CREATE TABLE IF NOT EXISTS members (
                    user_id INTEGER PRIMARY KEY,
                    timezone TEXT,
                    opt_in INTEGER DEFAULT 1,
                    telegram_id TEXT,
                    telegram_username TEXT
                )
            """)

            # ---------------- TELEGRAM ----------------
            await db.execute("""
                CREATE TABLE IF NOT EXISTS telegram_links (
                    user_id INTEGER,
                    token TEXT UNIQUE,
                    expiry TEXT
                )
            """)

            # ---------------- SERVER CONFIG ----------------
            await db.execute("""
                CREATE TABLE IF NOT EXISTS servers (
                    guild_id INTEGER PRIMARY KEY,
                    bubble_channel_id INTEGER,
                    battlefield_channel_id INTEGER,
                    event_coordinator_role_id INTEGER,
                    setup_complete INTEGER DEFAULT 0
                )
            """)

            # ---------------- EVENT STATE (IMPORTANT FIX) ----------------
            await db.execute("""
                CREATE TABLE IF NOT EXISTS event_state (
                    guild_id INTEGER PRIMARY KEY,
                    active_event TEXT,
                    cycle_start_day TEXT,
                    last_rotation TEXT
                )
            """)

            # ---------------- REMINDER LOG ----------------
            await db.execute("""
                CREATE TABLE IF NOT EXISTS event_log (
                    guild_id INTEGER,
                    event_type TEXT,
                    reminder_type TEXT,
                    day TEXT,
                    PRIMARY KEY (guild_id, event_type, reminder_type, day)
                )
            """)

            # ---------------- BUBBLE LOG ----------------
            await db.execute("""
                CREATE TABLE IF NOT EXISTS bubble_log (
                    guild_id INTEGER,
                    user_id INTEGER,
                    event_type TEXT,
                    day TEXT,
                    PRIMARY KEY (guild_id, user_id, event_type, day)
                )
            """)

            # ---------------- ROLES ----------------
            await db.execute("""
                CREATE TABLE IF NOT EXISTS roles (
                    user_id INTEGER PRIMARY KEY,
                    role TEXT
                )
            """)

            await db.commit()

    # =====================================================
    # MEMBER
    # =====================================================

    async def set_member_contact(self, user_id, **kwargs):

        async with aiosqlite.connect(self.db_path) as db:

            await db.execute("INSERT OR IGNORE INTO members (user_id) VALUES (?)", (user_id,))

            allowed = {"timezone", "opt_in", "telegram_id", "telegram_username"}

            for k, v in kwargs.items():
                if k in allowed:
                    await db.execute(
                        f"UPDATE members SET {k}=? WHERE user_id=?",
                        (v, user_id)
                    )

            await db.commit()

    async def get_member_contact(self, user_id):

        async with aiosqlite.connect(self.db_path) as db:

            cursor = await db.execute("""
                SELECT user_id, timezone, opt_in, telegram_id, telegram_username
                FROM members WHERE user_id=?
            """, (user_id,))

            row = await cursor.fetchone()

            if not row:
                return None

            return {
                "user_id": row[0],
                "timezone": row[1],
                "opt_in": row[2],
                "telegram_id": row[3],
                "telegram_username": row[4],
            }

    # =====================================================
    # SERVER CONFIG
    # =====================================================

    async def set_server_config(self, guild_id, **kwargs):

        async with aiosqlite.connect(self.db_path) as db:

            await db.execute("INSERT OR IGNORE INTO servers (guild_id) VALUES (?)", (guild_id,))

            allowed = {
                "bubble_channel_id",
                "battlefield_channel_id",
                "event_coordinator_role_id",
                "setup_complete"
            }

            for k, v in kwargs.items():
                if k in allowed:
                    await db.execute(
                        f"UPDATE servers SET {k}=? WHERE guild_id=?",
                        (v, guild_id)
                    )

            await db.commit()

    async def get_server_config(self, guild_id):

        async with aiosqlite.connect(self.db_path) as db:

            cursor = await db.execute("""
                SELECT *
                FROM servers WHERE guild_id=?
            """, (guild_id,))

            row = await cursor.fetchone()

            if not row:
                return None

            return {
                "guild_id": row[0],
                "bubble_channel_id": row[1],
                "battlefield_channel_id": row[2],
                "event_coordinator_role_id": row[3],
                "setup_complete": row[4],
            }

    # =====================================================
    # EVENT STATE MACHINE (CORE FIX)
    # =====================================================

    async def get_event_schedule(self, guild_id):

        async with aiosqlite.connect(self.db_path) as db:

            cursor = await db.execute("""
                SELECT active_event, cycle_start_day, last_rotation
                FROM event_state
                WHERE guild_id=?
            """, (guild_id,))

            row = await cursor.fetchone()

            if not row:
                return None

            return {
                "current_event": row[0],
                "cycle_start_day": row[1],
                "last_rotation": row[2]
            }

    async def set_event_schedule(self, guild_id, current_event):

        today = date.today().isoformat()

        async with aiosqlite.connect(self.db_path) as db:

            await db.execute("""
                INSERT OR IGNORE INTO event_state (guild_id, active_event, cycle_start_day, last_rotation)
                VALUES (?, ?, ?, ?)
            """, (guild_id, current_event, today, today))

            await db.execute("""
                UPDATE event_state
                SET active_event=?, last_rotation=?
                WHERE guild_id=?
            """, (current_event, today, guild_id))

            await db.commit()

    async def rotate_event(self, guild_id):

        config = await self.get_event_schedule(guild_id)
        if not config:
            new_event = "svs"
        else:
            new_event = "ke" if config["current_event"] == "svs" else "svs"

        await self.set_event_schedule(guild_id, new_event)

        return new_event

    # =====================================================
    # LOGGING (UNCHANGED BUT SAFE)
    # =====================================================

    async def log_reminder(self, guild_id, event_type, reminder_type):

        async with aiosqlite.connect(self.db_path) as db:

            await db.execute("""
                INSERT OR REPLACE INTO event_log
                (guild_id, event_type, reminder_type, day)
                VALUES (?, ?, ?, date('now'))
            """, (guild_id, event_type, reminder_type))

            await db.commit()

    async def was_reminder_sent_today(self, guild_id, event_type, reminder_type):

        async with aiosqlite.connect(self.db_path) as db:

            cursor = await db.execute("""
                SELECT 1 FROM event_log
                WHERE guild_id=? AND event_type=? AND reminder_type=? AND day=date('now')
            """, (guild_id, event_type, reminder_type))

            return await cursor.fetchone() is not None


db = Database()
