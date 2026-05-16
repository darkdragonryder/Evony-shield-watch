"""
Evony Shield Watch
DATABASE CORE (STABLE CONTRACT VERSION)
"""

import aiosqlite
from config import Config


class Database:

    def __init__(self):
        self.db_path = Config.DB_PATH
        self.db = None

    # =====================================================
    # INIT
    # =====================================================

    async def init(self):

        if self.db is not None:
            return

        self.db = await aiosqlite.connect(self.db_path)
        self.db.row_factory = aiosqlite.Row

        await self.db.execute("PRAGMA journal_mode=WAL;")

        await self._create_tables()
        await self.db.commit()

    # =====================================================
    # INTERNAL GUARD
    # =====================================================

    def _require_db(self):

        if self.db is None:
            raise RuntimeError("Database not initialized. Call db.init() first.")

    # =====================================================
    # TABLES
    # =====================================================

    async def _create_tables(self):

        await self.db.execute("""
        CREATE TABLE IF NOT EXISTS members (
            discord_id INTEGER PRIMARY KEY,
            telegram_id TEXT,
            telegram_username TEXT,
            role TEXT DEFAULT 'member',
            opt_in INTEGER DEFAULT 1,
            timezone TEXT DEFAULT 'UTC'
        )
        """)

        await self.db.execute("""
        CREATE TABLE IF NOT EXISTS server_config (
            guild_id INTEGER PRIMARY KEY,
            bubble_channel_id INTEGER,
            battlefield_channel_id INTEGER,
            setup_complete INTEGER DEFAULT 0,
            event_coordinator_role_id INTEGER
        )
        """)

        await self.db.execute("""
        CREATE TABLE IF NOT EXISTS event_schedule (
            guild_id INTEGER PRIMARY KEY,
            current_event TEXT DEFAULT 'svs',
            next_event_date TEXT
        )
        """)

        await self.db.execute("""
        CREATE TABLE IF NOT EXISTS custom_events (
            event_id INTEGER PRIMARY KEY AUTOINCREMENT,
            guild_id INTEGER,
            name TEXT,
            event_type TEXT,
            start_time TEXT,
            end_time TEXT,
            coordinator_id INTEGER,
            checkin_cutoff TEXT,
            channel_id INTEGER,
            message_id INTEGER
        )
        """)

        await self.db.execute("""
        CREATE TABLE IF NOT EXISTS telegram_links (
            token TEXT PRIMARY KEY,
            discord_id INTEGER,
            guild_id INTEGER,
            expiry TEXT
        )
        """)

    # =====================================================
    # EVENT SCHEDULE (READ)
    # =====================================================

    async def get_event_schedule(self, guild_id: int):

        self._require_db()

        cursor = await self.db.execute("""
            SELECT * FROM event_schedule WHERE guild_id = ?
        """, (guild_id,))

        row = await cursor.fetchone()

        if not row:
            return None

        return dict(row)

    # =====================================================
    # EVENT SCHEDULE (WRITE)
    # =====================================================

    async def set_event_schedule(self, guild_id: int, **kwargs):

        self._require_db()

        if not kwargs:
            await self.db.execute("""
                INSERT OR IGNORE INTO event_schedule (guild_id)
                VALUES (?)
            """, (guild_id,))
            await self.db.commit()
            return

        fields = []
        values = []

        for k, v in kwargs.items():
            fields.append(f"{k} = ?")
            values.append(v)

        values.append(guild_id)

        await self.db.execute(f"""
            INSERT INTO event_schedule (guild_id)
            VALUES (?)
            ON CONFLICT(guild_id)
            DO UPDATE SET {", ".join(fields)}
        """, values)

        await self.db.commit()

    # =====================================================
    # MEMBER
    # =====================================================

    async def set_member_contact(self, discord_id: int, **kwargs):

        self._require_db()

        if not kwargs:
            await self.db.execute("""
                INSERT OR IGNORE INTO members (discord_id)
                VALUES (?)
            """, (discord_id,))
            await self.db.commit()
            return

        fields = []
        values = []

        for k, v in kwargs.items():
            fields.append(f"{k} = ?")
            values.append(v)

        values.append(discord_id)

        await self.db.execute(f"""
            INSERT INTO members (discord_id)
            VALUES (?)
            ON CONFLICT(discord_id)
            DO UPDATE SET {", ".join(fields)}
        """, values)

        await self.db.commit()

    async def get_member_contact(self, discord_id: int):

        self._require_db()

        cursor = await self.db.execute("""
            SELECT * FROM members WHERE discord_id = ?
        """, (discord_id,))

        row = await cursor.fetchone()

        if not row:
            return None

        return dict(row)

    # =====================================================
    # SERVER CONFIG
    # =====================================================

    async def set_server_config(self, guild_id: int, **kwargs):

        self._require_db()

        if not kwargs:
            await self.db.execute("""
                INSERT OR IGNORE INTO server_config (guild_id)
                VALUES (?)
            """, (guild_id,))
            await self.db.commit()
            return

        fields = []
        values = []

        for k, v in kwargs.items():
            fields.append(f"{k} = ?")
            values.append(v)

        values.append(guild_id)

        await self.db.execute(f"""
            INSERT INTO server_config (guild_id)
            VALUES (?)
            ON CONFLICT(guild_id)
            DO UPDATE SET {", ".join(fields)}
        """, values)

        await self.db.commit()
