"""
=========================================================
 Evony Shield Watch
 DATABASE CORE (HARDENED + CONSISTENT)
 - Single schema authority
 - Safe init on startup
 - No silent column mismatches
=========================================================
"""

import aiosqlite
from config import Config


# =========================================================
# DB CORE CLASS
# =========================================================

class Database:

    def __init__(self):
        self.db_path = Config.DB_PATH
        self.db = None

    # =====================================================
    # INIT
    # =====================================================

    async def init(self):

        self.db = await aiosqlite.connect(self.db_path)
        await self.db.execute("PRAGMA journal_mode=WAL;")

        await self._create_tables()
        await self.db.commit()

    # =====================================================
    # TABLES (SINGLE SOURCE OF TRUTH)
    # =====================================================

    async def _create_tables(self):

        # -----------------------------
        # MEMBERS
        # -----------------------------
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

        # -----------------------------
        # SERVER CONFIG
        # -----------------------------
        await self.db.execute("""
        CREATE TABLE IF NOT EXISTS server_config (
            guild_id INTEGER PRIMARY KEY,
            bubble_channel_id INTEGER,
            battlefield_channel_id INTEGER,
            setup_complete INTEGER DEFAULT 0,
            event_coordinator_role_id INTEGER
        )
        """)

        # -----------------------------
        # EVENT SCHEDULE
        # -----------------------------
        await self.db.execute("""
        CREATE TABLE IF NOT EXISTS event_schedule (
            guild_id INTEGER PRIMARY KEY,
            current_event TEXT DEFAULT 'svs',
            next_event_date TEXT
        )
        """)

        # -----------------------------
        # CUSTOM EVENTS
        # -----------------------------
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

        # -----------------------------
        # TELEGRAM LINKS
        # -----------------------------
        await self.db.execute("""
        CREATE TABLE IF NOT EXISTS telegram_links (
            token TEXT PRIMARY KEY,
            discord_id INTEGER,
            guild_id INTEGER,
            expiry TEXT
        )
        """)

    # =========================================================
    # MEMBER SAFE UPSERT (NO DRIFT)
    # =========================================================

    async def set_member_contact(self, discord_id: int, **kwargs):

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
        DO UPDATE SET {", ".join(fields) if fields else "discord_id = discord_id"}
        """, values)

        await self.db.commit()

    # =========================================================
    # GET MEMBER
    # =========================================================

    async def get_member_contact(self, discord_id: int):

        cursor = await self.db.execute("""
        SELECT * FROM members WHERE discord_id = ?
        """, (discord_id,))

        row = await cursor.fetchone()

        if not row:
            return None

        cols = [c[0] for c in cursor.description]

        return dict(zip(cols, row))

    # =========================================================
    # SERVER CONFIG
    # =========================================================

    async def set_server_config(self, guild_id: int, **kwargs):

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
        DO UPDATE SET {", ".join(fields) if fields else "guild_id = guild_id"}
        """, values)

        await self.db.commit()

    # =========================================================
    # EVENT SCHEDULE
    # =========================================================

    async def set_event_schedule(self, guild_id: int, **kwargs):

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
        DO UPDATE SET {", ".join(fields) if fields else "guild_id = guild_id"}
        """, values)

        await self.db.commit()

    # =========================================================
    # CUSTOM EVENTS (MINIMAL HELPERS)
    # =========================================================

    async def create_custom_event(self, **data):

        cursor = await self.db.execute("""
        INSERT INTO custom_events (
            guild_id, name, event_type, start_time,
            end_time, coordinator_id, checkin_cutoff,
            channel_id
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            data["guild_id"],
            data["name"],
            data["event_type"],
            data["start_time"],
            data["end_time"],
            data["coordinator_id"],
            data["checkin_cutoff"],
            data["channel_id"]
        ))

        await self.db.commit()
        return cursor.lastrowid

    async def get_custom_event(self, event_id: int):

        cursor = await self.db.execute("""
        SELECT * FROM custom_events WHERE event_id = ?
        """, (event_id,))

        row = await cursor.fetchone()

        if not row:
            return None

        cols = [c[0] for c in cursor.description]
        return dict(zip(cols, row))
