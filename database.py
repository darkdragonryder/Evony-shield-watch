"""
Evony Shield Watch
DATABASE CORE (HARDENED + SAFE + CONSISTENT)
"""

import aiosqlite
from config import Config


class Database:

    def init(self):
        self.db_path = Config.DB_PATH
        self.db = None

    # =====================================================
    # INIT (SAFE GUARDED)
    # =====================================================

    async def init(self):

        if self.db is not None:
            return  # already initialized safely

        self.db = await aiosqlite.connect(self.db_path)
        self.db.row_factory = aiosqlite.Row

        await self.db.execute("PRAGMA journal_mode=WAL;")

        await self._create_tables()
        await self.db.commit()

    # =====================================================
    # SAFE EXEC GUARD
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
    # MEMBER UPSERT (SAFE)
    # =====================================================

    async def set_member_contact(self, discord_id: int, **kwargs):

        self._require_db()

        if not kwargs:
            await self.db.execute(
                "INSERT OR IGNORE INTO members (discord_id) VALUES (?)",
                (discord_id,)
            )
            await self.db.commit()
            return

        fields = []
        values = []

        for k, v in kwargs.items():
            fields.append(f"{k} = ?")
            values.append(v)

        await self.db.execute(f"""
        INSERT INTO members (discord_id)
        VALUES (?)
        ON CONFLICT(discord_id)
        DO UPDATE SET {", ".join(fields)}
        """, [discord_id] + values)

        await self.db.commit()

    # =====================================================
    # GET MEMBER
    # =====================================================

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
            await self.db.execute(
                "INSERT OR IGNORE INTO server_config (guild_id) VALUES (?)",
                (guild_id,)
            )
            await self.db.commit()
            return

        fields = []
        values = []

        for k, v in kwargs.items():
            fields.append(f"{k} = ?")
            values.append(v)

        await self.db.execute(f"""
        INSERT INTO server_config (guild_id)
        VALUES (?)
        ON CONFLICT(guild_id)
        DO UPDATE SET {", ".join(fields)}
        """, [guild_id] + values)

        await self.db.commit()

    # =====================================================
    # EVENT SCHEDULE
    # =====================================================

    async def set_event_schedule(self, guild_id: int, **kwargs):

        self._require_db()

        fields = []
        values = []

        for k, v in kwargs.items():
            fields.append(f"{k} = ?")
            values.append(v)

        await self.db.execute(f"""
        INSERT INTO event_schedule (guild_id)
        VALUES (?)
        ON CONFLICT(guild_id)
        DO UPDATE SET {", ".join(fields)}
        """, [guild_id] + values)

        await self.db.commit()

    # =====================================================
    # CUSTOM EVENTS
    # =====================================================

    async def create_custom_event(self, **data):

        self._require_db()

        columns = ", ".join(data.keys())
        placeholders = ", ".join(["?"] * len(data))
        values = list(data.values())

        cursor = await self.db.execute(f"""
        INSERT INTO custom_events ({columns})
        VALUES ({placeholders})
        """, values)

        await self.db.commit()

        return cursor.lastrowid

    async def get_custom_events(self, guild_id: int):

        self._require_db()

        cursor = await self.db.execute("""
        SELECT * FROM custom_events
        WHERE guild_id = ?
        ORDER BY start_time ASC
        """, (guild_id,))

        rows = await cursor.fetchall()

        return [dict(r) for r in rows]

    # =====================================================
    # TELEGRAM LINK TOKENS
    # =====================================================

    async def create_telegram_link(
        self,
        token,
        discord_id,
        guild_id,
        expiry
    ):

        self._require_db()

        await self.db.execute("""
        INSERT INTO telegram_links
        (token, discord_id, guild_id, expiry)
        VALUES (?, ?, ?, ?)
        """, (token, discord_id, guild_id, expiry))

        await self.db.commit()

    async def get_telegram_link(self, token):

        self._require_db()

        cursor = await self.db.execute("""
        SELECT * FROM telegram_links
        WHERE token = ?
        """, (token,))

        row = await cursor.fetchone()

        if not row:
            return None

        return dict(row)

    async def delete_telegram_link(self, token):

        self._require_db()

        await self.db.execute("""
        DELETE FROM telegram_links
        WHERE token = ?
        """, (token,))

        await self.db.commit()

    # =====================================================
    # CLEAN CLOSE
    # =====================================================

    async def close(self):

        if self.db:
            await self.db.close()
            self.db = None


# =====================================================
# GLOBAL DATABASE INSTANCE
# =====================================================

db = Database()
