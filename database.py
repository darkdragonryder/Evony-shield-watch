"""
=========================================================
Evony Shield Watch
Database Layer (STABLE - FIXED SCHEDULING CORE)
=========================================================
"""

import aiosqlite

DB_PATH = "evony_bot.db"


class Database:

    def __init__(self):
        self.db_path = DB_PATH

    # =====================================================
    # INIT
    # =====================================================

    async def init(self):

        async with aiosqlite.connect(self.db_path) as db:

            # MEMBERS
            await db.execute("""
                CREATE TABLE IF NOT EXISTS members (
                    user_id INTEGER PRIMARY KEY,
                    timezone TEXT,
                    opt_in INTEGER DEFAULT 1,
                    telegram_id TEXT,
                    telegram_username TEXT
                )
            """)

            # TELEGRAM LINKS
            await db.execute("""
                CREATE TABLE IF NOT EXISTS telegram_links (
                    user_id INTEGER,
                    token TEXT UNIQUE,
                    expiry TEXT
                )
            """)

            # SERVER CONFIG
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

            # =========================
            # FIX: EVENT SCHEDULE TABLE
            # =========================
            await db.execute("""
                CREATE TABLE IF NOT EXISTS event_schedule (
                    guild_id INTEGER PRIMARY KEY,
                    current_event TEXT,
                    next_event_date TEXT
                )
            """)

            # EVENT LOG (reminder spam control)
            await db.execute("""
                CREATE TABLE IF NOT EXISTS event_log (
                    guild_id INTEGER,
                    event_type TEXT,
                    reminder_type TEXT,
                    day TEXT,
                    PRIMARY KEY (guild_id, event_type, reminder_type, day)
                )
            """)

            # BUBBLE LOG
            await db.execute("""
                CREATE TABLE IF NOT EXISTS bubble_log (
                    guild_id INTEGER,
                    user_id INTEGER,
                    event_type TEXT,
                    day TEXT,
                    PRIMARY KEY (guild_id, user_id, event_type, day)
                )
            """)

            # ROLES
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
                FROM members
                WHERE user_id = ?
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

            await db.execute("""
                INSERT OR IGNORE INTO servers (guild_id)
                VALUES (?)
            """, (guild_id,))

            allowed = {
                "current_event",
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
                FROM servers
                WHERE guild_id=?
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
    # FIXED EVENT SCHEDULING (REAL STORAGE)
    # =====================================================

    async def set_event_schedule(self, guild_id, current_event=None, next_event_date=None):

        async with aiosqlite.connect(self.db_path) as db:

            await db.execute("""
                INSERT OR REPLACE INTO event_schedule
                (guild_id, current_event, next_event_date)
                VALUES (?, ?, ?)
            """, (
                guild_id,
                current_event,
                next_event_date.isoformat() if next_event_date else None
            ))

            await db.commit()

    async def get_event_schedule(self, guild_id):

        async with aiosqlite.connect(self.db_path) as db:

            cursor = await db.execute("""
                SELECT guild_id, current_event, next_event_date
                FROM event_schedule
                WHERE guild_id=?
            """, (guild_id,))

            row = await cursor.fetchone()

            if not row:
                return None

            return {
                "guild_id": row[0],
                "current_event": row[1],
                "next_event_date": row[2]
            }

    async def rotate_event(self, guild_id):

        schedule = await self.get_event_schedule(guild_id)

        current = schedule["current_event"] if schedule else "svs"
        new_event = "ke" if current == "svs" else "svs"

        await self.set_event_schedule(
            guild_id,
            current_event=new_event,
            next_event_date=None
        )

        return new_event

    # =====================================================
    # REMINDER LOGGING (UNCHANGED BUT SAFE)
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

    # =====================================================
    # BUBBLE TRACKING
    # =====================================================

    async def track_bubble_reminder(self, guild_id, user_id, event_type):

        async with aiosqlite.connect(self.db_path) as db:

            await db.execute("""
                INSERT OR REPLACE INTO bubble_log
                (guild_id, user_id, event_type, day)
                VALUES (?, ?, ?, date('now'))
            """, (guild_id, user_id, event_type))

            await db.commit()

    async def has_bubble_reminder_today(self, guild_id, user_id, event_type):

        async with aiosqlite.connect(self.db_path) as db:

            cursor = await db.execute("""
                SELECT 1 FROM bubble_log
                WHERE guild_id=? AND user_id=? AND event_type=? AND day=date('now')
            """, (guild_id, user_id, event_type))

            return await cursor.fetchone() is not None

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
                SELECT role FROM roles WHERE user_id=?
            """, (user_id,))

            row = await cursor.fetchone()

            return row[0] if row else "member"


db = Database()
