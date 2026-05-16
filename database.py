"""
=========================================================
Evony Shield Watch
Database Layer (CLEAN + CONSISTENT + SAFE UPSERTS)
=========================================================
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

        self.db = await aiosqlite.connect(self.db_path)

        await self.db.execute("PRAGMA journal_mode=WAL;")

        # =================================================
        # MEMBERS TABLE
        # =================================================
        await self.db.execute("""
        CREATE TABLE IF NOT EXISTS members (
            user_id INTEGER PRIMARY KEY,
            guild_id INTEGER,
            role TEXT DEFAULT 'member',
            opt_in INTEGER DEFAULT 1,
            timezone TEXT DEFAULT 'UTC',
            telegram_id TEXT,
            telegram_username TEXT
        )
        """)

        # =================================================
        # GUILD CONFIG
        # =================================================
        await self.db.execute("""
        CREATE TABLE IF NOT EXISTS guild_config (
            guild_id INTEGER PRIMARY KEY,
            bubble_channel_id INTEGER,
            battlefield_channel_id INTEGER,
            setup_complete INTEGER DEFAULT 0,
            event_coordinator_role_id INTEGER
        )
        """)

        # =================================================
        # EVENT SCHEDULE (SVS / KE STATE)
        # =================================================
        await self.db.execute("""
        CREATE TABLE IF NOT EXISTS event_schedule (
            guild_id INTEGER PRIMARY KEY,
            current_event TEXT DEFAULT 'svs',
            next_event_date TEXT
        )
        """)

        # =================================================
        # CUSTOM EVENTS
        # =================================================
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

        # =================================================
        # CHECKINS
        # =================================================
        await self.db.execute("""
        CREATE TABLE IF NOT EXISTS event_checkins (
            event_id INTEGER,
            user_id INTEGER,
            status TEXT
        )
        """)

        # =================================================
        # TELEGRAM LINK TOKENS
        # =================================================
        await self.db.execute("""
        CREATE TABLE IF NOT EXISTS telegram_tokens (
            user_id INTEGER,
            guild_id INTEGER,
            token TEXT,
            expiry TEXT
        )
        """)

        await self.db.commit()

    # =====================================================
    # MEMBER UPSERT (FIXED CONSISTENCY LAYER)
    # =====================================================

    async def set_member_contact(
        self,
        user_id: int,
        guild_id: int = None,
        opt_in: int = None,
        timezone: str = None,
        telegram_id: str = None,
        telegram_username: str = None,
        role: str = None
    ):

        # build dynamic update
        fields = []
        values = []

        if guild_id is not None:
            fields.append("guild_id=?")
            values.append(guild_id)

        if opt_in is not None:
            fields.append("opt_in=?")
            values.append(opt_in)

        if timezone is not None:
            fields.append("timezone=?")
            values.append(timezone)

        if telegram_id is not None:
            fields.append("telegram_id=?")
            values.append(telegram_id)

        if telegram_username is not None:
            fields.append("telegram_username=?")
            values.append(telegram_username)

        if role is not None:
            fields.append("role=?")
            values.append(role)

        values.append(user_id)

        await self.db.execute(f"""
        INSERT INTO members (user_id)
        VALUES (?)
        ON CONFLICT(user_id)
        DO UPDATE SET {", ".join(fields)}
        """, (user_id, *values[:-1]))

        await self.db.commit()

    # =====================================================
    # GET MEMBER
    # =====================================================

    async def get_member_contact(self, user_id: int):

        cursor = await self.db.execute("""
        SELECT * FROM members WHERE user_id = ?
        """, (user_id,))

        row = await cursor.fetchone()

        if not row:
            return None

        return {
            "user_id": row[0],
            "guild_id": row[1],
            "role": row[2],
            "opt_in": row[3],
            "timezone": row[4],
            "telegram_id": row[5],
            "telegram_username": row[6]
        }

    # =====================================================
    # DELETE MEMBER
    # =====================================================

    async def delete_member_data(self, user_id: int, guild_id: int):

        await self.db.execute("""
        DELETE FROM members
        WHERE user_id = ? AND guild_id = ?
        """, (user_id, guild_id))

        await self.db.commit()

    # =====================================================
    # GUILD CONFIG
    # =====================================================

    async def set_server_config(self, guild_id: int, **kwargs):

        fields = []
        values = []

        for k, v in kwargs.items():
            fields.append(f"{k}=?")
            values.append(v)

        values.append(guild_id)

        await self.db.execute(f"""
        INSERT INTO guild_config (guild_id)
        VALUES (?)
        ON CONFLICT(guild_id)
        DO UPDATE SET {", ".join(fields)}
        """, (guild_id, *values[:-1]))

        await self.db.commit()

    async def get_server_config(self, guild_id: int):

        cursor = await self.db.execute("""
        SELECT * FROM guild_config WHERE guild_id = ?
        """, (guild_id,))

        row = await cursor.fetchone()

        if not row:
            return None

        return {
            "guild_id": row[0],
            "bubble_channel_id": row[1],
            "battlefield_channel_id": row[2],
            "setup_complete": row[3],
            "event_coordinator_role_id": row[4]
        }

    # =====================================================
    # EVENT SCHEDULE (SVS / KE)
    # =====================================================

    async def set_event_schedule(self, guild_id: int, **kwargs):

        fields = []
        values = []

        for k, v in kwargs.items():
            fields.append(f"{k}=?")
            values.append(v)

        values.append(guild_id)

        await self.db.execute(f"""
        INSERT INTO event_schedule (guild_id)
        VALUES (?)
        ON CONFLICT(guild_id)
        DO UPDATE SET {", ".join(fields)}
        """, (guild_id, *values[:-1]))

        await self.db.commit()

    async def get_event_schedule(self, guild_id: int):

        cursor = await self.db.execute("""
        SELECT * FROM event_schedule WHERE guild_id = ?
        """, (guild_id,))

        row = await cursor.fetchone()

        if not row:
            return None

        return {
            "guild_id": row[0],
            "current_event": row[1],
            "next_event_date": row[2]
        }

    # =====================================================
    # CUSTOM EVENTS
    # =====================================================

    async def create_custom_event(self, **kwargs):

        cursor = await self.db.execute("""
        INSERT INTO custom_events (
            guild_id, name, event_type,
            start_time, end_time,
            coordinator_id, checkin_cutoff,
            channel_id, message_id
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            kwargs["guild_id"],
            kwargs["name"],
            kwargs["event_type"],
            str(kwargs["start_time"]),
            str(kwargs["end_time"]),
            kwargs["coordinator_id"],
            str(kwargs["checkin_cutoff"]),
            kwargs["channel_id"],
            kwargs.get("message_id")
        ))

        await self.db.commit()

        return cursor.lastrowid

    async def update_custom_event(self, event_id: int, **kwargs):

        fields = []
        values = []

        for k, v in kwargs.items():
            fields.append(f"{k}=?")
            values.append(v)

        values.append(event_id)

        await self.db.execute(f"""
        UPDATE custom_events
        SET {", ".join(fields)}
        WHERE event_id = ?
        """, values)

        await self.db.commit()

    async def get_custom_event(self, event_id: int):

        cursor = await self.db.execute("""
        SELECT * FROM custom_events WHERE event_id = ?
        """, (event_id,))

        return await cursor.fetchone()

    async def get_active_custom_events(self, guild_id: int):

        cursor = await self.db.execute("""
        SELECT * FROM custom_events
        WHERE guild_id = ?
        """, (guild_id,))

        return await cursor.fetchall()

    async def delete_custom_event(self, event_id: int):

        await self.db.execute("""
        DELETE FROM custom_events WHERE event_id = ?
        """, (event_id,))

        await self.db.commit()

    # =====================================================
    # TELEGRAM TOKENS
    # =====================================================

    async def create_telegram_link_token(self, user_id, guild_id, token, expiry):

        await self.db.execute("""
        INSERT INTO telegram_tokens (user_id, guild_id, token, expiry)
        VALUES (?, ?, ?, ?)
        """, (user_id, guild_id, token, str(expiry)))

        await self.db.commit()

    async def link_telegram_user(self, token, telegram_id, username):

        cursor = await self.db.execute("""
        SELECT user_id FROM telegram_tokens WHERE token = ?
        """, (token,))

        row = await cursor.fetchone()

        if not row:
            return False

        user_id = row[0]

        await self.db.execute("""
        UPDATE members
        SET telegram_id = ?, telegram_username = ?
        WHERE user_id = ?
        """, (telegram_id, username, user_id))

        await self.db.execute("""
        DELETE FROM telegram_tokens WHERE token = ?
        """, (token,))

        await self.db.commit()

        return True


# =========================================================
# GLOBAL INSTANCE
# =========================================================

db = Database()
