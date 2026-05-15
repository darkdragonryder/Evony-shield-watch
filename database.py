"""
=========================================================
 Evony Shield Watch
 SQLite Database Layer (Discord + Telegram Support)
=========================================================
"""

# =========================================================
# IMPORTS
# =========================================================

import aiosqlite
from datetime import datetime
from typing import Optional, List, Dict, Any

from config import Config


# =========================================================
# DATABASE CORE
# =========================================================

class Database:

    def __init__(self, db_path: str = "evony_bot.db"):
        self.db_path = db_path

    # =====================================================
    # INIT DATABASE
    # =====================================================

    async def init(self):

        async with aiosqlite.connect(self.db_path) as db:

            # -------------------------------------------------
            # SERVER CONFIG
            # -------------------------------------------------

            await db.execute("""
                CREATE TABLE IF NOT EXISTS server_config (
                    guild_id INTEGER PRIMARY KEY,
                    bubble_channel_id INTEGER,
                    battlefield_channel_id INTEGER,
                    event_coordinator_role_id INTEGER,
                    current_event TEXT DEFAULT 'svs',
                    setup_complete INTEGER DEFAULT 0
                )
            """)

            # -------------------------------------------------
            # EVENT SCHEDULE
            # -------------------------------------------------

            await db.execute("""
                CREATE TABLE IF NOT EXISTS event_schedule (
                    guild_id INTEGER PRIMARY KEY,
                    current_event TEXT DEFAULT 'svs',
                    last_event_end DATE,
                    next_event_date DATE
                )
            """)

            # -------------------------------------------------
            # CUSTOM EVENTS
            # -------------------------------------------------

            await db.execute("""
                CREATE TABLE IF NOT EXISTS custom_events (
                    event_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    guild_id INTEGER,
                    event_type TEXT,
                    name TEXT,
                    start_time TIMESTAMP,
                    end_time TIMESTAMP,
                    coordinator_id INTEGER,
                    checkin_cutoff TIMESTAMP,
                    channel_id INTEGER,
                    message_id INTEGER,
                    status TEXT DEFAULT 'active',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)

            # -------------------------------------------------
            # EVENT CHECKINS
            # -------------------------------------------------

            await db.execute("""
                CREATE TABLE IF NOT EXISTS event_checkins (
                    checkin_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    event_id INTEGER,
                    user_id INTEGER,
                    status TEXT,
                    checked_at TIMESTAMP
                )
            """)

            # -------------------------------------------------
            # MEMBER CONTACTS (DISCORD + TELEGRAM)
            # -------------------------------------------------

            await db.execute("""
                CREATE TABLE IF NOT EXISTS member_contacts (
                    user_id INTEGER PRIMARY KEY,

                    # Discord settings
                    discord_opt_in INTEGER DEFAULT 1,

                    # Telegram integration
                    telegram_id TEXT UNIQUE,
                    telegram_username TEXT,
                    telegram_link_token TEXT,
                    telegram_link_expiry TIMESTAMP,

                    # Optional extras
                    timezone TEXT DEFAULT 'UTC'
                )
            """)

            # -------------------------------------------------
            # REMINDER LOGS
            # -------------------------------------------------

            await db.execute("""
                CREATE TABLE IF NOT EXISTS reminder_logs (
                    log_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    guild_id INTEGER,
                    event_type TEXT,
                    reminder_type TEXT,
                    sent_at TIMESTAMP
                )
            """)

            # -------------------------------------------------
            # BUBBLE TRACKING
            # -------------------------------------------------

            await db.execute("""
                CREATE TABLE IF NOT EXISTS bubble_tracking (
                    track_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    guild_id INTEGER,
                    user_id INTEGER,
                    event_type TEXT,
                    event_date DATE,
                    reminded_at TIMESTAMP
                )
            """)

            await db.commit()

    # =====================================================
    # SERVER CONFIG
    # =====================================================

    async def get_server_config(self, guild_id: int):

        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row

            async with db.execute(
                "SELECT * FROM server_config WHERE guild_id = ?",
                (guild_id,)
            ) as cur:
                row = await cur.fetchone()
                return dict(row) if row else None

    async def set_server_config(self, guild_id: int, **kwargs):

        async with aiosqlite.connect(self.db_path) as db:

            exists = await db.execute_fetchone(
                "SELECT guild_id FROM server_config WHERE guild_id = ?",
                (guild_id,)
            )

            if exists:

                set_clause = ", ".join([f"{k} = ?" for k in kwargs])
                values = list(kwargs.values()) + [guild_id]

                await db.execute(
                    f"UPDATE server_config SET {set_clause} WHERE guild_id = ?",
                    values
                )

            else:

                cols = ["guild_id"] + list(kwargs.keys())
                vals = [guild_id] + list(kwargs.values())

                placeholders = ",".join(["?"] * len(vals))

                await db.execute(
                    f"""
                    INSERT INTO server_config ({','.join(cols)})
                    VALUES ({placeholders})
                    """,
                    vals
                )

            await db.commit()

    # =====================================================
    # EVENT SCHEDULE
    # =====================================================

    async def get_event_schedule(self, guild_id: int):

        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row

            async with db.execute(
                "SELECT * FROM event_schedule WHERE guild_id = ?",
                (guild_id,)
            ) as cur:
                row = await cur.fetchone()
                return dict(row) if row else None

    async def set_event_schedule(self, guild_id: int, **kwargs):

        async with aiosqlite.connect(self.db_path) as db:

            exists = await db.execute_fetchone(
                "SELECT guild_id FROM event_schedule WHERE guild_id = ?",
                (guild_id,)
            )

            if exists:

                set_clause = ", ".join([f"{k} = ?" for k in kwargs])
                values = list(kwargs.values()) + [guild_id]

                await db.execute(
                    f"UPDATE event_schedule SET {set_clause} WHERE guild_id = ?",
                    values
                )

            else:

                cols = ["guild_id"] + list(kwargs.keys())
                vals = [guild_id] + list(kwargs.values())

                placeholders = ",".join(["?"] * len(vals))

                await db.execute(
                    f"""
                    INSERT INTO event_schedule ({','.join(cols)})
                    VALUES ({placeholders})
                    """,
                    vals
                )

            await db.commit()

    # =====================================================
    # MEMBER CONTACTS (DISCORD + TELEGRAM)
    # =====================================================

    async def get_member_contact(self, user_id: int):

        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row

            async with db.execute(
                "SELECT * FROM member_contacts WHERE user_id = ?",
                (user_id,)
            ) as cur:
                row = await cur.fetchone()
                return dict(row) if row else None

    async def set_member_contact(self, user_id: int, **kwargs):

        async with aiosqlite.connect(self.db_path) as db:

            existing = await self.get_member_contact(user_id)

            if existing:

                set_clause = ", ".join([f"{k} = ?" for k in kwargs])
                values = list(kwargs.values()) + [user_id]

                await db.execute(
                    f"UPDATE member_contacts SET {set_clause} WHERE user_id = ?",
                    values
                )

            else:

                cols = ["user_id"] + list(kwargs.keys())
                vals = [user_id] + list(kwargs.values())

                placeholders = ",".join(["?"] * len(vals))

                await db.execute(
                    f"""
                    INSERT INTO member_contacts ({','.join(cols)})
                    VALUES ({placeholders})
                    """,
                    vals
                )

            await db.commit()

    # =====================================================
    # TELEGRAM LINKING SYSTEM
    # =====================================================

    async def create_telegram_link_token(self, user_id: int, token: str, expiry: datetime):

        await self.set_member_contact(
            user_id,
            telegram_link_token=token,
            telegram_link_expiry=expiry
        )

    async def link_telegram_user(self, token: str, telegram_id: str, username: str):

        async with aiosqlite.connect(self.db_path) as db:

            await db.execute("""
                UPDATE member_contacts
                SET telegram_id = ?,
                    telegram_username = ?,
                    telegram_link_token = NULL,
                    telegram_link_expiry = NULL
                WHERE telegram_link_token = ?
                AND telegram_link_expiry > datetime('now')
            """, (telegram_id, username, token))

            await db.commit()

    async def get_user_by_telegram(self, telegram_id: str):

        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row

            async with db.execute(
                "SELECT * FROM member_contacts WHERE telegram_id = ?",
                (telegram_id,)
            ) as cur:
                row = await cur.fetchone()
                return dict(row) if row else None

    # =====================================================
    # AUTO CLEANUP (SERVER LEAVE)
    # =====================================================

    async def delete_user_data(self, user_id: int):

        async with aiosqlite.connect(self.db_path) as db:

            await db.execute(
                "DELETE FROM member_contacts WHERE user_id = ?",
                (user_id,)
            )

            await db.execute(
                "DELETE FROM event_checkins WHERE user_id = ?",
                (user_id,)
            )

            await db.execute(
                "DELETE FROM bubble_tracking WHERE user_id = ?",
                (user_id,)
            )

            await db.commit()

    # =====================================================
    # SERVER MEMBER CLEANUP (WHEN LEAVE/KICK/BAN)
    # =====================================================

    async def purge_guild_user(self, user_id: int):

        await self.delete_user_data(user_id)

    # =====================================================
    # CHECKIN SYSTEM
    # =====================================================

    async def checkin_member(self, event_id: int, user_id: int, status: str):

        async with aiosqlite.connect(self.db_path) as db:

            await db.execute("""
                INSERT INTO event_checkins (
                    event_id,
                    user_id,
                    status,
                    checked_at
                )
                VALUES (?, ?, ?, datetime('now'))
            """, (event_id, user_id, status))

            await db.commit()
